"""Orchestrator and main entry points for indexing PDF documents."""

import asyncio
import math
from pathlib import Path

from loguru import logger
from pypdf import PdfReader

from agentree.config import settings
from agentree.indexing.toc_extraction import (
  check_page_for_toc,
  extract_outline_continuation,
  extract_outline_initial,
)
from agentree.models import Document, OutlineSection, OutlineSectionList, Page, PageChunk, Tree

# The maximum number of tokens per chunk.
MAX_TOKENS_PER_CHUNK = settings.max_tokens_per_chunk
# The number of pages to check for a table of contents.
TOP_CHECK_PAGE_NUM = settings.top_check_page_num


# TODO: Change return type to Tree (nested Node tree + doc_description), and
# also surface per-page text so storage / get_page_content can persist it.
# Today we only return a flat list[OutlineSection]; see TODO.md "Flat → nested Tree".
def index(pdf_path: str) -> list[OutlineSection]:
  """Index a PDF file with no table of contents into a flat list of sections.

  Args:
      pdf_path: Path to the PDF file to index.

  Returns:
      Sections found across the whole document, in document order.

  """
  outline: list[OutlineSection] = []
  doc = load_document(pdf_path)

  logger.bind(
    doc_name=doc.name,
    total_page_number=doc.last_page,
    total_token=sum(page.tokens for page in doc.pages),
  ).info('Loaded PDF document')

  # Check if the document has a table of contents.
  toc_pages: list[tuple[int, Page]] = find_toc_pages(doc.pages)

  # --- DOCUMENT INDEXING WITH TABLE OF CONTENTS --- #
  if toc_pages:
    logger.bind(toc_page_count=len(toc_pages)).debug('Found TOC pages')
    # TODO: TOC-found path (MISSION.md). Implement in toc_extraction.py + here:
    #   1. Extract TOC text from toc_pages (optionally merge with detect call).
    #   2. Ask the LLM for structured JSON directly (no toc_transformer loop).
    #   3. Map TOC entries → physical PDF page indices (simple mapping first;
    #      PageIndex offset/verify cascade is deferred — see TODO.md).
    #   4. Assign outline from that result, then fall through to
    #      flat→Tree assembly below (same as the no-TOC path).
    ...
  # --- DOCUMENT INDEXING WITHOUT TABLE OF CONTENTS --- #
  else:
    # Chunk the pages into chunks with overlap between them.
    chunk_pages: list[PageChunk] = chunk_pages_with_overlap(doc.pages)
    logger.bind(chunk_count=len(chunk_pages)).info('Chunked pages for indexing')

    outline = asyncio.run(extract_outline_initial(chunk_pages[0].content))
    logger.info(
      'initial_outline:\n{}',
      OutlineSectionList(sections=outline).model_dump_json(indent=2),
    )

    # Add all the continuation chunks to the outline.
    for chunk in chunk_pages[1:]:
      continuation = asyncio.run(extract_outline_continuation(chunk.content, outline))
      logger.info(
        'continuation_outline:\n{}',
        OutlineSectionList(sections=continuation).model_dump_json(indent=2),
      )
      outline.extend(continuation)

    # Assemble the nested Tree.
    # tree = assemble_tree(outline, doc)

  # TODO: After either branch, assemble Tree via assemble_tree(outline, doc)
  # (pure helpers in indexing/assemble.py — see TODO.md), generate
  # doc_description, and return Tree (+ doc.pages) instead of this flat list.
  return outline


def load_document(pdf_path: str | Path) -> Document:
  """Read a PDF, tag physical page indices, and return an immutable Document bag."""
  # TODO: Delegate to Document.load(pdf_path) once that factory exists
  # (TODO.md "Document.load factory"). This wrapper can then shrink to one
  # line or be deleted; call sites should prefer Document.load.
  path = Path(pdf_path)
  raw_pages = extract_text_and_tokens(path)
  pages = tag_physical_indices(raw_pages)
  return Document.from_pages(path, pages)


def find_toc_pages(pages: list[Page]) -> list[tuple[int, Page]]:
  """Find the pages that have a table of contents.

  Args:
      pages: The pages to check.

  Returns:
      A list of tuples of the page index and the page that has a table of contents.

  """
  toc_pages: list[tuple[int, Page]] = []
  last_page_had_toc: bool = False
  for page_index, page in enumerate(pages):
    # Keep going until we run out of pages or we find a page that
    # doesn't have a table of contents.
    if page_index >= TOP_CHECK_PAGE_NUM and not last_page_had_toc:
      break

    # TODO: We could probably optimize this by grabbing the toc content
    # in the same call as the check_page_for_toc call. That way we can
    # just return real content, which is kinda the point, basically.
    has_toc = asyncio.run(check_page_for_toc(page))
    last_page_had_toc = has_toc
    # If the page has a table of contents, add it to the list of pages
    # that have a table of contents.
    if has_toc:
      toc_pages.append((page_index, page))
    # If the page doesn't have a table of contents, we stop.
    else:
      break

  return toc_pages


def extract_text_and_tokens(pdf_path: str | Path) -> list[tuple[str, int]]:
  """Read every page of a PDF and estimate its token count.

  Args:
      pdf_path: Path to the PDF file to read.

  Returns:
      One (page_text, token_count) tuple per page, in page order.

  """
  path = Path(pdf_path)
  logger.bind(pdf_path=str(path)).info('Reading PDF')
  page_list = []
  reader = PdfReader(path)
  number_of_pages = len(reader.pages)

  # Add all pages to the page list.
  for page_num in range(number_of_pages):
    page = reader.pages[page_num]
    page_text = page.extract_text()
    # Approximate: ~4 characters per token.
    token_length = count_tokens(page_text)
    # Add the page text and token length to the page list.
    page_list.append((page_text, token_length))

  return page_list


