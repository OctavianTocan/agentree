"""Codex adapter for the structured completion protocol."""

from typing import override

from agentree.completion.protocol import StructuredCompletionClient
from agentree.types.completion import ResponseModel


class CodexCompletionClient(StructuredCompletionClient):
  """Adapter that maps the shared API onto `completion.codex_sdk`."""

  @override
  async def complete(
    self,
    prompt: str,
    response_model: type[ResponseModel],
    *,
    system_prompt: str,
  ) -> ResponseModel:
    """Complete a prompt and return a response model.

    Returns:
      A validated instance of `response_model`.

    """
    from agentree.completion.codex_sdk import generate_structured_completion

    return await generate_structured_completion(
      prompt=prompt,
      response_model=response_model,
      system_prompt=system_prompt,
    )
