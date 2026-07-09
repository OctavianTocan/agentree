# AGENTS.md — Codex adapter for agentic-stack

Codex reads `AGENTS.md` before doing any work. This file points it at
the portable brain in `.agent/`. Claude Code loads the same content via
`CLAUDE.md` (`@AGENTS.md`).

> **Python invocation**: examples below use `python3`. On stock Windows
> only `python` is on PATH; use whichever resolves on your system.

## Startup (read in order)
1. `.agent/AGENTS.md` — the map
2. `.agent/memory/personal/PREFERENCES.md` — user conventions
3. `.agent/memory/working/REVIEW_QUEUE.md` — pending candidate lessons
4. `.agent/memory/semantic/LESSONS.md` — distilled lessons
5. `.agent/protocols/permissions.md` — hard rules

If `REVIEW_QUEUE.md` shows pending > 10 or oldest staged > 7 days, review
candidates before substantive work.

## Skills
Codex scans `.agents/skills/` for repository-scoped skills (per
[OpenAI Codex docs](https://developers.openai.com/codex/skills)). The
install script symlinks or syncs `.agents/skills` from `.agent/skills`
so the portable brain remains the one source of truth. Load a full
`SKILL.md` only when its triggers match the task (progressive
disclosure). Edit skills in `.agent/skills/` — `.agents/skills/` is a
mirror and re-running the installer will sync it back.

Read `.agent/skills/_index.md` first. Current registry includes
`git-proxy`, `debug-investigator`, `deploy-checklist`, `memory-manager`,
`skillforge`, `data-layer`, `data-flywheel`, `brain`, `design-md`, and
`tldraw`.

## Recall before non-trivial tasks
For deploy / ship / release / migration / schema / timestamp / timezone /
date / failing test / debug / investigate / refactor, FIRST run:

```bash
python3 .agent/tools/recall.py "<description>"
```

Surface results in a `Consulted lessons before acting:` block and follow
them. If a surfaced lesson would be violated by the intended action, stop
and explain why.

## Memory discipline
- Update `.agent/memory/working/WORKSPACE.md` as you work (goal + next
  step on start; clear on complete/abandon).
- After significant actions, run
  `python3 .agent/tools/memory_reflect.py <skill> <action> <outcome>`
  with a rich `--note` (these are what the dream cycle promotes).
- Never delete memory entries; archive only.
- Never hand-edit `.agent/memory/semantic/LESSONS.md` — use
  `graduate.py` / `reject.py` / `retract_lesson.py`.
- Quick state: `python3 .agent/tools/show.py`.
- Teach a rule in one shot:
  `python3 .agent/tools/learn.py "<rule>" --rationale "<why>"`.

### When to log manually
- Major feature or bug fix that took real investigation
- Rollback, incident, or unexpected failure
- Architectural decision (why A over B)
- Project-specific constraint you wish you had known earlier

### Importance guide
| Value | When |
|---|---|
| 9–10 | Production incident, data migration, rollback, security issue |
| 7–8 | Deploy, schema change, architectural decision, non-obvious constraint |
| 5–6 | Refactor, significant bug fix, API contract change |
| 3–4 | Routine edit, file creation, test run |

## Hard rules
- No force push to `main`, `production`, `staging`.
- No modification of `.agent/protocols/permissions.md` (humans only).
- No deleting episodic or semantic memory entries — archive only.
- Follow `.agent/protocols/permissions.md` for approval gates (deploy,
  migrations, dependency installs, CI changes, etc.).

## Working principles

*These bias toward caution over speed. Use judgment for trivial tasks.*

### Investigate first

- **Read before writing:** Before adding code in a file, read its exports,
  the immediate caller, and obvious shared utilities. Match existing
  patterns; never guess. If you don't understand why existing code is
  structured the way it is, ask before adding to it.
- **Think before coding:** State assumptions explicitly; ask when
  uncertain. If multiple interpretations exist, present them (don't pick
  silently). If a simpler approach exists, say so. Push back when
  warranted.
- **Set verifiable goals:** Transform tasks into pass/fail criteria before
  starting. Weak criteria require constant clarification; strong criteria
  let you loop independently.
- **Surface conflicts, don't average them:** If two existing patterns
  contradict, don't blend them. Pick one (more recent / more tested),
  explain why, flag the other for cleanup.
- **Activate skills:** Scan `.agent/skills/_index.md` and load every
  relevant `SKILL.md`. Trigger on the *task* (e.g. `git-proxy` for
  commits/PRs, `debug-investigator` for bugs, `deploy-checklist` before
  ship). Missing a skill is a common source of convention violations.

### Write minimum

- **Simplicity first:** Minimum code that solves the problem. No features
  beyond what was asked, no abstractions for single-use code, no
  "flexibility" that wasn't requested, no error handling for impossible
  scenarios.
- **Surgical changes:** Every changed line traces directly to the request.
  Don't refactor or "improve" adjacent code; match existing style even if
  you'd do it differently. Remove imports/variables your changes orphaned;
  don't touch pre-existing dead code (mention it).
- **No obsolete paths by default:** During active product iteration, remove
  old behavior and state instead of preserving transitional fallbacks
  unless explicitly requested.
- **Fix root causes**, not symptoms.
- **Composability:** Build simple, extensible primitives and compose them.
  Avoid bespoke monoliths.

### Verify honestly

- **Tests verify intent, not behavior:** Every test must encode WHY the
  behavior matters, not just WHAT it does. If a test wouldn't fail when
  business logic changes, the function or the test is wrong.
- **Bug fixes require regression tests:** Every bug fix must add or update
  tests that fail for the bug and pass for the fix. If an automated
  regression test is impossible, explain why and document the manual
  verification used.
- **Fail loud:** Surface uncertainty rather than hiding it. "Tests pass" is
  wrong if you skipped any. "Feature works" is wrong if you didn't verify
  the edge case asked about.

## Project conventions (pdfindex)

Python package for hierarchical PDF indexing (Claude/Codex structured
completions, not vector chunking). Package root: `pdfindex/`. Tests:
`tests/`. Tooling: `uv` + Ruff + `ty` + pytest.

### Python / typing
- Target Python 3.10+; prefer `from __future__ import annotations`.
- Prefer Pydantic models and explicit types over ad-hoc dicts at
  boundaries (schemas, settings, completion payloads).
- Avoid `# type: ignore` and broad `Any` unless unavoidable; fix the type.

### Style
- Ruff owns format + lint (`pyproject.toml`: line length 100, indent 2,
  single quotes). Match existing modules.
- Module docstrings on packages/modules; function docstrings describe the
  caller contract (Args/Returns), not the implementation. Inline comments
  explain non-obvious WHY only — no section-divider comments.
- Logging: Loguru only (`from loguru import logger`). Configure via
  `pdfindex.logging_config.configure_logging()`. Brace-format messages;
  use `bind()` for structured context. No stdlib `logging` in app code.

### Layout
- Application code under `pdfindex/`; tests under top-level `tests/` (not
  next to source).
- Named exports / clear module APIs; reuse existing types from sibling
  modules instead of redefining them.

### Subagents
Follow `.agent/protocols/delegation.md`. For non-trivial work: bucket into
independent sub-tasks, brief each subagent fully (fresh context), and
synthesize conflicts in the parent. Do not fan out without a clear return
format and budget.

### Pull requests
Write for a tired reviewer who should know what the PR does in five
seconds. Prefer conventional-commit titles (`type(scope): summary`) and
imperative phrasing. Description: one sentence of what/why, then bullets.
Validation lists only commands you actually ran. No filler, invented
diff stats, or AI tells. Use `git-proxy` for git safety.

## Verification

Before claiming work complete (and before commit/push when changes warrant
it), run the same checks as CI:

```bash
uv run ruff format --check pdfindex tests
uv run ruff check pdfindex tests
uv run ty check pdfindex tests
uv run pytest -q
```

Scoped subsets while iterating: `uv run ruff check …`, `uv run ty check …`,
`uv run pytest …`.
