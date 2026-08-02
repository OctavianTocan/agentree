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

    The depth variable is a whole number giving how deeply the section is nested. A top-level section has depth 0, a subsection of it has depth 1, a subsection of that has depth 2, and so on. Base it on the visual hierarchy of the document, not on any numbering the document gives its own sections: a section labelled "1.2.1" is depth 2 only if it is visually nested two levels deep.

    For the title, you need to extract the original title from the text, only fix the space inconsistency.

    The provided text contains tags like <physical_index_X> and <physical_index_X> to indicate the start and end of page X.

    For the physical_index, you need to extract the physical index of the start of the section from the text, and set `physical_index` to the integer `X` (e.g `2`, not `<physical_index_2>`).

    For starts_at_top, set it to true only if the section's title is the very first content on its page. If any text from a previous section comes before the title on that page, set it to false. Do fuzzy matching and ignore spacing or line-break inconsistencies.

    Directly return the final JSON structure. Do not output anything else.
    You should NOT call any tools for this task."""

EXTRACT_OUTLINE_CONTINUATION_PROMPT = """
    You are an expert in extracting hierarchical tree structure.
    You are given a tree structure of the previous part and the text of the current part.
    Your task is to continue the tree structure from the previous part to include the current part.

    The depth variable is a whole number giving how deeply the section is nested. A top-level section has depth 0, a subsection of it has depth 1, a subsection of that has depth 2, and so on. Base it on the visual hierarchy of the document, not on any numbering the document gives its own sections: a section labelled "1.2.1" is depth 2 only if it is visually nested two levels deep.

    For the title, you need to extract the original title from the text, only fix the space inconsistency.

    The provided text contains tags like <physical_index_X> and <physical_index_X> to indicate the start and end of page X. \

    For the physical_index, you need to extract the physical index of the start of the section from the text, and set `physical_index` to the integer `X` (e.g `2`, not `<physical_index_2>`).

    For starts_at_top, set it to true only if the section's title is the very first content on its page. If any text from a previous section comes before the title on that page, set it to false. Do fuzzy matching and ignore spacing or line-break inconsistencies.

    Directly return only the additional sections found in the current part - do not repeat sections already present in the previous tree structure. Do not output anything else.
    You should NOT call any tools for this task."""

GENERATE_DOC_DESCRIPTION_PROMPT = """
    You are an expert in generating a one-line description of a document.

    You are given a tree structure of the document.
    Your task is to generate a one-line description of the document.

    Return the description. Do not output anything else.
    You should NOT call any tools for this task.
    """

GENERATE_NODE_SUMMARY_PROMPT = """
    You are an expert in generating a summary of a node.

    You are given a node of the document.
    Your task is to generate a summary of the node.

    Return the summary. Do not output anything else.
    You should NOT call any tools for this task.
    """
