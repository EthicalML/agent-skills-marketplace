# Contributing

Contributions are accepted through pull requests. The `master` branch is PR-only; do not push changes directly to it.

Before opening a pull request, run:

```bash
scripts/validate.sh
```

Every skill and manifest must pass this validation locally.

## Skill authoring

- Use the `writing-skills` skill when creating or revising a SKILL.md.
- Keep frontmatter limited to supported fields and include non-empty `name` and `description` values.
- Use kebab-case skill names and make each name match its directory.
- Quote a description when it contains a colon followed by a space.
- Keep procedures concise, executable, and portable across supported agent runtimes.
- Do not hard-wrap Markdown prose.

## Breaking changes

A skill rename or removal must carry the `breaking-change` label. Include a `Migration` section in the pull request body that tells existing users exactly what to change.
