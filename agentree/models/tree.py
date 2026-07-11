"""Assembled index product: nested Node tree wrapped as Tree."""

from pydantic import BaseModel, Field
from typing_extensions import Self


# TODO: index() should eventually return Tree (not list[OutlineSection]).
# Node/Tree are the storage + MCP contract; the producer still emits flat
# OutlineSection only — see assemble_tree in pdf_index.py.
class Node(BaseModel):
  """One section of a document; may nest child sections.

  Example::

      {
        'title': 'Results',
        'node_id': '0000',
        'start_index': 1,
        'end_index': 1,
        'nodes': [
          {'title': 'Key Points', 'node_id': '0001', 'start_index': 1, 'end_index': 1, 'nodes': []}
        ],
      }
  """

  title: str = Field(description='Section heading text.')
  start_index: int = Field(description='First physical PDF page (1-indexed) this section spans.')
  end_index: int = Field(description='Last physical PDF page (1-indexed) this section spans.')
  node_id: str | None = Field(
    default=None, description="Zero-padded unique id within the tree, e.g. '0007'."
  )
  summary: str | None = Field(
    default=None, description="LLM-generated summary of this section's content."
  )
  text: str | None = Field(default=None, description='Raw page text for this section, if retained.')
  nodes: list[Self] = Field(
    default=[],
    description='Child sections nested under this one; empty for a leaf.',
  )


class Tree(BaseModel):
  """The full index for one document: its section tree plus doc-level metadata.

  Example::

      {
        'doc_name': 'q1-fy25-earnings.pdf',
        'doc_description': 'Q1 FY25 earnings release with results and outlook.',
        'structure': [
          {
            'title': 'Results',
            'node_id': '0000',
            'start_index': 1,
            'end_index': 1,
            'nodes': [
              {
                'title': 'Key Points',
                'node_id': '0001',
                'start_index': 1,
                'end_index': 1,
                'nodes': [],
              }
            ],
          },
          {'title': 'Outlook', 'node_id': '0002', 'start_index': 2, 'end_index': 3, 'nodes': []},
        ],
      }
  """

  doc_name: str = Field(description='Filename of the indexed document.')
  # TODO: Populate via generate_doc_description once tree assembly exists.
  doc_description: str | None = Field(
    default=None,
    description='LLM-generated one-line description distinguishing this document from others.',
  )
  structure: list[Node] = Field(description="Root-level sections of the document's tree.")
