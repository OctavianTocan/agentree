"""Node-level document content schemas."""

from pydantic import Field

from agentree.models.base import StrictModel


class NodeSummary(StrictModel):
  r"""One summary of a node.

  Example::

      {'summary': 'This is a summary of the node.'}
  """

  summary: str = Field(description='Summary of the node.')
