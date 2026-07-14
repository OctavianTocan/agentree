"""Pure flat-outline → nested Tree assembly (no I/O, no LLM calls)."""

from loguru import logger

from agentree.models import FlatSection, Outline
from agentree.models.document import Document
from agentree.models.tree import Node


def outline_to_flat_sections(outline: Outline, doc: Document) -> list[FlatSection]:
  """Derive each section's page range over the flat outline.

  ``end_index`` is the next section's start minus one; the final section runs
  to ``doc.last_page``. Raises ValueError on a missing ``physical_index`` — v1
  has no page-offset recovery.
  """
  flat_sections: list[FlatSection] = []
  sections = outline.sections
  for i, section in enumerate(sections):
    if section.physical_index is None:
      raise ValueError('Physical index is required for each section')
    # end = next section's start - 1; the last section runs to the final page.
    if i == len(sections) - 1:
      end_index: int = doc.last_page
    else:
      next_start = sections[i + 1].physical_index
      if next_start is None:
        raise ValueError('Physical index is required for each section')
      end_index = next_start - 1

    flat_sections.append(
      FlatSection(
        code=section.code,
        title=section.title,
        start_index=section.physical_index,
        end_index=end_index,
      )
    )
  return flat_sections


def flat_sections_to_nodes(flat_sections: list[FlatSection]) -> list[Node]:
  """Nest flat sections by dotted code ("1.1" under "1") and assign zero-padded ids."""
  nodes: list[Node] = []
  nodes_dict: dict[str, Node] = {}
  for i, flat_section in enumerate(flat_sections):
    code: str = flat_section.code
    node: Node = Node(
      title=flat_section.title,
      start_index=flat_section.start_index,
      end_index=flat_section.end_index,
      id=f'{i:04d}',
    )

    # Add the node to the dictionary.
    nodes_dict[code] = node

    # Find the parent.
    parent_code: str | None = '.'.join(code.split('.')[:-1]) if len(code.split('.')) > 1 else None

    # Add the node to the parent's children.
    if parent_code and parent_code in nodes_dict:
      nodes_dict[parent_code].children.append(node)
    else:
      # No parent, this is a root node.
      nodes.append(node)

    logger.debug(f'Node {i}: {node.model_dump_json(indent=2)}')

  return nodes
