---
name: writing-agents-md
description: Cut a repository's agent instruction files down to what every session actually needs. Use when asked to write, revise, simplify, shorten or restructure AGENTS.md, CLAUDE.md, .github/copilot-instructions.md or path-scoped instruction files, or when a guide has grown into documentation rather than instructions.
---

# Writing agent instructions

This skill is about content. `standardize-agent-instructions` is about layout: which files exist and how each harness finds them. Run that one when the files are in the wrong places, this one when what is in them is not worth loading.

The entry point is loaded on every request of every session. Every sentence is paid for on every task, including the tasks that never touch its subject. That budget is the whole reason this skill exists.

## 0. Keep it simple

Radical simplicity. Simple does not mean incomplete: it means the rule is stated once, in the fewest words that still make it followable, and nothing else is there.

A guide is instructions, not documentation. If a sentence does not change what an agent does, cut it. That includes rationale, history, migration narratives, reassurance, and explanations of why a rule is good.

## 1. Measure before you restructure

Never restructure from an impression of size. Get the section census first:

```bash
python3 - .github/copilot-instructions.md <<'PY'
import pathlib, re, sys
text = pathlib.Path(sys.argv[1]).read_text()
parts = re.split(r'^(#{1,2} .+)$', text, flags=re.M)
print(f"{len(text):>7}  TOTAL")
for i in range(1, len(parts), 2):
    body = parts[i + 1]
    padding = sum(len(l) - len(re.sub(r' {2,}\|', ' |', l)) for l in body.split('\n') if l.startswith('|'))
    note = f"   ({padding} of it table padding)" if padding else ""
    print(f"{len(body):>7}  {parts[i]}{note}")
PY
```

Read the census before deciding anything. A section that dominates the file is usually one of three things, and each has a different fix:

- **Padding.** Formatters pad every markdown table cell to the width of the widest one, so a single long cell inflates every row. Fix it with a formatter-ignore comment above the table and single-spaced cells. This costs no content and is often the largest single win.
- **A different reader.** Split it out (step 4).
- **Genuine bloat.** Cut it (step 3).

## 2. Confirm the layout before editing

Instruction files are usually symlinked so several harnesses share one source of truth. Editing the symlink instead of the real file is a silent mistake.

```bash
ls -la CLAUDE.md AGENTS.md GEMINI.md .github/copilot-instructions.md .github/instructions/ .claude/rules/ 2>/dev/null
```

If the layout is inconsistent or there is no single source of truth, run `standardize-agent-instructions` first, then return here. Otherwise edit only the real file.

## 3. Triage every section

Take each section from the census and assign exactly one outcome:

| Outcome | When |
| --- | --- |
| **Keep** | It changes what an agent does on most tasks: the change workflow, hard constraints, placement rules, naming. |
| **Cut** | A tool already enforces it (formatter, linter, type checker, schema), or it restates another section, or it is reference material an agent can read from the source when needed. |
| **Compress** | The rule is real but wrapped in explanation. Keep the rule, drop the explanation. Usually one bullet. |
| **Move to a companion document** | Real reference with a clear read-condition: a catalogue, a mapping table, a menu of what exists. |
| **Move to a path-scoped file** | It governs one directory and nothing else. |
| **Gate it** | The section asserts facts about the source that rot silently. See step 6. |

Two rules that decide most hard cases:

- Split by reader, not by size. A section earns its own document when a different question sends someone to it, not when it is long. Two tables serving two different jobs are two documents; one long table serving one job stays.
- A path-scoped file is only worth it when its glob is genuinely narrow. If the rule touches most of `src/`, the glob will be `src/**` and the move buys nothing. Know your harnesses too: some auto-apply path-scoped files, others only read them on demand, so anything an agent must not violate by accident stays in the entry point.

## 4. Rewrite what stays

- Bullets, not paragraphs. Imperative. One rule per bullet.
- State each rule once, in the section that owns it.
- No history, no rationale, no "this used to be". If a gotcha needs its cause explained to be followable, keep the cause to one clause.
- Name the file, command or symbol precisely. An agent acts on names.
- Keep the repository's own editorial rules (dash style, wrapping, tone).

## 5. Give every companion document a read-condition

List them with the condition that sends a reader there, not with a summary of contents:

```markdown
- `STYLES.md` - Before adding or moving CSS.
- `TRANSITIONS.md` - Before changing motion, and when a transition misbehaves.
```

A document nobody knows when to open is a document nobody opens.

## 6. Prefer a gate over a paragraph

Optional, and worth it when a document asserts facts derivable from source: which components own a thing, which files exist, which routes are covered.

Write a validator that derives those facts and compares, wire it into the repository's existing check command, and delete the prose the check now guarantees. Check both directions: undocumented things in the source, and documented things no longer in the source. Where the repository already has a similar validator, copy its shape rather than inventing one.

Facts that cannot be derived (prose, intent) can still be covered by a content hash the author re-blesses deliberately, which proves someone looked without pretending to prove more.

## 7. Verify

- Re-run the census. Entry point under ~10KB is a good target; above that, be able to say why.
- Every path, command and symbol the file cites must exist: grep them. Names carried forward from an older revision are a common and invisible defect.
- Run the repository's formatter and linter over every file touched.
- Read the diff for meaning lost, not just bytes removed. A cut rule that was load-bearing is the only real failure mode here.
- Then the honest test, per `writing-skills`: give a blind subagent a typical task in the repository and watch whether it finds the rule it needs. If it does not, the rule was cut too far or moved somewhere it cannot be found.
