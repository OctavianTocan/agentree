# Contributing

Thanks for considering a contribution to Agentree.

## Ground rules

- Be kind. We follow the [Code of Conduct](CODE_OF_CONDUCT.md).
- Open an issue before large design changes.
- Keep diffs surgical; match existing style (Ruff owns format/lint).
- Do not commit secrets, `.env` files, or private documents.
- Bug fixes should include a regression test when practical.

## Development setup

Requirements: Python 3.10+, [uv](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/OctavianTocan/agentree.git
cd agentree
uv sync
cp .env.example .env   # fill in tokens locally; never commit .env
```

Optional: `uv run pre-commit install`

## Checks (same as CI)

```bash
uv run ruff format --check agentree tests
uv run ruff check agentree tests
uv run ty check agentree tests
uv run pytest -q
```

Or via the justfile: `just check`.

## Pull requests

1. Branch from `main`.
2. Use [Conventional Commits](https://www.conventionalcommits.org/) — they drive
   the changelog and releases:
   - `feat:` → minor bump (or patch while pre-1.0, per release-please config)
   - `fix:` → patch bump
   - `feat!:` / `fix!:` / `BREAKING CHANGE:` → major bump
   - `docs:`, `chore:`, `ci:`, `test:` → usually no release by themselves
3. Ensure CI is green.
4. Fill in the PR template: what/why, and which commands you ran.

## Releases

[Release Please](https://github.com/googleapis/release-please) runs on every
push to `main`. It opens (or updates) a release PR that bumps
`pyproject.toml`, refreshes `CHANGELOG.md`, and updates the version marker in
`README.md`. Merging that PR tags `vX.Y.Z` and creates the GitHub Release.

Do **not** hand-edit `CHANGELOG.md` for routine work — put the story in the
commit message / PR title instead.

If branch rules block `github-actions[bot]`, add a fine-scoped PAT (or GitHub
App token) as the `RELEASE_PLEASE_TOKEN` repository secret.

## Security

Report vulnerabilities privately — see [SECURITY.md](SECURITY.md). Do not open
public issues for security reports.

## Attribution

This project is inspired by [PageIndex](https://github.com/VectifyAI/PageIndex)
(MIT, Vectify AI). See [NOTICE](NOTICE) and the README Acknowledgments. We are
not affiliated with Vectify AI.
