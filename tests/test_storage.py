import hashlib
import sqlite3

import pytest

from PDFindex import storage
from PDFindex.models import Node, Page, Tree


def _make_tree() -> Tree:
    return Tree(
        doc_name="report.pdf",
        doc_description="An example report.",
        structure=[
            Node(
                title="Preface",
                start_index=1,
                end_index=4,
                node_id="0000",
                summary="Why this report exists.",
            ),
            Node(
                title="Methods",
                start_index=5,
                end_index=9,
                node_id="0001",
                summary="How we collected the data.",
                nodes=[
                    Node(
                        title="Data Collection",
                        start_index=5,
                        end_index=7,
                        node_id="0002",
                    ),
                ],
            ),
        ],
    )


def _make_pages(count: int = 9) -> list[Page]:
    return [Page(content=f"page {i} text", tokens=10) for i in range(1, count + 1)]


def _store_example(
    conn: sqlite3.Connection,
    *,
    content_hash: str = "a" * 64,
    tree: Tree | None = None,
    pages: list[Page] | None = None,
) -> str:
    return storage.store_document(
        conn,
        tree=tree or _make_tree(),
        pages=pages or _make_pages(),
        pdf_blob_path="blobs/aaaa.pdf",
        content_hash=content_hash,
        indexer_version="0.1.0",
        model="haiku",
    )


@pytest.fixture
def conn(tmp_path):
    db = storage.init_db(tmp_path / "index.db")
    yield db
    db.close()


def test_init_db_creates_all_tables(conn):
    tables = {
        row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type IN ('table')")
    }
    assert {"documents", "pages", "sections", "sections_fts"} <= tables


def test_init_db_is_idempotent(tmp_path):
    db_path = tmp_path / "index.db"

    storage.init_db(db_path)
    conn = storage.init_db(db_path)

    table_count = conn.execute(
        "SELECT COUNT(*) FROM sqlite_master WHERE type = 'table' AND name = 'documents'"
    ).fetchone()[0]
    conn.close()

    assert table_count == 1


class _EmptyCursor:
    def fetchone(self):
        return None

    def fetchall(self):
        return []


class _FakeConnWithoutFts5:
    """Minimal stub that reports no FTS5 in compile_options.

    `init_db` only gets as far as the FTS5 probe before raising, so we don't
    need a real engine underneath — just enough to make the probe return empty.
    """

    def execute(self, sql, *args, **kwargs):
        return _EmptyCursor()

    def close(self):
        return None


def test_init_db_fails_loud_without_fts5(tmp_path, monkeypatch):
    monkeypatch.setattr(storage.sqlite3, "connect", lambda _path: _FakeConnWithoutFts5())

    with pytest.raises(RuntimeError, match="FTS5"):
        storage.init_db(tmp_path / "index.db")


def test_compute_content_hash_matches_sha256(tmp_path):
    pdf = tmp_path / "x.pdf"
    pdf.write_bytes(b"hello")

    assert storage.compute_content_hash(pdf) == hashlib.sha256(b"hello").hexdigest()


def test_compute_content_hash_streams_large_files(tmp_path):
    pdf = tmp_path / "big.pdf"
    payload = b"x" * (1 << 20)
    pdf.write_bytes(payload)

    assert storage.compute_content_hash(pdf) == hashlib.sha256(payload).hexdigest()


def test_store_document_returns_doc_id_as_hash_prefix(conn):
    doc_id = _store_example(conn)

    assert doc_id == "a" * 16


def test_store_document_persists_pages_and_sections(conn):
    pages = _make_pages()
    _store_example(conn, pages=pages)

    page_count = conn.execute("SELECT COUNT(*) FROM pages").fetchone()[0]
    section_count = conn.execute("SELECT COUNT(*) FROM sections").fetchone()[0]
    fts_count = conn.execute("SELECT COUNT(*) FROM sections_fts").fetchone()[0]

    assert page_count == len(pages)
    assert section_count == 3
    assert fts_count == 3


