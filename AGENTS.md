# AGENTS.md — Codex adapter for agentic-stack

Codex reads `AGENTS.md` before doing any work. This file points it at
the portable brain in `.agent/`.

> **Python invocation**: examples below use `python3`. On stock Windows
> only `python` is on PATH; use whichever resolves on your system.

## Startup (read in order)
1. `.agent/AGENTS.md` — the map
2. `.agent/memory/personal/PREFERENCES.md` — user conventions
3. `.agent/memory/semantic/LESSONS.md` — distilled lessons
4. `.agent/protocols/permissions.md` — hard rules

## Skills
Codex scans `.agents/skills/` for repository-scoped skills (per
[OpenAI Codex docs](https://developers.openai.com/codex/skills)). The
install script symlinks or syncs `.agents/skills` from `.agent/skills`
so the portable brain remains the one source of truth. Load a full
`SKILL.md` only when its triggers match the task (progressive
disclosure). Edit skills in `.agent/skills/` — `.agents/skills/` is a
mirror and re-running the installer will sync it back.

## Recall before non-trivial tasks
For deploy / ship / migration / schema / timestamp / date / failing test /
debug / refactor, FIRST run:

```bash
python3 .agent/tools/recall.py "<description>"
```

Surface results in a `Consulted lessons before acting:` block and follow
them.

## Memory discipline
- Update `.agent/memory/working/WORKSPACE.md` as you work.
- After significant actions, run
  `python3 .agent/tools/memory_reflect.py <skill> <action> <outcome>`.
- Never delete memory entries; archive only.
- Quick state: `python3 .agent/tools/show.py`.
- Teach a rule in one shot:
  `python3 .agent/tools/learn.py "<rule>" --rationale "<why>"`.

## Hard rules
- No force push to `main`, `production`, `staging`.
- No modification of `.agent/protocols/permissions.md`.


## Working principles

*These bias toward caution over speed. Use judgment for trivial tasks.*

### Investigate first

- **Read before writing:** Before adding code in a file, read its exports, the immediate caller, and obvious shared utilities. Match existing patterns; never guess. If you don't understand why existing code is structured the way it is, ask before adding to it.
- **Think before coding:** State assumptions explicitly; ask when uncertain. If multiple interpretations exist, present them (don't pick silently). If a simpler approach exists, say so. Push back when warranted.
- **Set verifiable goals:** Transform tasks into pass/fail criteria before starting. "Add validation" becomes "write tests for invalid inputs, then make them pass". Weak criteria require constant clarification; strong criteria let you loop independently.
- **Surface conflicts, don't average them:** If two existing patterns contradict, don't blend them. Pick one (more recent / more tested), explain why, flag the other for cleanup. "Average" code that satisfies both is the worst code.
- **Activate skills:** Scan all skills (`domain-*`, `practice-*`, `workflow-*`, `tool-*`, `gen-*`, `meta-*`) and activate every relevant one. Trigger on the *task*: `practice-code-quality` for any TS edit, `practice-debug` for bugs, `workflow-plan` before creative work. Missing a skill is the #1 source of convention violations.

### Write minimum

- **Simplicity first:** Minimum code that solves the problem. No features beyond what was asked, no abstractions for single-use code, no "flexibility" that wasn't requested, no error handling for impossible scenarios. If 200 lines could be 50, rewrite it.
- **Surgical changes:** Every changed line traces directly to the request. Don't refactor or "improve" adjacent code; match existing style even if you'd do it differently. Remove imports/variables your changes orphaned; don't touch pre-existing dead code (mention it).
- **No obsolete paths by default:** During active product iteration, remove old behavior and state instead of preserving transitional fallbacks unless explicitly requested.
- **Fix root causes**, not symptoms.
- **Composability:** Build simple, extensible primitives and compose them. Avoid bespoke monoliths.

### Verify honestly

- **Tests verify intent, not behavior:** Every test must encode WHY the behavior matters, not just WHAT it does. `expect(getUserName()).toBe('John')` is worthless if the function takes a hardcoded ID. If a test wouldn't fail when business logic changes, the function is wrong.
- **Bug fixes require regression tests:** Every bug fix must add or update tests that fail for the bug and pass for the fix. If an automated regression test is impossible, explain why and document the manual verification used.
- **Fail loud:** Surface uncertainty rather than hiding it. "Migration completed" is wrong if records were silently skipped. "Tests pass" is wrong if you skipped any. "Feature works" is wrong if you didn't verify the edge case asked about.
- **No browser review:** Don't spin up a dev server or browser agent to verify UI. Typecheck + lint is sufficient; user reviews UI. Run `bun run ci` (repo-policy + lint + typecheck + tests + arch:sentrux + effect:check-skill-drift + knip) before claiming work complete.


## Conventions

### Type safety

- No type casting (`as`, `as any`, `as unknown as`, `<Type>expr`, `expr!`). Fix the underlying type.
- No TypeScript enums; use unions or const objects.
- Derive types from source: `typeof table.$inferSelect`, `z.infer<...>`, `Schema.Type<...>`.

### Imports

- Scoped path aliases for cross-package (`@apps/*`, `@platform/*`, `@comcom/*`, `@ui/*`, `@clients/*`, `@tooling/*`, `@infra/*`, `@ci/*`, `@agent-dev/*`); `@/*` for local.
- Import directly from files, never from `index.ts` barrels: `@ui/design-system/components/ui/button`, not `@ui/design-system`.
- Approved package-export exception: `@ui/design-system/components/icons` is the design-system icon registry; direct `lucide-react` imports belong there.
- No file extensions in imports (`.ts`, `.tsx`, `.js`).

### Tests

- Tests live in package-level `test/` directories, not next to source.

### Comments

- No section-divider comments (e.g. `// ----`).
- Inline comments explain non-obvious WHY, never restate WHAT. If reading the code already makes its behavior obvious, the comment is noise: delete it. No references to current task/PR/ticket; that belongs in the commit message.
- JSDoc on every function (exports AND non-exported helpers) describes the interface, never the implementation. Non-exported helpers get a single-line summary; exported and public surfaces (service/repo methods, exported functions) also carry proper `@param`/`@returns` (plus `@template`/`@throws` as relevant), each stating the caller's contract rather than the type. See `practice-code-quality`.

### Exports

- Named exports for reusable components. Default exports only for Next.js pages/layouts.
- Reuse types from sibling modules; never redefine a type that already exists in a dependency.

### Subagents

- **Bucket then dispatch:** Decompose non-trivial work into independent buckets, one subagent per bucket. Many small focused buckets beat one monolith: parallelizes execution, keeps each context tight, isolates failures. Bucketing is the default for large tasks, not an optimization.
- **Foreground vs background:** Foreground when you need results inline; background (async, notified on completion) for independent parallel work. Both inherit full Read/Write/Edit/Bash; restrict via `subagent_type` (`Explore`/`Plan`) for read-only. No concurrent cap.
- **Brief them fully:** Subagents start with fresh context. Every prompt needs a full overview, explicit step-by-step instructions, and the skills they must activate. Partial context is never enough.
- **Models:** `claude-opus-4-7` for any code-writing subagent (no exceptions). Research subagents may use `claude-sonnet-4-6` or `claude-haiku-4-5`; they retain full code read access and should use it freely rather than answering from training.

#### Teams (research, design, critique)

For hard research questions, design tradeoffs, or critique passes, spawn a *team* of background agents in parallel, each with a distinct expert lens (e.g. security, performance, UX, a relevant `domain-*` skill). Frame each lens role neutrally ("evaluate from a security perspective"), never the conclusion ("explain why X is right"). Synthesize in the parent: surface conflicts honestly, decide.

### Effect-TS

Any edit to a file that imports from `effect` or `@effect/*` is an Effect change: activate `domain-effect` and `domain-effect-source` (mandatory even for "small" changes, since that is where API drift hides). Those skills own the rules: reference docs, vendor-source citations, the Effect Expert subagent, and `effect:check-skill-drift`.

### Pull requests

Write the title and description for a tired reviewer who should know what the PR does in five seconds. See `practice-pr`; `domain-git` owns the required body sections.

- Title: keep the `type(scope): summary` prefix, then a plain imperative phrase. No PR/issue numbers, slice counts like `(3/8)`, diff stats, or emoji.
- Description: lead with one sentence saying what changed and why. Bullets over paragraphs, one change each.
- Validation lists only commands and checks you actually ran.
- Cut filler openers ("This PR…"), invented numbers (file/diff counts — GitHub shows them), and AI tells ("comprehensive", "robust", "seamless").

### Verification

- Run `bun run ci` (repo-policy + lint + typecheck + tests + arch:sentrux + effect:check-skill-drift + knip) before committing or pushing; never claim work complete without clean output.
- Scoped subsets: `bun run check` (lint), `bun run typecheck`, `bun run test`.
