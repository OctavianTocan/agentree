# Security Policy

## Supported versions

Agentree is **alpha** (`0.x`). Security fixes are applied on a best-effort basis
to the latest commit on the default branch. There are no long-term support
branches yet.

| Version | Supported |
| --- | --- |
| `0.1.x` | Yes (best effort) |
| older | No |

## Reporting a vulnerability

Please **do not** open a public issue for security reports.

Prefer one of:

1. [GitHub private vulnerability reporting](https://github.com/OctavianTocan/agentree/security/advisories/new)
   (if enabled on this repository)
2. Email: [contact@octaviantocan.com](mailto:contact@octaviantocan.com) with subject
   `Agentree security`

Include:

- A short description of the issue
- Steps to reproduce or a proof of concept
- Affected commit / version if known
- Impact assessment (what an attacker could do)

You should receive an acknowledgment within a few days. We will coordinate a
fix and disclosure timeline with you. There is no bug bounty program at this
time.

## Scope notes

- Do not include real API tokens, OAuth credentials, or private PDFs in reports
  or public issues.
- Supply-chain reports against dependencies are welcome; prefer upstream
  advisories when the fix belongs there.
