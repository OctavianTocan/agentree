"""SQLite storage layer for the indexed PDF corpus.

One DB file holds the whole corpus: documents, per-page text, and a flattened
section tree with a sister FTS5 index over section titles and summaries. Search
tooling itself is wired up elsewhere — this module owns only the schema and the
read/write paths over it.
"""

from __future__ import annotations

import hashlib
import sqlite3
from collections.abc import Iterator
from datetime import datetime, timezone
from pathlib import Path
from typing import NamedTuple

from pdfindex.models import Node, Page, Tree

_SCHEMA = """
CREATE TABLE IF NOT EXISTS documents (
    doc_id          TEXT PRIMARY KEY,
    content_hash    TEXT UNIQUE NOT NULL,
    doc_name        TEXT NOT NULL,
    doc_description TEXT,
    page_count      INTEGER NOT NULL,
    pdf_blob_path   TEXT NOT NULL,
    indexer_version TEXT NOT NULL,
    model           TEXT NOT NULL,
    indexed_at      TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS pages (
    doc_id      TEXT NOT NULL REFERENCES documents(doc_id) ON DELETE CASCADE,
    page_num    INTEGER NOT NULL,
    content     TEXT NOT NULL,
    token_count INTEGER NOT NULL,
    PRIMARY KEY (doc_id, page_num)
) WITHOUT ROWID;
CREATE TABLE IF NOT EXISTS sections (
    doc_id      TEXT NOT NULL REFERENCES documents(doc_id) ON DELETE CASCADE,
    node_id     TEXT NOT NULL,
    parent_id   TEXT,
    path        TEXT NOT NULL,
    title       TEXT NOT NULL,
    summary     TEXT,
    start_index INTEGER NOT NULL,
    end_index   INTEGER NOT NULL,
    PRIMARY KEY (doc_id, node_id)
) WITHOUT ROWID;
CREATE VIRTUAL TABLE IF NOT EXISTS sections_fts USING fts5(
    doc_id UNINDEXED, node_id UNINDEXED, title, summary,
    tokenize = 'porter unicode61'
);
"""

_PATH_SEPARATOR = ' › '


class _SectionRow(NamedTuple):
  """One flattened section, in the shape it gets written to SQLite.

  Being a NamedTuple means `executemany` accepts a list of these directly,
  and named field access makes the FTS extract read cleanly.
  """

  doc_id: str
  node_id: str
  parent_id: str | None
  path: str
  title: str
  summary: str | None
  start_index: int
  end_index: int


_DOCUMENT_COLUMNS = (
  'doc_id',
  'content_hash',
  'doc_name',
  'doc_description',
  'page_count',
  'pdf_blob_path',
  'indexer_version',
  'model',
  'indexed_at',
)


def init_db(db_path: Path | str) -> sqlite3.Connection:
  """Open (or create) the corpus DB, initialize its schema, and verify FTS5.

  Args:
      db_path: Filesystem path to the SQLite DB file; created if missing.

  Returns:
      Open connection with foreign keys enabled and all tables in place.
      The caller owns the connection's lifetime.

  Raises:
      RuntimeError: if the linked SQLite was built without FTS5 support.

  """
  conn = sqlite3.connect(str(db_path))
  conn.execute('PRAGMA foreign_keys = ON')
  fts_available = conn.execute(
    "SELECT 1 FROM pragma_compile_options() WHERE compile_options = 'ENABLE_FTS5'"
  ).fetchone()
  if not fts_available:
    conn.close()
    raise RuntimeError('SQLite FTS5 extension is required but not available in this build.')
  conn.executescript(_SCHEMA)
  conn.commit()
  return conn


def compute_content_hash(pdf_path: Path | str) -> str:
  """SHA-256 hex digest of a PDF's bytes.

  The first 16 hex chars become the document's `doc_id`, so re-indexing the
  same file is a no-op.

  Args:
      pdf_path: Filesystem path to a PDF file.

  Returns:
      Lowercase 64-character hex digest.

  """
  digest = hashlib.sha256()
  with open(pdf_path, 'rb') as f:
    for chunk in iter(lambda: f.read(65536), b''):
      digest.update(chunk)
  return digest.hexdigest()


