"""Tiny structured-output helpers for LLM completions."""

from pydantic import Field

from agentree.models.base import StrictModel


class BoolModel(StrictModel):
  """A model that returns a boolean value.

  Example::

      {'value': true}
  """

  value: bool = Field(description='The boolean value.')
