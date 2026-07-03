"""Task-specific logic for extracting a document's tree structure without a table of contents."""

import dataclasses

from PDFindex.claude_client import DEFAULT_OPTIONS, generate_structured_completion
from PDFindex.models import TreeStructure, TreeStructureList
from PDFindex.prompts import (
    GENERATE_TREE_STRUCTURE_INITIAL_PROMPT,
    GENERATE_TREE_STRUCTURE_CONTINUATION_PROMPT,
)

INITIAL_OPTIONS = dataclasses.replace(
    DEFAULT_OPTIONS, system_prompt=GENERATE_TREE_STRUCTURE_INITIAL_PROMPT
)
CONTINUATION_OPTIONS = dataclasses.replace(
    DEFAULT_OPTIONS, system_prompt=GENERATE_TREE_STRUCTURE_CONTINUATION_PROMPT
)


async def generate_toc_initial_structure(chunk_text: str) -> list[TreeStructure]:
    """Generate the tree structure found in the first chunk of a document.

    Args:
        chunk_text: Page-tagged text of the first chunk.

    Returns:
        Sections found in this chunk, in document order.
    """
    result = await generate_structured_completion(
        chunk_text, INITIAL_OPTIONS, TreeStructureList
    )
    return result.sections


async def generate_toc_continuation_structure(
    chunk_text: str, previous_structure: list[TreeStructure]
) -> list[TreeStructure]:
    """Continue the tree structure into the next chunk, given what's been extracted so far.

    Args:
        chunk_text: Page-tagged text of the current chunk.
        previous_structure: Sections already extracted from earlier chunks.

    Returns:
        Only the new sections found in this chunk, in document order.
    """
    previous_structure_json = TreeStructureList(
        sections=previous_structure
    ).model_dump_json(indent=2)
    prompt = (
        f"Previous tree structure:\n{previous_structure_json}\n\n"
        f"Current part of the document:\n{chunk_text}"
    )
    result = await generate_structured_completion(
        prompt, CONTINUATION_OPTIONS, TreeStructureList
    )
    return result.sections
