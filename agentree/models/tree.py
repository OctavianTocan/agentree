"""Assembled index product: nested Node tree wrapped as Tree."""

from typing import Self

from pydantic import BaseModel, Field

from agentree.models.base import StrictModel


class DocumentDescription(StrictModel):
  """LLM-generated one-line description distinguishing this document from others."""

  description: str = Field(
    description='LLM-generated one-line description distinguishing this document from others.'
  )


class Node(BaseModel):
  """One section of a document; may nest child sections.

  Example::

      {
        'title': 'Results',
        'id': '0000',
        'start_index': 1,
        'end_index': 1,
        'children': [
          {
            'title': 'Key Points',
            'id': '0001',
            'start_index': 1,
            'end_index': 1,
            'children': [],
          }
        ],
      }
  """

  title: str = Field(description='Section heading text.')
  start_index: int = Field(description='First physical PDF page (1-indexed) this section spans.')
  end_index: int = Field(description='Last physical PDF page (1-indexed) this section spans.')
  id: str | None = Field(
    default=None, description="Zero-padded unique id within the tree, e.g. '0007'."
  )
  summary: str | None = Field(
    default=None, description="LLM-generated summary of this section's content."
  )
  text: str | None = Field(default=None, description='Raw page text for this section, if retained.')
  children: list[Self] = Field(
    default=[],
    description='Child sections nested under this one; empty for a leaf.',
  )


class Tree(BaseModel):
  """The full index for one document: its section tree plus doc-level metadata.

  Example::

      {
        'doc_name': 'q1-fy25-earnings.pdf',
        'doc_description': {
          'description': 'Q1 FY25 earnings release with results and outlook.',
        },
        'nodes': [
          {
            'title': 'Results',
            'id': '0000',
            'start_index': 1,
            'end_index': 1,
            'children': [
              {
                'title': 'Key Points',
                'id': '0001',
                'start_index': 1,
                'end_index': 1,
                'children': [],
              }
            ],
          },
          {'title': 'Outlook', 'id': '0002', 'start_index': 2, 'end_index': 3, 'children': []},
        ],
      }
  """

  doc_name: str = Field(description='Filename of the indexed document.')
  doc_description: DocumentDescription | None = Field(
    default=None,
    description='LLM-generated one-line description distinguishing this document from others.',
  )
  nodes: list[Node] = Field(description="Nodes of the document's tree.")