def count_tokens(text: str) -> int:
  """Estimate a text's token count (roughly 4 characters per token)."""
  return len(text) // 4


# TODO: Split assembly into pure functions in agentree/indexing/assemble.py
# (see TODO.md):
#   1. outline_to_flat_sections(outline, *, last_page) -> list[FlatSection]
#      end = next.start - 1; last section → last_page; fail loud if
#      physical_index is None. No appear_start in v1. Unit-test fixtures only.
#   2. flat_sections_to_nodes(flat) -> list[Node]
#      nest by dotted structure; assign zero-padded node_id. Unit-test with
#      hand-built FlatSections.
#   3. assemble_tree below becomes a thin orchestrator:
#      flat = outline_to_flat_sections(...); nodes = flat_sections_to_nodes(...);
#      return Tree(doc_name=doc.name, structure=nodes)
# PageIndex refs: post_processing (ranges), list_to_tree, write_node_id.
# Then wire assemble_tree from index() (TODO.md "Wire assemble_tree + index()").
def assemble_tree(outline: list[OutlineSection], doc: Document) -> Tree:
  """Assemble a nested Tree from a flat draft outline and PDF Document facts.

  Uses ``doc.name`` for ``Tree.doc_name`` and ``doc.last_page`` for the final
  section's ``end_index``. Not yet implemented.
  """
  del outline, doc
  raise NotImplementedError('assemble_tree is not implemented yet')


# TODO: Keep this pure and module-level for unit tests (tests/test_process.py).
# Document.load / load_document should call it — do not fold tagging into a
# mutating Document method. May move to indexing/pdf_io.py with extract helpers.
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


# TODO: Would love to use Pydantic here. That would be pretty cool.
def chunk_pages_with_overlap(pages: list[Page], overlap_page: int = 1) -> list[PageChunk]:
  """Group pages into token-budgeted chunks, with a small page overlap between consecutive chunks.

  Args:
      pages: Page-tagged content to group, in document order.
      overlap_page: Number of trailing pages from one chunk to repeat at
          the start of the next, so a section header split across a chunk
          boundary isn't missed.

  Returns:
      Page chunks, each under `MAX_TOKENS_PER_CHUNK`.

  """
  # Calculate the total token count of the pages.
  total_token_count = sum([page.tokens for page in pages])

  # Merge all pages into one chunk if the total token count is less than the token budget.
  if total_token_count <= MAX_TOKENS_PER_CHUNK:
    page_text = ''.join([page.content for page in pages])
    return [PageChunk(content=page_text)]

  # Calculate the expected number of groups to split the pages into.
  expected_chunks_num = math.ceil(total_token_count / MAX_TOKENS_PER_CHUNK)

  # This is how much _new_ content each chunk should contain.
  even_split_tokens_per_chunk = math.ceil(total_token_count / expected_chunks_num)

  # Used to estimate how many tokens the overlap adds.
  avg_tokens_per_page = total_token_count / len(pages)
  # This is the estimated number of tokens to overlap between chunks.
  overlap_tokens_estimate = avg_tokens_per_page * overlap_page

  # This is the target number of tokens for each chunk.
  chunk_target = min(even_split_tokens_per_chunk + overlap_tokens_estimate, MAX_TOKENS_PER_CHUNK)
  logger.bind(
    expected_chunks_num=expected_chunks_num,
    even_split_tokens_per_chunk=even_split_tokens_per_chunk,
    avg_tokens_per_page=avg_tokens_per_page,
    overlap_tokens_estimate=overlap_tokens_estimate,
    chunk_target=chunk_target,
  ).debug('Computed chunk budget')

  # Initialize the list of chunks and the current chunk's pages.
  chunks: list[PageChunk] = []
  # TODO: This isn't named correctly. It's not a list of pages,
  # it's just the content that we will append to the chunk, which we will
  current_chunk_pages: list[str] = []
  current_token_count: int = 0

  # Iterate through the pages and add them to the current chunk's pages.
  for page_index, page in enumerate(pages):
    current_page_tokens: int = page.tokens
    current_page_contents: str = page.content

    if current_token_count + current_page_tokens > chunk_target:
      # We close out the current chunk now that this page would push it over budget.
      content = ''.join(current_chunk_pages)
      chunks.append(PageChunk(content=content))

      # Re-seed the next chunk with the last `overlap_page` pages of this one, so a
      # section header split across the chunk boundary still appears in both chunks.
      overlap_start = max(page_index - overlap_page, 0)
      current_chunk_pages = [page.content for page in pages[overlap_start:page_index]]
      current_token_count = sum([page.tokens for page in pages[overlap_start:page_index]])

    # Add the current page to the current chunk's pages.
    current_chunk_pages.append(current_page_contents)
    # Add the current page tokens to the current token count.
    current_token_count += current_page_tokens

  # Add the last group to the list of groups.
  if current_chunk_pages:
    chunks.append(PageChunk(content=''.join(current_chunk_pages)))

  logger.bind(chunk_count=len(chunks)).debug('Finished chunking pages')
  return chunks
