"""Pure flat-outline → nested Tree assembly (no I/O, no LLM calls)."""

import re

from loguru import logger

from agentree.models import FlatSection, Outline, OutlineSection
from agentree.models.document import Document
from agentree.models.tree import Node

_NODE_ID_WIDTH = 4
_PHYSICAL_INDEX_TAG = re.compile(r'<physical_index_\d+>')


def outline_to_flat_sections(outline: Outline, doc: Document) -> list[FlatSection]:
  """Derive each section's page range over the flat outline.

  A section ends just before the next section's start page — unless that page
  does not open with the next heading, in which case the two share the page and
  this section's range extends onto it. The final section runs to
  ``doc.last_page``.

  Args:
    outline: Flat, draft outline whose sections carry a ``physical_index``.
    doc: Source document, used for page text and ``last_page``.

  Returns:
    The same sections, in order, with page ranges resolved.

  """
  flat_sections: list[FlatSection] = []
  sections = outline.sections
  last = len(sections) - 1
  for i, section in enumerate(sections):
    if i == last:
      end_index = doc.last_page
    else:
      nxt: OutlineSection = sections[i + 1]
      clean_break = _appears_at_page_start(nxt.title, doc.pages[nxt.physical_index - 1].content)
      end_index = nxt.physical_index - 1 if clean_break else nxt.physical_index
      end_index = max(section.physical_index, end_index)

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


def assign_node_ids(nodes: list[Node]) -> None:
  """Number the tree with zero-padded ids in depth-first document order.

  Ids ('0000', '0001', …) are walked pre-order, so a parent's id precedes its
  children's. Each node is mutated in place.

  Args:
    nodes: Root nodes to number, in document order.

  """
  # Explicit stack of the not-yet-numbered frontier, kept in document order:
  # the next node to number is always on top, its children pushed reversed.
  frontier: list[Node] = list(reversed(nodes))
  next_id = 0
  while frontier:
    node = frontier.pop()
    node.id = str(next_id).zfill(_NODE_ID_WIDTH)
    next_id += 1
    frontier.extend(reversed(node.children))


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


def _appears_at_page_start(title: str, page_text: str, window: int = 200) -> bool:
  head = _normalize(page_text[:window])
  logger.debug('appears_at_page_start head={!r} title={!r}', head, title)
  return _normalize(title) in head


def _normalize(text: str) -> str:
  untagged = _PHYSICAL_INDEX_TAG.sub(' ', text)
  return ' '.join(untagged.casefold().split())
