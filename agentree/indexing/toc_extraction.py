"""Task-specific logic for extracting a document outline without a table of contents."""

from agentree.completion import StructuredCompletionClient, create_completion_client
from agentree.indexing.prompts import (
  CHECK_PAGE_FOR_TOC_PROMPT,
  EXTRACT_OUTLINE_CONTINUATION_PROMPT,
  EXTRACT_OUTLINE_INITIAL_PROMPT,
)
from agentree.models import BoolModel, Outline, Page

# TODO: Add TOC-found helpers used by pdf_index.index when toc_pages is non-empty:
#   - extract_toc_content(pages) → raw TOC text (or merge into check_page_for_toc)
#   - toc_to_structure(toc_text) → list[OutlineSection] via one direct LLM call
#     (deliberately skip PageIndex toc_transformer continuation; see MISSION.md)
#   - prompts for those live in prompts.py (also TODO there)
# TODO: Add generate_doc_description(tree) — one LLM call over the cleaned tree.


async def check_page_for_toc(page: Page, client: StructuredCompletionClient | None = None) -> bool:
  """Check if the page has a table of contents.

  Args:
      page: The page to check.
      client: Optional completion client override.

  Returns:
      True if the page has a table of contents, False otherwise.

  """
  client: StructuredCompletionClient = client or create_completion_client()
  result: BoolModel = await client.complete(
    page.content,
    BoolModel,
    system_prompt=CHECK_PAGE_FOR_TOC_PROMPT,
  )
  return result.value


async def extract_outline_initial(
  chunk_text: str, client: StructuredCompletionClient | None = None
) -> Outline:
  """Extract the draft outline from the first chunk of a document.

  Args:
      chunk_text: Page-tagged text of the first chunk.
      client: Optional completion client override.

  Returns:
      Sections found in this chunk, in document order.

  """
  client: StructuredCompletionClient = client or create_completion_client()
  result: Outline = await client.complete(
    chunk_text,
    Outline,
    system_prompt=EXTRACT_OUTLINE_INITIAL_PROMPT,
  )
  return result


async def extract_outline_continuation(
  chunk_text: str,
  previous_outline: Outline,
  client: StructuredCompletionClient | None = None,
) -> Outline:
  """Continue the draft outline into the next chunk, given what's been extracted so far.

  Args:
      chunk_text: Page-tagged text of the current chunk.
      previous_outline: Sections already extracted from earlier chunks.
      client: Optional completion client override.

  Returns:
      Only the new sections found in this chunk, in document order.

  """
  client: StructuredCompletionClient = client or create_completion_client()
  prompt: str = (
    f'Previous outline:\n{previous_outline.model_dump_json(indent=2)}\n\n'
    f'Current part of the document:\n{chunk_text}'
  )
  result: Outline = await client.complete(
    prompt,
    Outline,
    system_prompt=EXTRACT_OUTLINE_CONTINUATION_PROMPT,
  )
  return result
