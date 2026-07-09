"""Pydantic model definitions for document and structure schemas."""

from typing import Any
from typing import Self

from pydantic import BaseModel, ConfigDict, Field


def require_all_properties(schema: dict[str, Any]) -> None:
  """Codex/OpenAI strict schemas require every property to be defined.
  This function adds a `required` property to the schema for each property.

  Args:
    schema: The schema to add the `required` property to.
  """
  if 'properties' not in schema:
    return

  schema['required'] = list(schema['properties'].keys())


class StrictModel(BaseModel):
  """Base for schemas that may be used as Codex/OpenAI structured-output schemas."""

  # We need this to avoid Codex complaining about us not having `additionalProperties: false`.
  model_config = ConfigDict(
    extra='forbid',
    json_schema_extra=require_all_properties,
  )


class BoolModel(StrictModel):
  """A model that returns a boolean value."""

  value: bool = Field(description='The boolean value.')


class Node(BaseModel):
  """One section of a document; may nest child sections."""

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
  """The full index for one document: its section tree plus doc-level metadata."""

  doc_name: str = Field(description='Filename of the indexed document.')
  doc_description: str | None = Field(
    default=None,
    description='LLM-generated one-line description distinguishing this document from others.',
  )
  structure: list[Node] = Field(description="Root-level sections of the document's tree.")


class Page(BaseModel):
  """One page of a document."""

  content: str = Field(description='Raw extracted text of this page.')
  tokens: int = Field(ge=0, description='Number of tokens in the page content.')


class PageChunk(BaseModel):
  """One chunk of a document."""

  content: str = Field(description='The content of the chunk.')


class TreeStructure(StrictModel):
  """One section of a document's table of contents, as extracted by the model."""

  structure: str = Field(
    description='The structure index of the hierarchy section in the table of contents.'
  )
  title: str = Field(description='The title of the section.')
  physical_index: str | None = Field(
    default=None,
    description=(
      'The physical index of the start of the section, or null if it '
      "doesn't start in the given text."
    ),
  )


class TreeStructureList(StrictModel):
  """Flat list of sections extracted from one chunk of the document."""

  sections: list[TreeStructure] = Field(
    description='One entry per section found in the given text.'
  )
