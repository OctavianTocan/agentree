import asyncio
import logging
import math

from pypdf import PdfReader

from PDFindex.models import Page, TreeStructure
from PDFindex.settings import settings
from PDFindex.toc_extraction import (
    generate_toc_continuation_structure,
    generate_toc_initial_structure,
)

logger: logging.Logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

MAX_TOKENS_PER_CHUNK = settings.max_tokens_per_chunk


def index(pdf_path: str) -> list[TreeStructure]:
    """Index a PDF file with no table of contents into a flat list of sections.

    Args:
        pdf_path: Path to the PDF file to index.

    Returns:
        Sections found across the whole document, in document order.
    """

    # Extract the text and tokens from the PDF file.
    page_list = extract_text_and_tokens(pdf_path)

    logger.info({"total_page_number": len(page_list)})
    logger.info({"total_token": sum([page[1] for page in page_list])})

    chunk_texts: list[str] = process(page_list)
    structure = asyncio.run(generate_toc_initial_structure(chunk_texts[0]))
    logger.info(f"initial_structure: {structure}")

    for chunk_text in chunk_texts[1:]:
        continuation_structure = asyncio.run(
            generate_toc_continuation_structure(chunk_text, structure)
        )
        logger.info(f"continuation_structure: {continuation_structure}")
        structure.extend(continuation_structure)

    return structure


def extract_text_and_tokens(pdf_path: str) -> list[tuple[str, int]]:
    """Read every page of a PDF and estimate its token count.

    Args:
        pdf_path: Path to the PDF file to read.

    Returns:
        One (page_text, token_count) tuple per page, in page order.
    """
    logger.info("Reading PDF: %s", pdf_path)
    page_list = []
    reader = PdfReader(pdf_path)
    number_of_pages = len(reader.pages)

    # Add all pages to the page list.
    for page_num in range(number_of_pages):
        page = reader.pages[page_num]
        page_text = page.extract_text()
        # Approximating the token length by dividing the page text length by 4, which is a rough estimate of the number of tokens in the page text.
        token_length = count_tokens(page_text)
        # Add the page text and token length to the page list.
        page_list.append((page_text, token_length))

    return page_list


def count_tokens(text: str) -> int:
    """Estimate a text's token count (roughly 4 characters per token)."""
    return len(text) // 4


async def build_document_node_tree(page_list):
    """Placeholder for building the final Node/Tree structure. Not yet implemented."""
    ...


def process(page_list: list[tuple[str, int]], start_index: int = 1) -> list[str]:
    """Tag each page with its physical index and split the document into overlapping chunks.

    Args:
        page_list: One (page_text, token_count) tuple per page, as returned by
            `extract_text_and_tokens`.
        start_index: Physical index (1-indexed) of the first page in `page_list`.

    Returns:
        Page-tagged chunk texts, each under the token budget.
    """
    pages: list[Page] = []
    for page_index in range(start_index, start_index + len(page_list)):
        # Add the physical index to the page text. This is used to identify the page in the document.
        page_text = f"<physical_index_{page_index}>\n{page_list[page_index-start_index][0]}\n<physical_index_{page_index}>\n\n"

        # Count the tokens in the page text.
        token_count = count_tokens(page_text)

        # Add the page to the pages list.
        pages.append(Page(content=page_text, tokens=token_count))

    # Chunk the pages into chunks with overlap between them.
    chunk_texts: list[str] = chunk_pages_with_overlap(pages)
    logger.info(f"len(chunk_texts): {len(chunk_texts)}")
    return chunk_texts


# TODO: Would love to use Pydantic here. That would be pretty cool.
def chunk_pages_with_overlap(pages: list[Page], overlap_page: int = 1) -> list[str]:
    """Group pages into token-budgeted chunks, with a small page overlap between consecutive chunks.

    Args:
        pages: Page-tagged content to group, in document order.
        overlap_page: Number of trailing pages from one chunk to repeat at
            the start of the next, so a section header split across a chunk
            boundary isn't missed.

    Returns:
        Concatenated chunk texts, each under `MAX_TOKENS_PER_CHUNK`.
    """

    # Calculate the total token count of the pages.
    total_token_count = sum([page.tokens for page in pages])

    # Merge all pages into one text if the total token count is less than the token budget.
    if total_token_count <= MAX_TOKENS_PER_CHUNK:
        page_text = "".join([page.content for page in pages])
        return [page_text]

    # Calculate the expected number of groups to split the pages into.
    expected_chunks_num = math.ceil(total_token_count / MAX_TOKENS_PER_CHUNK)
    logger.debug(f"expected_chunks_num: {expected_chunks_num}")

    # This is how much _new_ content each chunk should contain.
    even_split_tokens_per_chunk = math.ceil(total_token_count / expected_chunks_num)
    logger.debug(f"even_split_tokens_per_chunk: {even_split_tokens_per_chunk}")

    # This is the average number of tokens per page. This is used to estimate the number of tokens to overlap between chunks.
    avg_tokens_per_page = total_token_count / len(pages)
    logger.debug(f"avg_tokens_per_page: {avg_tokens_per_page}")
    # This is the estimated number of tokens to overlap between chunks.
    overlap_tokens_estimate = avg_tokens_per_page * overlap_page
    logger.debug(f"overlap_tokens_estimate: {overlap_tokens_estimate}")

    # This is the target number of tokens for each chunk.
    chunk_target = min(
        even_split_tokens_per_chunk + overlap_tokens_estimate, MAX_TOKENS_PER_CHUNK
    )
    logger.debug(f"chunk_target: {chunk_target}")

    # Initialize the list of chunks and the current chunk's pages.
    chunks: list[str] = []
    current_chunk_pages: list[str] = []
    current_token_count: int = 0

    # Iterate through the pages and add them to the current chunk's pages.
    for i, page in enumerate(pages):
        current_page_tokens: int = page.tokens
        current_page_contents: str = page.content

        if current_token_count + current_page_tokens > chunk_target:
            # Close out the current chunk now that this page would push it over budget.
            chunks.append("".join(current_chunk_pages))
            # Re-seed the next chunk with the last `overlap_page` pages of this one, so a
            # section header split across the chunk boundary still appears in both chunks.
            overlap_start = max(i - overlap_page, 0)
            current_chunk_pages = [page.content for page in pages[overlap_start:i]]
            current_token_count = sum([page.tokens for page in pages[overlap_start:i]])

        # Add the current page to the current chunk's pages.
        current_chunk_pages.append(current_page_contents)
        # Add the current page tokens to the current token count.
        current_token_count += current_page_tokens

    # Add the last group to the list of groups.
    if current_chunk_pages:
        chunks.append("".join(current_chunk_pages))

    logger.debug(f"len(chunks): {len(chunks)}")
    return chunks
