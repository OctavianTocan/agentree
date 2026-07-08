"""Provider-agnostic contract for structured LLM completions."""

from typing import Protocol

from PDFindex.types.completion import ResponseModel


class StructuredCompletionClient(Protocol):
  """Client that completes a prompt and returns a validated Pydantic model."""

  async def complete(
    self,
    prompt: str,
    response_model: type[ResponseModel],
    *,
    system_prompt: str,
  ) -> ResponseModel:
    """Complete a prompt and return a response model.

    Args:
      prompt: User-turn text sent to the model.
      response_model: Pydantic model the reply must validate against.
      system_prompt: Task instructions for the model.

    Returns:
      A validated instance of `response_model`.

    """
    ...
