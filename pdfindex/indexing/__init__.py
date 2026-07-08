"""PDF indexing pipeline: extraction, chunking, and TOC inference."""

from pdfindex.indexing.pdf_index import index
from pdfindex.indexing.toc_extraction import (
  check_page_for_toc,
  generate_toc_continuation_structure,
  generate_toc_initial_structure,
)

__all__ = [
  'check_page_for_toc',
  'generate_toc_continuation_structure',
  'generate_toc_initial_structure',
  'index',
]
