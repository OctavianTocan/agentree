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
- [x] **`Document.load` factory** — move PDF extract+tag construction onto
      `Document.load(pdf_path) -> Document`. Keep `tag_physical_indices` as a
      pure module-level function (unit-tested). `load_document` becomes a
      thin wrapper or goes away. Prefer helpers in `indexing/pdf_io.py` if
      `models` ↔ `indexing` import cycles appear. Do not make extract/tag
      mutating instance methods on the frozen bag.
      (`agentree/models/document.py`, `agentree/indexing/pdf_index.py`)
- [x] **`outline_to_flat_sections`** — pure: `list[OutlineSection]` +
      `last_page` → `list[FlatSection]`. Rule: `end = next.start - 1`; last
      section → `last_page`. Fail loud on missing `physical_index` (no
      PageIndex `appear_start` in v1). Unit-test with tiny fixtures (no PDF).
      Prefer `agentree/indexing/assemble.py`. PageIndex ref:
      `post_processing` (ranges half only).
- [x] **`flat_sections_to_nodes`** — pure: `list[FlatSection]` →
      `list[Node]`. Nest by dotted `structure` (`"1.1"` → parent `"1"`);
      assign zero-padded `node_id`. Unit-test with hand-built `FlatSection`s.
      Same `assemble.py`. PageIndex refs: `list_to_tree`, `write_node_id`.
- [x] **Wire `assemble_tree` + `index()`** — thin orchestrator:
      `outline_to_flat_sections` → `flat_sections_to_nodes` →
      `Tree(doc_name=doc.name, structure=nodes)`. Call from no-TOC (and later
      TOC) path. See `reference/pageindex-tree-product.md`.
      (`assemble_tree(outline, doc)`)
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
      CLI already has a stopgap `save_tree` → `output/<doc>.json`; replace with
      a real `agentree/storage/` interface (tree + pages + optional `.md`).
      (`agentree/cli.py`, `agentree/storage/`)

## Fix the draft quality (the tree is currently wrong)

A real run on `examples/documents/Regulation Best Interest_proposed rule.pdf`
(408 pages) exposed three defects. See
`reference/no-toc-structure-and-range-fixes.md` for the build spec + PageIndex
code. Do these before persistence — a broken tree isn't worth storing.

- [x] **Stop letting the model author the `code`** — done: model emits `depth`
      (0-based); nesting uses a depth stack in `flat_sections_to_nodes`;
      continuations get `open_spine(...)` only. (`agentree/models/outline.py`,
      `indexing/prompts.py`, `indexing/toc_extraction.py`, `indexing/assemble.py`)
- [x] **Fix `start_index > end_index`** — done via `OutlineSection.starts_at_top`
      (LLM fills it on the same outline call; no extra per-section call). Range
      math: `end = next.start - 1` if `starts_at_top` else `end = next.start`,
      with `end = max(start, end)`. (`models/outline.py`, `indexing/prompts.py`,
      `indexing/assemble.py`, tests)
- [ ] **Pre-flight cost estimate** — `agentree/completion/pricing.py` already
      logs *per-completion* cost. Still missing: one WARNING before fan-out from
      `sum(page.tokens)` × model $/1M, labelled as a lower bound (excludes
      output/thinking, retries, TOC scan, continuation re-sends).
      (`agentree/indexing/pdf_index.py`, `agentree/completion/pricing.py`)

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

- [x] Depth-based nesting + open-spine continuations (draft quality Fix 1).
- [x] `starts_at_top` range derivation (draft quality Fix 2; replaced string heuristic).
- [x] Add a CLI command that launches agentree, `agentree`.
- [x] No-TOC flat draft extraction (chunk + init/continue → `list[OutlineSection]`).
- [x] Document what PageIndex returns vs the draft:
      `reference/pageindex-tree-product.md`.
