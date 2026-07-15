"""Pure flat-outline → nested Tree assembly (no I/O, no LLM calls)."""

from agentree.models import FlatSection, Outline
from agentree.models.document import Document
from agentree.models.tree import Node

_MISSING_PHYSICAL_INDEX = 'Physical index is required for each section'


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
      raise ValueError(_MISSING_PHYSICAL_INDEX)
    # end = next section's start - 1; the last section runs to the final page.
    if i == len(sections) - 1:
      end_index: int = doc.last_page
    else:
      next_start = sections[i + 1].physical_index
      if next_start is None:
        raise ValueError(_MISSING_PHYSICAL_INDEX)
      end_index = next_start - 1

    flat_sections.append(
      FlatSection(
        depth=section.depth,
        title=section.title,
        start_index=section.physical_index,
        end_index=end_index,
      )
    )
  return flat_sections


def flat_sections_to_nodes(sections: list[FlatSection]) -> list[Node]:
  """Nest flat sections by depth.

  Args:
    sections: Flat sections in document order, each with a ``depth``.

  Returns:
    The root-level nodes, with deeper sections nested as children.

  """
  # Dummy root node.
  root = Node(title='', start_index=0, end_index=0)
  stack: list[Node] = [root]

  for section in sections:
    # We use min() to ensure that the depth is not greater than the length of the stack.
    deepest_parent_depth: int = len(stack) - 1
    depth: int = min(section.depth, deepest_parent_depth)

    # Create the node, and add it to the parent's children.
    node = Node(title=section.title, start_index=section.start_index, end_index=section.end_index)
    stack[depth].children.append(node)

    # Remove all parents that are deeper than the current depth. That way we don't have to traverse
    # the tree to find the parent.
    del stack[depth + 1 :]
    stack.append(node)

  return root.children


# TODO: How would this code know which sections need to be sent to the LLM? I don't understand
# that. Shouldn't we just use the outline that we pass to it, and maybe just grab its parents if
# it has them, and if not, then we just pass it the last same-depth section?
# def open_spine(sections: list[FlatSection]) -> list[FlatSection]:
#     """The chain of still-open ancestors: walk from the end, keep each section
#     whose level is strictly less than the last one we kept."""
#     spine: list[FlatSection] = []
#     need = None  # max level allowed for the next (shallower) ancestor
#     for s in reversed(sections):
#         if need is None or s.level < need:
#             spine.append(s)
#             need = s.level
#         if need == 0:
#             break
#     return list(reversed(spine))
