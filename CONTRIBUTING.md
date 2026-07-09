# Contributing

Thanks for considering a contribution to PDFIndex.

## Ground rules

- Be kind. We follow the [Code of Conduct](CODE_OF_CONDUCT.md).
- Open an issue before large design changes.
- Keep diffs surgical; match existing style (Ruff owns format/lint).
- Do not commit secrets, `.env` files, or private documents.
- Bug fixes should include a regression test when practical.

## Development setup

Requirements: Python 3.10+, [uv](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/OctavianTocan/pdf-indexing-pages-for-agents.git
cd pdf-indexing-pages-for-agents
uv sync
cp .env.example .env   # fill in tokens locally; never commit .env
```

Optional: `uv run pre-commit install`

## Checks (same as CI)

```bash
uv run ruff format --check pdfindex tests
uv run ruff check pdfindex tests
uv run ty check pdfindex tests
uv run pytest -q
```

Or via the justfile: `just check`.

## Pull requests

1. Branch from `main`.
2. Make focused commits (conventional commits preferred: `feat:`, `fix:`, `docs:`).
3. Ensure CI is green.
4. Fill in the PR template: what/why, and which commands you ran.

## Security

Report vulnerabilities privately — see [SECURITY.md](SECURITY.md). Do not open
public issues for security reports.

## Attribution

This project is inspired by [PageIndex](https://github.com/VectifyAI/PageIndex)
(MIT, Vectify AI). See [NOTICE](NOTICE) and the README Acknowledgments. We are
not affiliated with Vectify AI.
