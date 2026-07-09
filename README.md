# PDFIndex

[![CI](https://github.com/OctavianTocan/pdf-indexing-pages-for-agents/actions/workflows/ci.yml/badge.svg)](https://github.com/OctavianTocan/pdf-indexing-pages-for-agents/actions/workflows/ci.yml)
[![CodeQL](https://github.com/OctavianTocan/pdf-indexing-pages-for-agents/actions/workflows/codeql.yml/badge.svg)](https://github.com/OctavianTocan/pdf-indexing-pages-for-agents/actions/workflows/codeql.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)

Index born-digital PDFs into a hierarchical **section tree** for agent retrieval.
Uses Claude or Codex structured completions instead of vector chunking.

Heavily inspired by [PageIndex](https://github.com/VectifyAI/PageIndex) (Vectify AI):
vectorless tree RAG where the document's structure *is* the index. An agent
reasons over section titles and page ranges, then fetches only the pages it
needs. See [Acknowledgments](#acknowledgments) and [NOTICE](NOTICE).

**Not affiliated with Vectify AI or PageIndex.**

**Status:** alpha (`0.1.0`). The no-TOC indexing path and CLI run today.
Persistence, nested tree assembly, TOC-found indexing, and the MCP server are
still in progress.

## Why this shape

Most RAG pipelines split text into fixed chunks and embed them. That loses
document hierarchy and forces similarity search where an agent could just *read
the outline*.

PDFIndex aims for **retrieval-as-tools**:

1. Index a PDF into sections (`title`, page span, nested nodes when ready).
2. Expose thin read tools over a corpus (structure + page ranges).
3. Let the *consuming* agent decide relevance.

## What works today

| Piece | State |
| --- | --- |
| CLI `pdfindex --pdf_path …` | Works |
| Text + token extraction (`pypdf`) | Works |
| TOC page detection (leading pages) | Works |
| No-TOC structure generation (chunked + continuation) | Works |
| Completion providers: Claude Agent SDK, Codex SDK | Works |
| Flat `TreeStructure` list from `index()` | Works |
| Nested `Tree` / `node_id` / `doc_description` | Not wired yet |
| TOC-found → structure path | Stub after detection |
| SQLite corpus storage | Not wired |
| MCP server for agents | Not built yet |

## Requirements

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) (recommended)
- For Claude: OAuth token from `claude setup-token` (`CLAUDE_CODE_OAUTH_TOKEN`
  or `PDFINDEX_CLAUDE_CODE_OAUTH_TOKEN`)
- For Codex: a working Codex SDK setup (see `openai-codex` git dependency)

Born-digital PDFs only. Scanned / OCR docs are out of scope for now.

## Install

```bash
git clone https://github.com/OctavianTocan/pdf-indexing-pages-for-agents.git
cd pdf-indexing-pages-for-agents
uv sync
cp .env.example .env   # add tokens locally; never commit .env
```

## Usage

```bash
uv run pdfindex --pdf_path /path/to/document.pdf
```

Sample PDFs live under [`examples/documents/`](examples/):

```bash
uv run pdfindex --pdf_path examples/documents/q1-fy25-earnings.pdf
```

By default this uses the Claude completion client. Override via settings:

| Variable | Default | Meaning |
| --- | --- | --- |
| `PDFINDEX_COMPLETION_CLIENT` | `claude` | `claude` or `codex` |
| `PDFINDEX_COMPLETIONS_ENABLED` | `true` | Set `false` to skip LLM calls (empty structured responses) |
| `PDFINDEX_CLAUDE_MODEL` | `haiku` | Claude model alias |
| `PDFINDEX_CODEX_MODEL` | `gpt-5.5` | Codex model alias |
| `PDFINDEX_CLAUDE_CODE_OAUTH_TOKEN` | unset | Mirrored to `CLAUDE_CODE_OAUTH_TOKEN` for the Agent SDK |
| `PDFINDEX_MAX_TOKENS_PER_CHUNK` | `20000` | Chunk size for no-TOC generation |
| `PDFINDEX_TOP_CHECK_PAGE_NUM` | `20` | Leading pages scanned for a TOC |

## Layout

```
pdfindex/
  cli.py              # Typer entrypoint (`pdfindex`)
  logging_config.py   # Loguru setup
  config/             # pydantic-settings (`PDFINDEX_*`)
  completion/         # Claude / Codex / disabled adapters
  indexing/           # PDF → structure orchestration
  models/             # Pydantic schemas
  types/              # Aliases and protocols
tests/                # pytest suite
examples/documents/   # sample PDFs for local runs
```

## Development

See [CONTRIBUTING.md](CONTRIBUTING.md).

```bash
uv sync
uv run ruff format pdfindex tests
uv run ruff check pdfindex tests
uv run ty check pdfindex tests
uv run pytest -q
```

Or `just check`. CI runs the same checks (`.github/workflows/ci.yml`) plus
CodeQL on a schedule.

## Roadmap (short)

1. Finish TOC-found indexing (detect already works).
2. Assemble flat sections into a nested `Tree` with `node_id`s.
3. Persist documents + pages (SQLite corpus).
4. Ship a thin MCP server: document metadata, structure, page content.
5. Optional later: page-offset verify cascade, embedded PDF outline fast path.

## Security

Please report vulnerabilities privately. See [SECURITY.md](SECURITY.md).

## Acknowledgments

PDFIndex draws heavily on the ideas in
[PageIndex](https://github.com/VectifyAI/PageIndex) by Vectify AI (MIT License,
Copyright 2025 Vectify AI): hierarchical section trees as the retrieval index,
agent reasoning over structure, and thin read tools instead of vector search.

This repository is a **reduced, independent implementation** aimed at Claude /
Codex structured completions and a future MCP surface. It is **not** a fork of
PageIndex, does **not** redistribute the PageIndex source tree, and is **not
affiliated with or endorsed by Vectify AI**.

Deliberate divergences (among others): simpler TOC-found path (no
`toc_transformer` continuation loop by default), deferred page-offset
verify/patch cascade, and retrieval-as-tools via MCP rather than a bespoke
search loop. Full copyright notice: [NOTICE](NOTICE).

## License

MIT. See [LICENSE](LICENSE). Third-party notices: [NOTICE](NOTICE).

Changelog: [CHANGELOG.md](CHANGELOG.md).
