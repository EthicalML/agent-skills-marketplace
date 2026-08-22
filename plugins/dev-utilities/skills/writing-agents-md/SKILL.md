---
name: writing-agents-md
description: Cut a repository's agent instruction files down to what every session actually needs. Use when asked to write, revise, simplify, shorten or restructure AGENTS.md, CLAUDE.md, .github/copilot-instructions.md or path-scoped instruction files, or when a guide has grown into documentation rather than instructions.
---

# Writing agent instructions

`standardize-agent-instructions` handles layout (which files exist, where). This skill handles content.

The entry point is loaded on every request, so every sentence costs every task. One test decides everything: if a sentence does not change what an agent does, cut it. That includes rationale, history, and reassurance.

## 1. Measure

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

The largest section is usually one of:

- **Table padding.** Formatters pad every cell to the widest one; a single long cell inflates every row. Fix: formatter-ignore comment above the table, single-spaced cells.
- **Reference for a different reader.** Split it out (step 3).
- **Bloat.** Cut it (step 3).

## 2. Confirm the layout

```bash
ls -la CLAUDE.md AGENTS.md GEMINI.md .github/copilot-instructions.md .github/instructions/ .claude/rules/ 2>/dev/null
```

Edit the real file, never a symlink. If there is no single source of truth, run `standardize-agent-instructions` first.

Write every in-repo path as `<root>/path`, not as a relative link: a symlinked file is read from several directory depths, so no relative path is correct from all of them.

## 3. Triage every section

<!-- prettier-ignore -->
| Outcome | When |
| --- | --- |
| **Keep** | Changes what an agent does on most tasks: workflow, hard constraints, placement, naming. |
| **Cut** | A tool already enforces it, it restates another section, or an agent can read it from source. |
| **Compress** | Real rule wrapped in explanation. Keep the rule, drop the explanation. |
| **Companion document** | Reference with a clear read-condition: a catalogue, a mapping, a menu. |
| **Path-scoped file** | Governs one directory and nothing else. |
| **Gate** | Asserts facts about the source that rot silently (step 6). |

Hard cases:

- Split by reader, not by size. A document earns its existence when a different question sends someone to it.
- A path-scoped file needs a genuinely narrow glob; `src/**` buys nothing. Rules an agent must not violate by accident stay in the entry point: not every harness auto-applies path-scoped files.

## 4. Rewrite what stays

- Bullets, imperative, one rule each.
- Each rule stated once, in the section that owns it.
- No history or rationale. If a gotcha needs its cause, one clause.
- Name files, commands and symbols precisely.
- Keep the repository's own editorial rules.

## 5. Companion documents get read-conditions

List the condition that sends a reader there, not a summary:

```markdown
- `STYLES.md` - Before adding or moving CSS.
- `TRANSITIONS.md` - Before changing motion, and when a transition misbehaves.
```

## 6. Gate derivable facts

When a document asserts facts derivable from source (which components exist, which routes are covered): write a validator that derives and compares, wire it into the existing check command, delete the prose it now guarantees. Check both directions: undocumented in source, documented but gone. Copy the shape of an existing validator if the repository has one. Underivable prose can get a content hash the author re-blesses deliberately.

## 7. Verify

- Re-run the census. Entry point under ~10KB, or be able to say why not.
- Grep that every cited path, command and symbol exists.
- Run the repository's formatter and linter.
- Read the diff for lost meaning, not just removed bytes.
- Give a blind subagent a typical task and watch whether it finds the rule it needs.
