from PDFindex.models import Page
from PDFindex.pdf_index import MAX_TOKENS_PER_CHUNK, chunk_pages_with_overlap


def make_page(label: str, tokens: int) -> Page:
    return Page(content=f"<{label}>", tokens=tokens)


def test_single_chunk_when_everything_fits_under_budget():
    pages = [make_page("A", 100), make_page("B", 100), make_page("C", 100)]

    chunks = chunk_pages_with_overlap(pages)

    assert chunks == ["<A><B><C>"]


def test_splits_into_multiple_chunks_when_over_budget():
    # Each page is a third of the budget, so six of them need more than one chunk.
    page_tokens = MAX_TOKENS_PER_CHUNK // 3
    pages = [make_page(label, page_tokens) for label in "ABCDEF"]

    chunks = chunk_pages_with_overlap(pages)

    assert len(chunks) > 1
    for page in pages:
        assert any(page.content in chunk for chunk in chunks), f"{page.content} was dropped"


def test_consecutive_chunks_share_overlap_content():
    page_tokens = MAX_TOKENS_PER_CHUNK // 3
    pages = [make_page(label, page_tokens) for label in "ABCDEF"]

    chunks = chunk_pages_with_overlap(pages, overlap_page=1)

    assert len(chunks) > 1
    for previous_chunk, next_chunk in zip(chunks, chunks[1:]):
        shared = [page for page in pages if page.content in previous_chunk and page.content in next_chunk]
        assert shared, "consecutive chunks should share at least one overlapping page"


def test_oversized_single_page_is_not_dropped():
    # A page bigger than the whole budget on its own - not something to silently lose.
    huge = make_page("HUGE", MAX_TOKENS_PER_CHUNK * 2)
    pages = [make_page("A", 100), huge, make_page("B", 100)]

    chunks = chunk_pages_with_overlap(pages)

    assert any(huge.content in chunk for chunk in chunks)