def test_store_document_reindexes_same_hash_replaces_not_duplicates(conn):
    args = {
        "conn": conn,
        "tree": _make_tree(),
        "pages": _make_pages(),
        "pdf_blob_path": "blobs/aaaa.pdf",
        "content_hash": "a" * 64,
        "indexer_version": "0.1.0",
        "model": "haiku",
    }
    first = storage.store_document(**args)
    second = storage.store_document(**args)

    assert first == second
    assert conn.execute("SELECT COUNT(*) FROM documents").fetchone()[0] == 1
    assert conn.execute("SELECT COUNT(*) FROM sections").fetchone()[0] == 3
    assert conn.execute("SELECT COUNT(*) FROM sections_fts").fetchone()[0] == 3


def test_store_document_reindex_with_new_structure_replaces_old(conn):
    original_pages = _make_pages(count=9)
    _store_example(conn, pages=original_pages)

    new_tree = Tree(
        doc_name="report.pdf",
        doc_description="Revised.",
        structure=[
            Node(
                title="Only Chapter",
                start_index=1,
                end_index=9,
                node_id="0000",
                summary="New summary",
            ),
        ],
    )
    storage.store_document(
        conn,
        tree=new_tree,
        pages=original_pages,
        pdf_blob_path="blobs/aaaa.pdf",
        content_hash="a" * 64,
        indexer_version="0.2.0",
        model="haiku",
    )

    titles = [row[0] for row in conn.execute("SELECT title FROM sections")]
    assert titles == ["Only Chapter"]
    fts_titles = [row[0] for row in conn.execute("SELECT title FROM sections_fts")]
    assert fts_titles == ["Only Chapter"]
    assert conn.execute("SELECT COUNT(*) FROM pages").fetchone()[0] == 9


def test_store_document_records_indexer_version_and_model(conn):
    _store_example(conn)

    doc = storage.get_document(conn, "a" * 16)
    assert doc is not None
    assert doc["indexer_version"] == "0.1.0"
    assert doc["model"] == "haiku"


def test_store_document_writes_pages_in_document_order(conn):
    pages = [
        Page(content="alpha", tokens=1),
        Page(content="beta", tokens=2),
        Page(content="gamma", tokens=3),
    ]
    _store_example(conn, pages=pages)

    rows = conn.execute("SELECT page_num, content FROM pages ORDER BY page_num").fetchall()
    assert rows == [(1, "alpha"), (2, "beta"), (3, "gamma")]


def test_store_document_records_page_count_from_pages(conn):
    _store_example(conn, pages=_make_pages(count=7))

    doc = storage.get_document(conn, "a" * 16)
    assert doc is not None
    assert doc["page_count"] == 7


def test_store_document_rejects_node_without_id(conn):
    bad_tree = Tree(
        doc_name="report.pdf",
        structure=[Node(title="No ID", start_index=1, end_index=2)],
    )

    with pytest.raises(ValueError, match="node_id"):
        storage.store_document(
            conn,
            tree=bad_tree,
            pages=_make_pages(),
            pdf_blob_path="blobs/a.pdf",
            content_hash="a" * 64,
            indexer_version="0.1.0",
            model="haiku",
        )

    assert conn.execute("SELECT COUNT(*) FROM documents").fetchone()[0] == 0
    assert conn.execute("SELECT COUNT(*) FROM sections").fetchone()[0] == 0


def test_get_document_returns_metadata(conn):
    _store_example(conn)

    doc = storage.get_document(conn, "a" * 16)
    assert doc is not None
    assert doc["doc_name"] == "report.pdf"
    assert doc["doc_description"] == "An example report."
    assert doc["page_count"] == 9
    assert doc["content_hash"] == "a" * 64
    assert doc["pdf_blob_path"] == "blobs/aaaa.pdf"
    assert doc["indexed_at"]


def test_get_document_returns_none_for_missing(conn):
    assert storage.get_document(conn, "unknown") is None