def store_document(
  conn: sqlite3.Connection,
  *,
  tree: Tree,
  pages: list[Page],
  pdf_blob_path: Path | str,
  content_hash: str,
  indexer_version: str,
  model: str,
) -> str:
  """Persist one document (metadata, pages, section tree) in one transaction.

  Re-indexing the same PDF (same `content_hash`) upserts: existing rows for
  that `doc_id` are deleted (cascade covers `pages` and `sections`; the FTS
  table is cleaned explicitly since FTS5 tables can't carry a foreign key),
  then the new rows are inserted.

  Args:
      conn: Open connection from `init_db`.
      tree: Indexed document structure (the rich `Tree` model).
      pages: One `Page` per physical PDF page, in page order. Drives the
          `page_count` and backs `get_page_content` lookups.
      pdf_blob_path: Location of the canonical PDF copy. Caller-managed; a
          content-addressed layout like `corpus/blobs/<content_hash>.pdf` is
          recommended but not enforced.
      content_hash: SHA-256 of the PDF bytes (see `compute_content_hash`).
          The first 16 hex chars become the `doc_id`.
      indexer_version: Version of the indexer that produced this `tree`, so a
          prompt or model bump can trigger a re-index.
      model: Model alias (e.g. "haiku") that produced this `tree`.

  Returns:
      The `doc_id` (first 16 hex chars of `content_hash`).

  """
  doc_id = content_hash[:16]
  indexed_at = datetime.now(timezone.utc).isoformat()

  try:
    conn.execute('BEGIN')
    conn.execute('DELETE FROM sections_fts WHERE doc_id = ?', (doc_id,))
    conn.execute('DELETE FROM documents WHERE doc_id = ?', (doc_id,))

    conn.execute(
      """
            INSERT INTO documents
                (doc_id, content_hash, doc_name, doc_description, page_count,
                 pdf_blob_path, indexer_version, model, indexed_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
      (
        doc_id,
        content_hash,
        tree.doc_name,
        tree.doc_description,
        len(pages),
        str(pdf_blob_path),
        indexer_version,
        model,
        indexed_at,
      ),
    )

    if pages:
      conn.executemany(
        """
                INSERT INTO pages (doc_id, page_num, content, token_count)
                VALUES (?, ?, ?, ?)
                """,
        [
          (doc_id, page_num, page.content, page.tokens)
          for page_num, page in enumerate(pages, start=1)
        ],
      )
    section_rows = list(_flatten_sections(tree.structure, doc_id=doc_id))
    if section_rows:
      conn.executemany(
        """
                INSERT INTO sections
                    (doc_id, node_id, parent_id, path, title, summary,
                     start_index, end_index)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
        section_rows,
      )
      conn.executemany(
        """
                INSERT INTO sections_fts (doc_id, node_id, title, summary)
                VALUES (?, ?, ?, ?)
                """,
        [(row.doc_id, row.node_id, row.title, row.summary or '') for row in section_rows],
      )
    conn.execute('COMMIT')
  except Exception:
    conn.execute('ROLLBACK')
    raise

  return doc_id


def _flatten_sections(
  nodes: list[Node],
  *,
  doc_id: str,
  parent_id: str | None = None,
  ancestor_titles: tuple[str, ...] = (),
) -> Iterator[_SectionRow]:
  """Walk the tree depth-first, yielding one `_SectionRow` per node.

  Builds a human-readable `path` from ancestor titles (e.g.
  `"Methods › Data Collection"`) so a search hit can be displayed without
  reconstructing the tree.
  """
  for node in nodes:
    if node.node_id is None:
      raise ValueError(f'Every Node in a stored Tree must have a node_id; {node.title!r} does not.')
    path_titles = (*ancestor_titles, node.title)
    yield _SectionRow(
      doc_id=doc_id,
      node_id=node.node_id,
      parent_id=parent_id,
      path=_PATH_SEPARATOR.join(path_titles),
      title=node.title,
      summary=node.summary,
      start_index=node.start_index,
      end_index=node.end_index,
    )
    if node.nodes:
      yield from _flatten_sections(
        node.nodes,
        doc_id=doc_id,
        parent_id=node.node_id,
        ancestor_titles=path_titles,
      )


def _row_to_document(row: tuple) -> dict:
  return dict(zip(_DOCUMENT_COLUMNS, row, strict=True))


