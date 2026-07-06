from PDFindex.models import Node, Tree, TreeStructure, TreeStructureList


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


def test_tree_structure_physical_index_defaults_to_none():
  section = TreeStructure(structure='1', title='Overview')

  assert section.physical_index is None


def test_tree_structure_list_round_trips_through_json():
  sections = TreeStructureList(
    sections=[
      TreeStructure(structure='1', title='Overview', physical_index='<physical_index_7>'),
      TreeStructure(structure='2', title='Methods', physical_index=None),
    ]
  )

  round_tripped = TreeStructureList.model_validate_json(sections.model_dump_json())

  assert round_tripped == sections
