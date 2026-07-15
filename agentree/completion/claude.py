"""Claude Agent SDK adapter for the structured completion protocol."""

import dataclasses
from typing import override

from agentree.completion.protocol import StructuredCompletionClient
from agentree.types.completion import ResponseModel


class ClaudeCompletionClient(StructuredCompletionClient):
  """Adapter that maps the shared API onto `completion.claude_sdk`."""

  @override
  async def complete(
    self,
    prompt: str,
    response_model: type[ResponseModel],
    *,
    system_prompt: str,
  ) -> ResponseModel:
    """Complete a prompt and return a response model."""
    from agentree.completion.claude_sdk import DEFAULT_OPTIONS, generate_structured_completion

    options = dataclasses.replace(DEFAULT_OPTIONS, system_prompt=system_prompt)

    return await generate_structured_completion(
      prompt=prompt,
      options=options,
      response_model=response_model,
    )
