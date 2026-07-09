# TODO

This is the markdown todo file for pdfindex.

## Indexing pipeline (vs PageIndex)

Gaps that block a usable PDF → tree index. See `MISSION.md` and
`reference/pageindex-pipeline.md`. Code markers live under `pdfindex/`.

- [ ] **TOC-found path** — detection works; after `find_toc_pages` the branch
      is a stub. Need: extract TOC text from those pages, ask the LLM for
      structured JSON directly (no PageIndex `toc_transformer` continuation
      loop), map entries to physical pages. Prefer combining detect+extract
      in one LLM call when touching this.
      (`pdfindex/indexing/pdf_index.py`, `toc_extraction.py`, `prompts.py`)
- [ ] **Flat → nested `Tree`** — `index()` returns `list[TreeStructure]`;
      storage and agents need `Tree` / `Node` (`start_index` / `end_index` /
      `node_id` / nested `nodes`). Implement assembly (PageIndex equivalents:
      `post_processing`, `list_to_tree`, `write_node_id`).
      (`pdfindex/indexing/pdf_index.py` → `build_document_node_tree`)
- [ ] **`doc_description`** — one LLM call over the (text-stripped) tree so
      an agent can pick this doc out of many. Field exists on `Tree`; no
      generator yet. (`pdfindex/indexing/`, `models/schemas.py`)
- [ ] **Expose per-page text from `index()`** — `extract_text_and_tokens`
      already produces pages; they never leave the function. Storage and
      `get_page_content` need them. Return pages alongside the tree (or a
      sibling API). (`pdfindex/indexing/pdf_index.py`)

## Persistence

- [ ] **Remake the SQLite storage layer manually** — current
      `pdfindex/storage/sqlite.py` is fully commented out; rewrite/restore
      schema + read/write paths.
- [ ] **Wire storage into the pipeline** — after `index()` emits a real
      `Tree` (+ pages), call `store_document` from the CLI/orchestrator so
      indexed PDFs persist under a corpus DB and can be queried later.
      (`pdfindex/cli.py`, `pdfindex/storage/`)

## Agent surface

- [ ] **MCP server** — thin read tools over the corpus for MCP clients
      (Claude Code, etc.): mirror PageIndex `retrieve.py` —
      `get_document`, `get_document_structure`, `get_page_content` — plus
      a way to trigger indexing. Shape still open: standalone stdio/HTTP
      vs in-process `create_sdk_mcp_server` (`MISSION.md`).

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

- [x] Add a CLI command that launches pdfindex, `pdfindex`.