def get_document(conn: sqlite3.Connection, doc_id: str) -> dict | None:
  """Return document metadata as a dict, or None if `doc_id` is unknown."""
  row = conn.execute(
    f"""
        SELECT {', '.join(_DOCUMENT_COLUMNS)}
        FROM documents WHERE doc_id = ?
        """,
    (doc_id,),
  ).fetchone()
  return _row_to_document(row) if row else None


def list_documents(conn: sqlite3.Connection) -> list[dict]:
  """Return metadata for every document, sorted by `doc_name` then `doc_id`."""
  rows = conn.execute(
    f"""
        SELECT {', '.join(_DOCUMENT_COLUMNS)}
        FROM documents ORDER BY doc_name, doc_id
        """
  ).fetchall()
  return [_row_to_document(row) for row in rows]


def get_document_structure(conn: sqlite3.Connection, doc_id: str) -> list[dict]:
  """Reconstruct the nested section tree for one document.

  Args:
      conn: Open connection from `init_db`.
      doc_id: Document whose section tree to load.

  Returns:
      A list of root nodes, each a dict with `node_id`, `title`, `summary`,
      `start_index`, `end_index`, `path`, and a `nodes` list. Returns an
      empty list if the document has no sections or doesn't exist.

  """
  rows = conn.execute(
    """
        SELECT node_id, parent_id, path, title, summary, start_index, end_index
        FROM sections WHERE doc_id = ?
        ORDER BY start_index, node_id
        """,
    (doc_id,),
  ).fetchall()

  nodes_by_id: dict[str, dict] = {}
  root_ids: list[str] = []
  for node_id, parent_id, path, title, summary, start_index, end_index in rows:
    nodes_by_id[node_id] = {
      'node_id': node_id,
      'title': title,
      'summary': summary,
      'start_index': start_index,
      'end_index': end_index,
      'path': path,
      'nodes': [],
    }
    if parent_id is None:
      root_ids.append(node_id)

  # Second pass attaches children. Iterating rows in (start_index, node_id)
  # order means each parent's children are appended in document order.
  for node_id, parent_id, *_ in rows:
    if parent_id is not None and parent_id in nodes_by_id:
      nodes_by_id[parent_id]['nodes'].append(nodes_by_id[node_id])

  return [nodes_by_id[node_id] for node_id in root_ids]


def get_page_content(conn: sqlite3.Connection, doc_id: str, pages: str) -> list[dict]:
  """Fetch the text of specific pages for one document.

  Args:
      conn: Open connection from `init_db`.
      doc_id: Document to read.
      pages: Page selector — `'5-7'` (range), `'3,8'` (list), or `'12'`
          (single), 1-indexed. Matches the format PageIndex's retrieve layer
          accepts (`PageIndex/pageindex/retrieve.py:12`).

  Returns:
      One `{'page': int, 'content': str}` per requested page that exists, in
      ascending page order. Out-of-range pages are silently dropped.

  Raises:
      ValueError: if `pages` is malformed or a range has start > end.

  """
  page_nums = _parse_pages(pages)
  if not page_nums:
    return []
  placeholders = ','.join('?' * len(page_nums))
  rows = conn.execute(
    f"""
        SELECT page_num, content FROM pages
        WHERE doc_id = ? AND page_num IN ({placeholders})
        """,
    [doc_id, *page_nums],
  ).fetchall()
  return sorted(
    ({'page': num, 'content': content} for num, content in rows),
    key=lambda r: r['page'],
  )


def _parse_pages(pages: str) -> list[int]:
  """Parse a pages selector string into a sorted, de-duplicated list of ints.

  Mirrors PageIndex's `_parse_pages`. Examples: `'5-7'` -> `[5, 6, 7]`,
  `'3,8'` -> `[3, 8]`, `'12'` -> `[12]`.

  Raises:
      ValueError: if a part isn't an int, or a range has start > end.

  """
  result: list[int] = []
  for part in pages.split(','):
    part = part.strip()
    if '-' in part:
      start_str, end_str = part.split('-', 1)
      start, end = int(start_str.strip()), int(end_str.strip())
      if start > end:
        raise ValueError(f'Invalid range {part!r}: start must be <= end.')
      result.extend(range(start, end + 1))
    else:
      result.append(int(part))
  return sorted(set(result))
