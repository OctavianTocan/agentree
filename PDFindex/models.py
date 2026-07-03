from __future__ import annotations

from pydantic import BaseModel, Field


class Node(BaseModel):
    """One section of a document; may nest child sections."""

    title: str = Field(description="Section heading text.")
    start_index: int = Field(
        description="First physical PDF page (1-indexed) this section spans."
    )
    end_index: int = Field(
        description="Last physical PDF page (1-indexed) this section spans."
    )
    node_id: str | None = Field(
        default=None, description="Zero-padded unique id within the tree, e.g. '0007'."
    )
    summary: str | None = Field(
        default=None, description="LLM-generated summary of this section's content."
    )
    text: str | None = Field(
        default=None, description="Raw page text for this section, if retained."
    )
    nodes: list[Node] = Field(
        default=[],
        description="Child sections nested under this one; empty for a leaf.",
    )


class Tree(BaseModel):
    """The full index for one document: its section tree plus doc-level metadata."""

    doc_name: str = Field(description="Filename of the indexed document.")
    doc_description: str | None = Field(
        default=None,
        description="LLM-generated one-line description distinguishing this document from others.",
    )
    structure: list[Node] = Field(
        description="Root-level sections of the document's tree."
    )


class Page(BaseModel):
    """One page of a document."""

    content: str = Field(description="Raw extracted text of this page.")
    tokens: int = Field(ge=0, description="Number of tokens in the page content.")
