---
name: hol-guard
description: Use when installing HOL Guard, protecting a supported local AI coding harness, checking protection status, or reviewing Guard approvals and receipts.
license: Apache-2.0
---

# HOL Guard

Use HOL Guard as the local pre-execution security boundary for supported AI coding harnesses. Let Guard own harness configuration changes and never bypass an approval.

## Step 1 — Check the local Guard state

Run:

```bash
hol-guard status
hol-guard detect --json
```

If `hol-guard` is unavailable, install the isolated CLI and repeat the checks:

```bash
pipx install hol-guard
hol-guard status
hol-guard detect --json
```

If `pipx` is unavailable, tell the user that an isolated CLI install is recommended instead of silently changing the active Python environment.

## Step 2 — Protect a detected harness

Choose the exact supported harness identifier from `hol-guard detect --json`. Do not invent or maintain a separate harness-name list. If the requested harness is not detected or supported, stop and report that rather than editing its configuration manually.

Run:

```bash
hol-guard bootstrap
hol-guard install <harness>
hol-guard run <harness> --dry-run
hol-guard run <harness>
hol-guard doctor <harness> --json
```

Do not run the non-dry-run protection step if the dry run reports an unexpected mutation or error.

## Step 3 — Handle Guard decisions without bypassing them

When Guard queues or blocks work, inspect the request and evidence:

```bash
hol-guard approvals
hol-guard approvals open <request-id>
hol-guard receipts
hol-guard diff <harness>
```

`hol-guard approvals open` requires the pending approval request ID. Use the ID shown by `hol-guard approvals`; do not invent one.

Never auto-approve a queued request. If the user explicitly decides after reviewing the risk and scope, use the Guard-owned approval commands rather than changing harness policy files directly.

## Step 4 — Verify protection

Run:

```bash
hol-guard status
hol-guard doctor <harness> --json
hol-guard receipts
```

Report the commands run, the detected harness, whether Guard proves the harness is protected, any remaining approval or error, and the exact next command if user action is still required. Do not claim protection without command output proving it.
