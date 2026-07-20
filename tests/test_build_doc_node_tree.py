from pathlib import Path

from agentree.indexing.assemble import open_spine
from agentree.indexing.pdf_index import assemble_tree
from agentree.models import Document, Outline, OutlineSection, Page


def _blank_doc(page_count: int) -> Document:
  return Document.from_pages('doc.pdf', [Page(content='', tokens=1) for _ in range(page_count)])


def _three_section_outline() -> Outline:
  return Outline(
    sections=[
      OutlineSection(depth=0, title='Overview', physical_index=1, starts_at_top=True),
      OutlineSection(depth=1, title='Background', physical_index=2, starts_at_top=True),
      OutlineSection(depth=0, title='Methods', physical_index=4, starts_at_top=True),
    ]
  )


def test_assemble_tree_nests_by_depth_and_derives_ranges() -> None:
  tree = assemble_tree(_three_section_outline(), _blank_doc(page_count=5))

  assert tree.doc_name == 'doc.pdf'
  # Two roots; the depth-1 section nests under the preceding depth-0 one.
  overview, methods = tree.nodes
  assert (overview.title, methods.title) == ('Overview', 'Methods')
  assert [child.title for child in overview.children] == ['Background']
  assert methods.children == []
  # Every heading opens its page, so each section ends one page before the next;
  # the last section runs to last_page (5).
  background = overview.children[0]
  assert (overview.start_index, overview.end_index) == (1, 1)
  assert (background.start_index, background.end_index) == (2, 3)
  assert (methods.start_index, methods.end_index) == (4, 5)


def test_assemble_tree_extends_range_when_next_section_starts_mid_page() -> None:
  outline = Outline(
    sections=[
      OutlineSection(depth=0, title='Overview', physical_index=1, starts_at_top=True),
      OutlineSection(depth=0, title='Methods', physical_index=2, starts_at_top=False),
    ]
  )

  overview, methods = assemble_tree(outline, _blank_doc(page_count=2)).nodes

  # 'Methods' does not start at the top of page 2, so Overview extends onto it.
  assert (overview.start_index, overview.end_index) == (1, 2)
  assert (methods.start_index, methods.end_index) == (2, 2)


def test_assemble_tree_assigns_zero_padded_ids_in_document_order() -> None:
  tree = assemble_tree(_three_section_outline(), _blank_doc(page_count=5))

  overview, methods = tree.nodes
  background = overview.children[0]
  assert (overview.id, background.id, methods.id) == ('0000', '0001', '0002')


def test_open_spine_keeps_only_the_rightmost_open_ancestors() -> None:
  sections = [
    OutlineSection(depth=0, title='A', physical_index=1),
    OutlineSection(depth=1, title='A.1', physical_index=2),
    OutlineSection(depth=2, title='A.1.a', physical_index=3),
    OutlineSection(depth=1, title='A.2', physical_index=4),
    OutlineSection(depth=2, title='A.2.a', physical_index=5),
  ]

  spine = open_spine(sections)

  assert [section.title for section in spine] == ['A', 'A.2', 'A.2.a']


def test_open_spine_of_empty_outline_is_empty() -> None:
  assert open_spine([]) == []


def test_open_spine_collapses_siblings_at_the_same_depth() -> None:
  sections = [
    OutlineSection(depth=0, title='A', physical_index=1),
    OutlineSection(depth=0, title='B', physical_index=2),
  ]

  spine = open_spine(sections)

  assert [section.title for section in spine] == ['B']


def test_document_exposes_name_and_last_page() -> None:
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
