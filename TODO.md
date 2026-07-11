# TODO

This is the markdown todo file for agentree.

**North star:** PDF → nested tree index agents can read → fetch page ranges.
See `MISSION.md` and `reference/pageindex-tree-product.md` (what PageIndex
returns + how assembly works). Full pipeline map:
`reference/pageindex-pipeline.md`. Code markers live under `agentree/`.

## Get a usable index (do these first)

The no-TOC path already emits a **flat draft**. Finish the product, then
store it. Lesson: `lessons/0005-assemble-tree-and-markdown-store.md`.

- [x] **`physical_index` as int from the LLM** — keep `<physical_index_N>`
      tags in page *input* text; stop asking for tag strings in the JSON.
      Change `OutlineSection.physical_index` to `int | None`, update both
      generate-structure prompts to emit the integer `N`, fix tests that
      expect `'<physical_index_…>'`. Makes PageIndex-style
      `convert_physical_index_to_int` unnecessary for the no-TOC path.
      (`agentree/models/outline.py`, `indexing/prompts.py`,
      `tests/test_toc_extraction.py`, `tests/test_models.py`)
- [ ] **Flat → nested `Tree`** — `index()` returns `list[OutlineSection]`;
      agents need `Tree` / `Node` (`start_index` / `end_index` / `node_id` /
      nested `nodes`). Implement assembly via `FlatSection` mid-stage
      (PageIndex: `post_processing`, `list_to_tree`, `write_node_id`; skip
      tag→int convert if the item above lands first). See
      `reference/pageindex-tree-product.md`.
      (`assemble_tree(outline, doc)` — `Document` supplies name + last_page)
- [ ] **Expose per-page text from `index()`** — `Document.pages` already
      holds tagged pages; they never leave `index()`. Storage and
      `get_page_content` need them. Return pages alongside the tree (or a
      small result type). (`agentree/indexing/pdf_index.py`)
- [ ] **`doc_description`** — one LLM call over the (text-stripped) tree so
      an agent can pick this doc out of many. Field exists on `Tree`; no
      generator yet. (`agentree/indexing/`, `models/tree.py`; PageIndex
      `generate_doc_description`)
- [ ] **Markdown/JSON corpus store (first persistence)** — thin write/read
      adapter over the `Tree` (+ pages): on-disk JSON for the machine
      contract, optional `.md` outline (headings + page ranges) for humans.
      Wire CLI so indexing writes something observable. Swap in SQLite/DB
      later behind the same interface. (`agentree/cli.py`, `agentree/storage/`)

## Indexing pipeline (after the product works)

- [ ] **TOC-found path** — detection works; after `find_toc_pages` the branch
      is a stub. Need: extract TOC text from those pages, ask the LLM for
      structured JSON directly (no PageIndex `toc_transformer` continuation
      loop), map entries to physical pages. Prefer combining detect+extract
      in one LLM call when touching this. Same flat draft → reuse assembly
      above. (`agentree/indexing/pdf_index.py`, `toc_extraction.py`,
      `prompts.py`)

## Persistence (later backends)

- [ ] **SQLite (or other DB) behind the same store interface** — optional
      upgrade once the markdown/JSON adapter proves the contract. Old
      commented `sqlite.py` is not load-bearing; remake only when needed.
      (`agentree/storage/`)

## Agent surface

- [ ] **MCP server** — thin read tools over the corpus for MCP clients
      (Claude Code, etc.): mirror PageIndex `retrieve.py` —
      `get_document`, `get_document_structure`, `get_page_content` — plus
      a way to trigger indexing. Shape still open: standalone stdio/HTTP
      vs in-process `create_sdk_mcp_server` (`MISSION.md`).
      Requires the tree product + a working store first.

## Providers

- [ ] Integrate more LLMs, particularly subscription-based ones, so people
      can use this basically for free. OpenCode is a good candidate.

## Deferred (do not build until the simple path fails)

These exist in PageIndex; we cut/deferred them on purpose (`MISSION.md`):

- [ ] Page-offset correction + verify / patch / downgrade cascade
- [ ] Embedded PDF outline fast path
- [ ] Recursive split of oversized nodes
- [ ] Per-node `text` / `summary` assembly (optional later)

## Release

# DONE

- [x] Add a CLI command that launches agentree, `agentree`.
- [x] No-TOC flat draft extraction (chunk + init/continue → `list[OutlineSection]`).
- [x] Document what PageIndex returns vs the draft:
      `reference/pageindex-tree-product.md`.
