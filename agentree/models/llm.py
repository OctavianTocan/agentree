"""Schemas for LLM completion inputs and outputs."""

from typing import Any

from pydantic import BaseModel, Field

from agentree.models.base import StrictModel


class BoolModel(StrictModel):
  """A model that returns a boolean value.

  Example::

      {'value': true}
  """

  value: bool = Field(description='The boolean value.')


class ClaudeReply(BaseModel):
  """One Claude query's collected output.

  Example::

      {'text': '', 'structured_output': {'value': true}, 'cost_usd': 0.01, 'usage': None}
  """

  text: str = Field(description='Concatenated assistant text blocks.')
  structured_output: dict[str, Any] | None = Field(
    default=None, description='StructuredOutput tool input, set when the model used it.'
  )
  cost_usd: float | None = Field(
    default=None, description='Total query cost in USD reported by the SDK, if any.'
  )
  usage: dict[str, Any] | None = Field(
    default=None, description='Token usage the SDK attached to the terminal result, if any.'
  )
