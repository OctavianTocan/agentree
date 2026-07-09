"""Task-specific logic for extracting a document's tree structure without a table of contents."""

from pdfindex.completion import StructuredCompletionClient, create_completion_client
from pdfindex.indexing.prompts import (
  CHECK_PAGE_FOR_TOC_PROMPT,
  GENERATE_TREE_STRUCTURE_CONTINUATION_PROMPT,
  GENERATE_TREE_STRUCTURE_INITIAL_PROMPT,
)
from pdfindex.models import BoolModel, Page, TreeStructure, TreeStructureList

# TODO: Add TOC-found helpers used by pdf_index.index when toc_pages is non-empty:
#   - extract_toc_content(pages) → raw TOC text (or merge into check_page_for_toc)
#   - toc_to_structure(toc_text) → list[TreeStructure] via one direct LLM call
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


async def generate_toc_initial_structure(
  chunk_text: str, client: StructuredCompletionClient | None = None
) -> list[TreeStructure]:
  """Generate the tree structure found in the first chunk of a document.

  Args:
      chunk_text: Page-tagged text of the first chunk.
      client: Optional completion client override.

  Returns:
      Sections found in this chunk, in document order.

  """
  client: StructuredCompletionClient = client or create_completion_client()
  result: TreeStructureList = await client.complete(
    chunk_text,
    TreeStructureList,
    system_prompt=GENERATE_TREE_STRUCTURE_INITIAL_PROMPT,
  )
  return result.sections


async def generate_toc_continuation_structure(
  chunk_text: str,
  previous_structure: list[TreeStructure],
  client: StructuredCompletionClient | None = None,
) -> list[TreeStructure]:
  """Continue the tree structure into the next chunk, given what's been extracted so far.

  Args:
      chunk_text: Page-tagged text of the current chunk.
      previous_structure: Sections already extracted from earlier chunks.
      client: Optional completion client override.

  Returns:
      Only the new sections found in this chunk, in document order.

  """
  client: StructuredCompletionClient = client or create_completion_client()
  previous_structure_json: str = TreeStructureList(sections=previous_structure).model_dump_json(
    indent=2
  )
  prompt = (
    f'Previous tree structure:\n{previous_structure_json}\n\n'
    f'Current part of the document:\n{chunk_text}'
  )
  result: TreeStructureList = await client.complete(
    prompt,
    TreeStructureList,
    system_prompt=GENERATE_TREE_STRUCTURE_CONTINUATION_PROMPT,
  )
  return result.sections
