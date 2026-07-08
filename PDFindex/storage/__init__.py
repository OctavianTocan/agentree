"""SQLite persistence for indexed PDF corpora."""

from PDFindex.storage.sqlite import (
  compute_content_hash,
  get_document,
  get_document_structure,
  get_page_content,
  init_db,
  list_documents,
  store_document,
)

__all__ = [
  'compute_content_hash',
  'get_document',
  'get_document_structure',
  'get_page_content',
  'init_db',
  'list_documents',
  'store_document',
]
