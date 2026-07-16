"""Pure flat-outline → nested Tree assembly (no I/O, no LLM calls)."""

from agentree.models import FlatSection, Outline, OutlineSection
from agentree.models.document import Document
from agentree.models.tree import Node

_MISSING_PHYSICAL_INDEX = 'Physical index is required for each section'


def outline_to_flat_sections(outline: Outline, doc: Document) -> list[FlatSection]:
  """Derive each section's page range over the flat outline.

  ``end_index`` is the next section's start minus one; the final section runs
  to ``doc.last_page``.

  Args:
    outline: Flat, draft outline whose sections carry a ``physical_index``.
    doc: Source document, used for ``last_page``.

  Returns:
    The same sections, in order, with page ranges resolved.

  Raises:
    ValueError: If any section is missing a ``physical_index`` — v1 has no
      page-offset recovery.

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


def open_spine(sections: list[OutlineSection]) -> list[OutlineSection]:
  """The chain of still-open ancestors — the rightmost path down the outline so far.

  Sent to the LLM as continuation context so it can place the next chunk's
  headings at the right depth, without re-sending the whole outline.

  Args:
    sections: Draft outline sections in document order, each with a ``depth``.

  Returns:
    The open ancestors from shallowest to deepest; closed branches dropped.

  Example::

      depth  section       pops                     stack after
      0      A             —                        [A]
      1        A.1         —                        [A, A.1]
      2          A.1.a     —                        [A, A.1, A.1.a]
      1        A.2         A.1.a (2>=1), A.1 (1>=1)  [A, A.2]
      2          A.2.a     —                        [A, A.2, A.2.a]

      open_spine([A, A.1, A.1.a, A.2, A.2.a]) -> [A, A.2, A.2.a]
  """
  stack: list[OutlineSection] = []
  for section in sections:
    while stack and stack[-1].depth >= section.depth:
      stack.pop()
    stack.append(section)
  return stack
