#!/usr/bin/env python3
"""Read local Joplin notes with SQLite and write notes through the terminal CLI."""

import argparse
from collections import Counter
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import shlex
import sqlite3
import subprocess
import sys
from uuid import uuid4


def arguments():
    parser = argparse.ArgumentParser(description=__doc__)
    target = parser.add_mutually_exclusive_group()
    target.add_argument("--db", help="database file (default override: JOPLIN_DB)")
    target.add_argument("--profile", help="profile directory containing database.sqlite")
    parser.add_argument("--include-conflicts", action="store_true")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("notebooks")
    commands.add_parser("search").add_argument("words")
    grep = commands.add_parser("grep")
    grep.add_argument("regex")
    grep.add_argument("-i", "--ignore-case", action="store_true")
    commands.add_parser("show").add_argument("note")
    recent = commands.add_parser("recent")
    recent.add_argument("-n", type=int, default=10)
    recent.add_argument("--notebook")
    create = commands.add_parser("create")
    create.add_argument("--notebook", required=True)
    create.add_argument("--title", required=True)
    create.add_argument("--body-file", type=Path, required=True)
    update = commands.add_parser("update")
    update.add_argument("note_id")
    update.add_argument("--title")
    body = update.add_mutually_exclusive_group()
    body.add_argument("--body-file", type=Path)
    body.add_argument("--append-file", type=Path)
    update.add_argument("--untag", action="append", default=[])
    update.add_argument("--notebook")
    for command in (create, update):
        command.add_argument("--tag", action="append", default=[])
        command.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def database_path(args):
    if args.profile:
        return Path(args.profile).expanduser() / "database.sqlite"
    override = args.db or os.getenv("JOPLIN_DB")
    if override:
        return Path(override).expanduser()
    config = Path.home() / ".config"
    terminal = config / "joplin/database.sqlite"
    desktop = config / "joplin-desktop/database.sqlite"
    if args.command not in ("create", "update") and not terminal.exists() and desktop.exists():
        return desktop
    return terminal


def undeleted(db, table):
    fields = {row["name"] for row in db.execute(f"PRAGMA table_info({table})")}
    return f"{table}.deleted_time = 0" if "deleted_time" in fields else "1"


def notebook_paths(db):
    folders = {row["id"]: row for row in db.execute(
        "SELECT id, title, parent_id FROM folders WHERE " + undeleted(db, "folders")
    )}
    paths = {}
    for folder_id in folders:
        parts = []
        seen = set()
        current = folder_id
        while current in folders and current not in seen:
            seen.add(current)
            parts.append(folders[current]["title"])
            current = folders[current]["parent_id"]
        paths[folder_id] = "/".join(reversed(parts))
    return folders, paths


def notebook_id(value, folders, paths):
    if value in paths:
        return value
    matches = [key for key in paths if value in (paths[key], folders[key]["title"])]
    if len(matches) != 1:
        raise ValueError("Notebook missing or ambiguous. Use a full ID from notebooks.")
    return matches[0]


def date(milliseconds):
    return datetime.fromtimestamp(milliseconds / 1000, timezone.utc).isoformat(timespec="seconds")


