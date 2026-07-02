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

    content: str = Field(description="Raw page text for this section, if retained.")
    tokens: int = Field(ge=0, description="Number of tokens in the page content.")


def _demo() -> None:
    tree = Tree(
        doc_name="2023-annual-report-truncated.pdf",
        structure=[
            Node(title="Preface", start_index=1, end_index=4, node_id="0000"),
            Node(
                title="Monetary Policy and Economic Developments",
                start_index=9,
                end_index=9,
                node_id="0003",
                nodes=[
                    Node(
                        title="March 2024 Summary",
                        start_index=9,
                        end_index=14,
                        node_id="0004",
                    ),
                    Node(
                        title="June 2023 Summary",
                        start_index=15,
                        end_index=20,
                        node_id="0005",
                    ),
                ],
            ),
        ],
    )
    round_tripped = Tree.model_validate_json(tree.model_dump_json())
    assert round_tripped == tree
    print(tree.model_dump_json(indent=2, exclude_none=True))


if __name__ == "__main__":
    _demo()
