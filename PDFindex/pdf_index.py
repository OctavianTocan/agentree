import math
import asyncio
import logging

from pypdf import PdfReader
from PDFindex.models import Page

logger: logging.Logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

MAX_TOKENS_PER_CHUNK = 20000


def index(pdf_path: str):
    """This function is used to index a PDF file."""

    # Extract the text and tokens from the PDF file.
    page_list = extract_text_and_tokens(pdf_path)

    logger.info({"total_page_number": len(page_list)})
    logger.info({"total_token": sum([page[1] for page in page_list])})

    process(page_list)

    #     structure = tree_parser(...)              # the tree you already understand
    # write_node_id(structure)                  # give every node an id: "0000", "0001", ...
    # add_node_text(structure, page_list)       # slice in each node's actual page text
    # generate_summaries_for_structure(structure) # one LLM call per node, summarizing its text
    # generate_doc_description(structure)       # one more LLM call, over the whole tree, for a doc-level blurb
    # format_structure(structure)               # reorder each node's keys for tidy output
    # return {doc_name, doc_description, structure}

    # async def page_index_builder():
    #     # TODO: Still needs implementing.
    #     structure = await build_document_node_tree(page_list)

    # return asyncio.run(page_index_builder())


def extract_text_and_tokens(pdf_path: str):
    """This function is used to extract the text and tokens from the PDF file."""
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


def count_tokens(text):
    """This function is used to count the tokens in the text."""
    return len(text) // 4


async def build_document_node_tree(page_list):
    # This builds the tree structure of the document.
    ...


def process(page_list, start_index=1):
    """This function is used to process the document without a table of contents."""
    pages: list[Page] = []
    for page_index in range(start_index, start_index + len(page_list)):
        # Add the physical index to the page text. This is used to identify the page in the document.
        page_text = f"<physical_index_{page_index}>\n{page_list[page_index-start_index][0]}\n<physical_index_{page_index}>\n\n"

        # Count the tokens in the page text.
        token_count = count_tokens(page_text)

        # Add the page to the pages list.
        pages.append(Page(content=page_text, tokens=token_count))

    # Chunk the pages into chunks with overlap between them.
    chunk_texts = chunk_pages_with_overlap(pages)
    logger.info(f"len(chunk_texts): {len(chunk_texts)}")


# TODO: Would love to use Pydantic here. That would be pretty cool.
def chunk_pages_with_overlap(pages: list[Page], overlap_page: int = 1) -> list[str]:
    """This function is used to chunk the pages into chunks with a small page overlap between chunks."""

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

        # If the current token count plus the page tokens is greater than the target, add the current chunk's pages to the list of chunks and start a new chunk's pages.
        if current_token_count + current_page_tokens > chunk_target:
            chunks.append("".join(current_chunk_pages))
            # TODO: Why are we doing this? What's the point of 'overlap_page', and why are we then setting the current chunk's pages to the pages from the overlap start to the current page? I don't understand the logic here.
            overlap_start = max(i - overlap_page, 0)
            # TODO: So, this is like marking an overlap from where we are, back to some 'overlap_page' page?
            current_chunk_pages = [page.content for page in pages[overlap_start:i]]
            # TODO: This also just adds the tokens from the overlap to our current token count?
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