def read_notes(db, args, folders, paths):
    visible = undeleted(db, "notes")
    if not args.include_conflicts:
        visible += " AND notes.is_conflict = 0"
    query = " FROM notes WHERE " + visible
    columns = "SELECT notes.id, notes.parent_id, notes.title, notes.updated_time"
    if args.command == "notebooks":
        counts = dict(db.execute("SELECT parent_id, count(*)" + query + " GROUP BY parent_id"))
        for key in sorted(paths, key=paths.get):
            print(paths[key], counts.get(key, 0), key, sep="\t")
    elif args.command == "grep":
        pattern = re.compile(args.regex, re.I if args.ignore_case else 0)
        for row in db.execute("SELECT id, title, body" + query):
            for number, line in enumerate((row["title"] + "\n" + row["body"]).splitlines(), 1):
                if pattern.search(line):
                    print(row["id"], row["title"], number, line, sep="\t")
    elif args.command == "show":
        rows = db.execute("SELECT *" + query + " AND id = ?", (args.note,)).fetchall()
        if not rows:
            rows = db.execute("SELECT *" + query + " AND title = ? LIMIT 2", (args.note,)).fetchall()
        if len(rows) != 1:
            raise ValueError("Note missing or ambiguous. Use a full ID from recent or grep.")
        note = rows[0]
        tags = db.execute("SELECT tags.title FROM tags JOIN note_tags ON tags.id = note_tags.tag_id "
                          "WHERE note_tags.note_id = ? ORDER BY tags.title", (note["id"],))
        print(note["title"])
        print("Notebook:", paths.get(note["parent_id"], ""))
        print("Tags:", ", ".join(row[0] for row in tags))
        print("Created:", date(note["created_time"]))
        print("Updated:", date(note["updated_time"]))
        print("\n" + note["body"])
    else:
        params = []
        if args.command == "search":
            # FTS4 offsets give four integers per hit, starting with the column index.
            def rank(offsets):
                hits = Counter(offsets.split()[::4])
                return 3 * hits["1"] + hits["2"]

            db.create_function("rank_hits", 1, rank)
            query = (" FROM notes_fts JOIN notes ON notes.id = notes_fts.id "
                     "WHERE notes_fts MATCH ? AND " + visible +
                     " ORDER BY rank_hits(offsets(notes_fts)) DESC, notes.updated_time DESC, notes.id")
            params.append(args.words)
        else:
            if args.n < 0:
                raise ValueError("-n must be non-negative.")
            if args.notebook:
                query += " AND parent_id = ?"
                params.append(notebook_id(args.notebook, folders, paths))
            query += " ORDER BY updated_time DESC, id LIMIT ?"
            params.append(args.n)
        for row in db.execute(columns + query, params):
            print(row["id"], paths.get(row["parent_id"], ""), row["title"], date(row["updated_time"]), sep="\t")


def warn_if_tui_open(path):
    # lsof scopes the process lookup to this database, including custom profiles.
    try:
        holders = subprocess.run(["lsof", "-t", "--", str(path.resolve())], capture_output=True, text=True)
        pids = [pid for pid in holders.stdout.split() if pid.isdigit() and pid != str(os.getpid())]
        if not pids:
            return
        processes = subprocess.run(["ps", "-ww", "-p", ",".join(pids), "-o", "command="],
                                   capture_output=True, text=True)
    except OSError:
        return
    tui = r"(?:(?:\S*/)?node\s+)?(?:\S*/)?joplin(?:/main\.js)?(?:\s+--profile\s+\S+)?"
    if any(re.fullmatch(tui, line.strip()) for line in processes.stdout.splitlines()):
        print("The TUI won't show the change until you switch notebooks. Don't write while a note is "
              "open in an external editor because CLI startup removes edit-* temp files.", file=sys.stderr)


def append_body(original, addition):
    if not original or not addition:
        return original + addition
    # Preserve both texts and add only the line breaks missing at the join.
    left = original[-4:].replace("\r\n", "\n")
    right = addition[:4].replace("\r\n", "\n")
    breaks = len(left) - len(left.rstrip("\n")) + len(right) - len(right.lstrip("\n"))
    return original + "\n" * max(0, 2 - breaks) + addition


