from pathlib import Path

import pytest

from agentree.indexing.pdf_index import assemble_tree
from agentree.models import Document, OutlineSection, Page


def test_assemble_tree_not_implemented_yet():
  outline: list[OutlineSection] = [
    OutlineSection(structure='1', title='Overview', physical_index=2),
    OutlineSection(structure='2', title='Methods', physical_index=5),
  ]
  doc = Document.from_pages(
    'doc.pdf',
    [Page(content='a', tokens=1), Page(content='b', tokens=1)],
  )
  with pytest.raises(NotImplementedError):
    assemble_tree(outline, doc)


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
