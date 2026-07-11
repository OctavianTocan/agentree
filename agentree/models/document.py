"""Immutable facts about one PDF being indexed."""

from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from agentree.models.pages import Page


class Document(BaseModel):
  """PDF facts for the indexing pipeline — path, name, tagged pages.

  Not a mutable session: holds what we know about the file, not outline/tree
  state. Transforms stay as functions (outline → Tree).

  Example::

      {
        'path': 'report.pdf',
        'name': 'report.pdf',
        'pages': [{'content': '<physical_index_1> Hello', 'tokens': 8}],
      }
  """

  model_config = ConfigDict(frozen=True)

  path: Path = Field(description='Filesystem path to the PDF.')
  name: str = Field(description='Basename of the PDF (used as Tree.doc_name).')
  pages: list[Page] = Field(
    description='Physically tagged pages in document order (1-indexed markers).'
  )

  @property
  def last_page(self) -> int:
    """1-indexed count of pages (end_index for the final section)."""
    return len(self.pages)

  @classmethod
  def from_pages(cls, pdf_path: str | Path, pages: list[Page]) -> 'Document':
    """Build a Document from a path and already-tagged pages."""
    path = Path(pdf_path)
    return cls(path=path, name=path.name, pages=pages)
