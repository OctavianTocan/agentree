from pathlib import Path

from agentree.indexing.assemble import open_spine
from agentree.indexing.pdf_index import assemble_tree
from agentree.models import Document, Outline, OutlineSection, Page


def _tagged_page(index: int, *lines: str) -> Page:
  body = '\n'.join(lines)
  content = f'<physical_index_{index}>\n{body}\n<physical_index_{index}>\n'
  return Page(content=content, tokens=max(1, len(content.split())))


def _three_section_outline() -> Outline:
  return Outline(
    sections=[
      OutlineSection(depth=0, title='Overview', physical_index=1),
      OutlineSection(depth=1, title='Background', physical_index=2),
      OutlineSection(depth=0, title='Methods', physical_index=4),
    ]
  )


def _doc_for_three_section_outline() -> Document:
  # Each heading sits at the top of its section's start page, so every following
  # section reads as a clean page break (end = next start - 1).
  return Document.from_pages(
    'doc.pdf',
    [
      _tagged_page(1, 'Overview', 'Intro prose.'),
      _tagged_page(2, 'Background', 'Background prose.'),
      _tagged_page(3, 'More background prose.'),
      _tagged_page(4, 'Methods', 'Methods prose.'),
      _tagged_page(5, 'More methods prose.'),
    ],
  )


def test_assemble_tree_nests_by_depth_and_derives_ranges() -> None:
  tree = assemble_tree(_three_section_outline(), _doc_for_three_section_outline())

  assert tree.doc_name == 'doc.pdf'
  # Two roots; the depth-1 section nests under the preceding depth-0 one.
  overview, methods = tree.nodes
  assert (overview.title, methods.title) == ('Overview', 'Methods')
  assert [child.title for child in overview.children] == ['Background']
  assert methods.children == []
  # Each heading opens its page, so end = next section's start - 1; the last
  # section runs to last_page (5).
  background = overview.children[0]
  assert (overview.start_index, overview.end_index) == (1, 1)
  assert (background.start_index, background.end_index) == (2, 3)
  assert (methods.start_index, methods.end_index) == (4, 5)


def test_assemble_tree_extends_range_when_next_heading_not_at_page_start() -> None:
  # 'Methods' starts mid-page 2, past the leading window the heuristic inspects,
  # so page 2 reads as shared and Overview extends onto it.
  trailing_overview = (
    'This paragraph continues the overview from the previous page and runs on '
    'long enough that the next heading falls well outside the leading window '
    'the page-start heuristic actually inspects on this page.'
  )
  doc = Document.from_pages(
    'doc.pdf',
    [
      _tagged_page(1, 'Overview', 'Intro prose.'),
      _tagged_page(2, trailing_overview, 'Methods', 'Methods prose.'),
    ],
  )
  outline = Outline(
    sections=[
      OutlineSection(depth=0, title='Overview', physical_index=1),
      OutlineSection(depth=0, title='Methods', physical_index=2),
    ]
  )

  overview, methods = assemble_tree(outline, doc).nodes

  assert (overview.start_index, overview.end_index) == (1, 2)
  assert (methods.start_index, methods.end_index) == (2, 2)


def test_assemble_tree_assigns_zero_padded_ids_in_document_order() -> None:
  tree = assemble_tree(_three_section_outline(), _doc_for_three_section_outline())

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