def test_list_documents_returns_sorted_rows(conn):
    _store_example(conn, content_hash="b" * 64)
    _store_example(conn, content_hash="a" * 64)

    docs = storage.list_documents(conn)

    assert [d["doc_id"] for d in docs] == ["a" * 16, "b" * 16]


def test_list_documents_returns_empty_when_corpus_empty(conn):
    assert storage.list_documents(conn) == []


def test_get_document_structure_reconstructs_nested_tree(conn):
    _store_example(conn)

    roots = storage.get_document_structure(conn, "a" * 16)
    root_titles = [n["title"] for n in roots]
    assert root_titles == ["Preface", "Methods"]

    methods = next(n for n in roots if n["title"] == "Methods")
    assert len(methods["nodes"]) == 1
    data_collection = methods["nodes"][0]
    assert data_collection["title"] == "Data Collection"
    assert data_collection["path"] == "Methods › Data Collection"
    assert data_collection["start_index"] == 5
    assert data_collection["end_index"] == 7


def test_get_document_structure_preserves_summary_and_indices(conn):
    _store_example(conn)

    roots = storage.get_document_structure(conn, "a" * 16)
    preface = next(n for n in roots if n["title"] == "Preface")
    assert preface["summary"] == "Why this report exists."
    assert preface["start_index"] == 1
    assert preface["end_index"] == 4


def test_get_document_structure_missing_doc_is_empty(conn):
    assert storage.get_document_structure(conn, "nope") == []


def test_get_page_content_supports_ranges(conn):
    _store_example(conn)

    result = storage.get_page_content(conn, "a" * 16, "2-4")
    assert [r["page"] for r in result] == [2, 3, 4]
    assert result[0]["content"] == "page 2 text"


def test_get_page_content_supports_csv(conn):
    _store_example(conn)

    result = storage.get_page_content(conn, "a" * 16, "3,8,1")
    assert [r["page"] for r in result] == [1, 3, 8]


def test_get_page_content_supports_single_page(conn):
    _store_example(conn)

    result = storage.get_page_content(conn, "a" * 16, "5")
    assert result == [{"page": 5, "content": "page 5 text"}]


def test_get_page_content_drops_out_of_range_pages(conn):
    _store_example(conn)

    result = storage.get_page_content(conn, "a" * 16, "1-100")
    assert [r["page"] for r in result] == list(range(1, 10))


def test_get_page_content_missing_doc_returns_empty(conn):
    assert storage.get_page_content(conn, "nope", "1") == []


def test_get_page_content_rejects_malformed_input(conn):
    _store_example(conn)

    with pytest.raises(ValueError):
        storage.get_page_content(conn, "a" * 16, "not-a-page")


def test_get_page_content_rejects_inverted_range(conn):
    _store_example(conn)

    with pytest.raises(ValueError):
        storage.get_page_content(conn, "a" * 16, "7-3")


def test_fts_index_returns_sections_matching_summary_terms(conn):
    _store_example(conn)

    cur = conn.execute("SELECT title FROM sections_fts WHERE sections_fts MATCH 'collected'")
    titles = [row[0] for row in cur.fetchall()]
    assert "Methods" in titles


def test_fts_index_stays_in_sync_after_reindex(conn):
    _store_example(conn)
    new_tree = Tree(
        doc_name="report.pdf",
        doc_description="Revised.",
        structure=[
            Node(
                title="Only Chapter",
                start_index=1,
                end_index=9,
                node_id="0000",
                summary="Quantum mechanics intro",
            ),
        ],
    )
    storage.store_document(
        conn,
        tree=new_tree,
        pages=_make_pages(),
        pdf_blob_path="blobs/aaaa.pdf",
        content_hash="a" * 64,
        indexer_version="0.2.0",
        model="haiku",
    )

    cur = conn.execute("SELECT title FROM sections_fts WHERE sections_fts MATCH 'data'")
    assert cur.fetchall() == []
    cur = conn.execute("SELECT title FROM sections_fts WHERE sections_fts MATCH 'quantum'")
    assert [row[0] for row in cur.fetchall()] == ["Only Chapter"]
