"""No-op completion client used when AI completions are disabled."""

from typing import override

from agentree.completion.protocol import StructuredCompletionClient
from agentree.models import BoolModel, Outline
from agentree.types.completion import ResponseModel


class DisabledCompletionClient(StructuredCompletionClient):
  """Returns empty structured responses without calling a model provider."""

  @override
  async def complete(
    self,
    prompt: str,
    response_model: type[ResponseModel],
    *,
    system_prompt: str,
  ) -> ResponseModel:
    """Return an empty instance of `response_model` without calling a provider."""
    if response_model is BoolModel:
      return response_model(value=False)
    if response_model is Outline:
      return response_model(sections=[])
    msg = f'No disabled default for response model: {response_model!r}'
    raise TypeError(msg)
