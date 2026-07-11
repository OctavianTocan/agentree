"""PDF indexing pipeline: extraction, chunking, and outline inference."""

from agentree.indexing.pdf_index import index
from agentree.indexing.toc_extraction import (
  check_page_for_toc,
  extract_outline_continuation,
  extract_outline_initial,
)

__all__ = [
  'check_page_for_toc',
  'extract_outline_continuation',
  'extract_outline_initial',
  'index',
]
