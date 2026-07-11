"""Page-level document content schemas."""

from pydantic import BaseModel, Field


class Page(BaseModel):
  r"""One page of a document.

  Example::

      {'content': '<physical_index_1>\nHello\n<physical_index_1>\n\n', 'tokens': 12}
  """

  content: str = Field(description='Raw extracted text of this page.')
  tokens: int = Field(ge=0, description='Number of tokens in the page content.')


class PageChunk(BaseModel):
  r"""One token-budgeted slice of tagged pages (LLM input, not a semantic section).

  Example::

      {'content': '<physical_index_1>\n...\n<physical_index_2>\n...\n'}
  """

  content: str = Field(description='The content of the chunk.')
