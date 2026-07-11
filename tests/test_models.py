import pytest
from pydantic import ValidationError

from agentree.models import (
  Document,
  FlatSection,
  Node,
  OutlineSection,
  OutlineSectionList,
  Page,
  Tree,
)


def test_tree_round_trips_through_json():
  tree = Tree(
    doc_name='report.pdf',
    structure=[
      Node(title='Preface', start_index=1, end_index=4, node_id='0000'),
      Node(
        title='Methods',
        start_index=5,
        end_index=9,
        node_id='0001',
        nodes=[
          Node(title='Data Collection', start_index=5, end_index=7, node_id='0002'),
        ],
      ),
    ],
  )

  round_tripped = Tree.model_validate_json(tree.model_dump_json())

  assert round_tripped == tree


def test_leaf_node_defaults_to_no_children():
  node = Node(title='Conclusion', start_index=10, end_index=11)

  assert node.nodes == []


def test_outline_section_physical_index_defaults_to_none():
  section = OutlineSection(structure='1', title='Overview')

  assert section.physical_index is None


def test_outline_section_list_round_trips_through_json():
  sections = OutlineSectionList(
    sections=[
      OutlineSection(structure='1', title='Overview', physical_index=7),
      OutlineSection(structure='2', title='Methods', physical_index=None),
    ]
  )

  round_tripped = OutlineSectionList.model_validate_json(sections.model_dump_json())

  assert round_tripped == sections


def test_flat_section_has_page_range():
  section = FlatSection(structure='1', title='Results', start_index=1, end_index=1)

  assert section.start_index == 1
  assert section.end_index == 1


def test_document_is_frozen():
  doc = Document.from_pages('a.pdf', [Page(content='x', tokens=1)])

  assert doc.model_config['frozen'] is True
  with pytest.raises(ValidationError):
    doc.__setattr__('name', 'other.pdf')