def update_steps(db, args, folder_id):
    selector = args.note_id.lower()
    if not re.fullmatch("[0-9a-fA-F]{32}", args.note_id):
        raise ValueError("update requires a full 32-hex note ID.")
    visible = undeleted(db, "notes")
    if not args.include_conflicts:
        visible += " AND is_conflict = 0"
    note = db.execute("SELECT body, encryption_applied FROM notes WHERE id = ? AND " + visible,
                      (selector,)).fetchone()
    if not note or note["encryption_applied"]:
        raise ValueError("Note missing, excluded, or awaiting decryption.")

    # The CLI looks up titles before IDs. Its mv command also tries folders first.
    if db.execute("SELECT 1 FROM notes WHERE title = ? AND id != ?", (selector, selector)).fetchone():
        raise ValueError("Another note's title matches this ID and would make the CLI selector ambiguous.")
    if folder_id and db.execute("SELECT 1 FROM folders WHERE id = ? OR title = ?", (selector, selector)).fetchone():
        raise ValueError("A notebook matches the note ID and would intercept the CLI move.")

    steps = []
    if args.body_file or args.append_file:
        body = (args.body_file or args.append_file).read_bytes().decode("utf-8")
        if args.append_file:
            body = append_body(note["body"], body)
        steps.append(["set", "--", selector, "body", body])
    steps.extend(["tag", "--", "add", tag, selector] for tag in args.tag)
    steps.extend(["tag", "--", "remove", tag, selector] for tag in args.untag)
    if folder_id:
        steps.append(["mv", "--", selector, folder_id])
    if args.title is not None:
        steps.append(["set", "--", selector, "title", args.title])
    if not steps:
        raise ValueError("Supply a title, file, tag change, or destination notebook.")
    return selector, steps


def write_note(db, path, args, folders, paths):
    if path.name != "database.sqlite":
        raise ValueError("CLI writes require a profile containing database.sqlite.")
    config = path.parent / "profiles.json"
    if config.exists() and json.loads(config.read_text()).get("currentProfileId") != "default":
        raise ValueError("Pass the active profile's own directory with --profile.")
    if args.title is not None and not args.title.strip():
        raise ValueError("Titles must contain text.")
    if any(not tag.strip() for tag in args.tag + getattr(args, "untag", [])):
        raise ValueError("Tags must contain text.")
    folder_id = notebook_id(args.notebook, folders, paths) if args.notebook is not None else None
    if folder_id and db.execute("SELECT 1 FROM folders WHERE title = ? AND id != ?", (folder_id, folder_id)).fetchone():
        raise ValueError("Another notebook's title matches the destination ID.")
    if args.command == "update":
        selector, steps = update_steps(db, args, folder_id)
    else:
        # A unique literal selector avoids wildcard and duplicate-title updates.
        selector = "draft-" + uuid4().hex
        body = args.body_file.read_bytes().decode("utf-8")
        steps = [["use", "--", folder_id], ["mknote", "--", selector], ["set", "--", selector, "body", body]]
        steps.extend(["tag", "--", "add", tag, selector] for tag in args.tag)
        steps.append(["set", "--", selector, "title", args.title])
    if any("\0" in value for step in steps for value in step):
        raise ValueError("CLI arguments cannot contain NUL characters.")
    if not args.dry_run:
        warn_if_tui_open(path)
    profile = os.path.expanduser(args.profile) if args.profile else str(path.parent)
    note_id = selector
    for step in steps:
        command = ["joplin", "--profile", profile, *step]
        if args.dry_run:
            print(shlex.join(command))
            continue
        try:
            result = subprocess.run(command)
        except OSError as error:
            raise ValueError(f"Could not start Joplin {step[0]}: {error}. Check recent for {selector}.") from error
        if result.returncode:
            raise ValueError(f"Joplin {step[0]} failed. Check recent for {selector} before retrying.")
        if step[0] == "mknote":
            note = db.execute("SELECT id FROM notes WHERE parent_id = ? AND title = ?",
                              (folder_id, selector)).fetchone()
            if not note:
                raise ValueError(f"Draft missing from the target notebook. Locate {selector} before retrying.")
            note_id = note["id"]
    if not args.dry_run:
        print(note_id)


def main():
    args = arguments()
    path = database_path(args)
    with sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True) as db:
        db.row_factory = sqlite3.Row
        folders, paths = notebook_paths(db)
        if args.command in ("create", "update"):
            write_note(db, path, args, folders, paths)
        else:
            read_notes(db, args, folders, paths)


if __name__ == "__main__":
    try:
        main()
    except (OSError, sqlite3.Error, ValueError, re.error) as error:
        sys.exit(str(error))
