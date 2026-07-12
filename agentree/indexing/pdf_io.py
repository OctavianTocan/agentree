"""PDF extraction and tagging utilities."""

from pathlib import Path

from loguru import logger
from pypdf import PageObject, PdfReader

from agentree.models.pages import Page

TOKENS_PER_CHARACTER: int = 4


def extract_text_and_tokens(pdf_path: str | Path) -> list[tuple[str, int]]:
  """Read every page of a PDF and estimate its token count.

  Args:
      pdf_path: Path to the PDF file to read.

  Returns:
      One (page_text, token_count) tuple per page, in page order.

  """
  path = Path(pdf_path)
  logger.bind(pdf_path=str(path)).info('Reading PDF')
  page_list: list[tuple[str, int]] = []
  reader = PdfReader(path)
  number_of_pages = len(reader.pages)

  # Add all pages to the page list.
  for page_num in range(number_of_pages):
    page: PageObject = reader.pages[page_num]
    page_text: str = page.extract_text()
    # Approximate: ~4 characters per token.
    token_length: int = count_tokens(page_text)
    # Add the page text and token length to the page list.
    page_list.append((page_text, token_length))

  return page_list


def tag_physical_indices(raw_pages: list[tuple[str, int]], start_index: int = 1) -> list[Page]:
  """Tag each page with its physical index and return tagged Page objects.

  Args:
      raw_pages: Untagged `(page_text, token_count)` tuples from PDF extraction.
      start_index: Physical index (1-indexed) of the first page in `raw_pages`.

  Returns:
      Pages whose `content` includes `<physical_index_N>` markers.

  """
  tagged_pages: list[Page] = []
  for page_index in range(start_index, start_index + len(raw_pages)):
    raw_text, _token_count = raw_pages[page_index - start_index]
    page_text = f'<physical_index_{page_index}>\n{raw_text}\n<physical_index_{page_index}>\n\n'

    token_count = count_tokens(page_text)
    tagged_pages.append(Page(content=page_text, tokens=token_count))

  return tagged_pages


def count_tokens(text: str) -> int:
  """Estimate a text's token count (roughly 4 characters per token).

  Args:
      text: The text to estimate the token count of.

  Returns:
      The estimated token count of the text.

  """
  return len(text) // TOKENS_PER_CHARACTER
