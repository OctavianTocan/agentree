"""System prompts for no-TOC outline extraction."""

# TODO: Add prompts for the TOC-found path and doc_description:
#   - EXTRACT_TOC_CONTENT / TOC_TO_STRUCTURE (direct JSON; no continuation loop)
#   - GENERATE_DOC_DESCRIPTION (one-liner over the text-stripped tree)
# Optionally enrich CHECK_PAGE_FOR_TOC_PROMPT to return TOC text when present
# so detect+extract can be a single call (see find_toc_pages TODO).

CHECK_PAGE_FOR_TOC_PROMPT = """
    You are an expert in checking if a page has a table of contents.

    You are given a page of text. Your task is to check if the page has a table of contents.

    Return True if the page has a table of contents, False otherwise. Do not output anything else.
    You should NOT call any tools for this task.
    """

EXTRACT_OUTLINE_INITIAL_PROMPT = """
    You are an expert in extracting hierarchical tree structure, your task is to generate the tree structure of the document.

    The depth variable is the numeric system which represents the index of the hierarchy section in the table of contents. For example, the first section has depth 1, the first subsection has depth 1.1, the second subsection has depth 1.2, etc.

    For the title, you need to extract the original title from the text, only fix the space inconsistency.

    The provided text contains tags like <physical_index_X> and <physical_index_X> to indicate the start and end of page X.

    For the physical_index, you need to extract the physical index of the start of the section from the text, and set `physical_index` to the integer `X` (e.g `2`, not `<physical_index_2>`).

    Directly return the final JSON structure. Do not output anything else.
    You should NOT call any tools for this task."""

EXTRACT_OUTLINE_CONTINUATION_PROMPT = """
    You are an expert in extracting hierarchical tree structure.
    You are given a tree structure of the previous part and the text of the current part.
    Your task is to continue the tree structure from the previous part to include the current part.

    The depth variable is the numeric system which represents the index of the hierarchy section in the table of contents. For example, the first section has depth 1, the first subsection has depth 1.1, the second subsection has depth 1.2, etc.

    For the title, you need to extract the original title from the text, only fix the space inconsistency.

    The provided text contains tags like <physical_index_X> and <physical_index_X> to indicate the start and end of page X. \

    For the physical_index, you need to extract the physical index of the start of the section from the text, and set `physical_index` to the integer `X` (e.g `2`, not `<physical_index_2>`).

    Directly return only the additional sections found in the current part - do not repeat sections already present in the previous tree structure. Do not output anything else.
    You should NOT call any tools for this task."""
