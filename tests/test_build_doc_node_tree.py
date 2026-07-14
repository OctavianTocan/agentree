from pathlib import Path

import pytest

from agentree.indexing.pdf_index import assemble_tree
from agentree.models import Document, Outline, OutlineSection, Page


def _doc_with_pages(count: int) -> Document:
  return Document.from_pages('doc.pdf', [Page(content=str(i), tokens=1) for i in range(count)])


def test_assemble_tree_nests_by_code_and_derives_ranges():
  outline = Outline(
    sections=[
      OutlineSection(code='1', title='Overview', physical_index=1),
      OutlineSection(code='1.1', title='Background', physical_index=2),
      OutlineSection(code='2', title='Methods', physical_index=4),
    ]
  )

  tree = assemble_tree(outline, _doc_with_pages(5))

  assert tree.doc_name == 'doc.pdf'
  # Two roots; "1.1" nests under "1".
  overview, methods = tree.nodes
  assert (overview.title, methods.title) == ('Overview', 'Methods')
  assert [child.title for child in overview.children] == ['Background']
  assert methods.children == []
  # end = next section's start - 1; last section runs to last_page (5).
  background = overview.children[0]
  assert (overview.start_index, overview.end_index) == (1, 1)
  assert (background.start_index, background.end_index) == (2, 3)
  assert (methods.start_index, methods.end_index) == (4, 5)
  # Zero-padded ids in document order.
  assert (overview.id, background.id, methods.id) == ('0000', '0001', '0002')


def test_assemble_tree_fails_loud_on_missing_physical_index():
  outline = Outline(sections=[OutlineSection(code='1', title='Overview', physical_index=None)])

  with pytest.raises(ValueError, match='Physical index'):
    assemble_tree(outline, _doc_with_pages(2))


def test_document_exposes_name_and_last_page():
  path = Path('examples/documents/report.pdf')
  doc = Document.from_pages(
    path,
    [
      Page(content='<physical_index_1>\nx\n', tokens=3),
      Page(content='<physical_index_2>\ny\n', tokens=3),
    ],
  )

  assert doc.name == 'report.pdf'
  assert doc.last_page == 2
  assert doc.path == path
