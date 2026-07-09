"""Generic structured completion wrapper using the OpenAI Codex Agent SDK."""

import logging

from openai_codex import ApprovalMode, AsyncCodex, AsyncThread, Sandbox, TurnResult

from pdfindex.config import settings
from pdfindex.types.completion import ResponseModel

logger: logging.Logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


async def generate_structured_completion(
    prompt: str,
    response_model: type[ResponseModel],
    *,
    system_prompt: str,
) -> ResponseModel:
    """Run a one-shot query using Codex and validate the structured response against a schema.

    Args:
      prompt: The user-turn text sent to the model.
      response_model: Pydantic model class used to validate the JSON response.
      system_prompt: The system prompt to use.

    Returns:
      An instance of the validated response model.

    """
    async with AsyncCodex() as codex:
        thread: AsyncThread = await codex.thread_start(
            sandbox=Sandbox.read_only,
            model=settings.codex_model,
            approval_mode=ApprovalMode.deny_all,
            personality=settings.personality,
            base_instructions=system_prompt,
        )
        result: TurnResult = await thread.run(
            input=prompt,
            effort=settings.codex_reasoning_effort,
            output_schema=response_model.model_json_schema(),
        )
        logger.debug("Codex turn status: %s", result.status)
        if result.error is not None:
            logger.error("Codex error: %s", result.error)
        if result.final_response is None:
            raise RuntimeError("Codex returned empty response")
        try:
            parsed = response_model.model_validate_json(result.final_response)
        except Exception as e:
            logger.error("Validation error: %s", e)
            logger.debug("Codex final_response (raw):\n%s", result.final_response)
            raise e
        logger.debug("Codex final_response:\n%s", parsed.model_dump_json(indent=2))
        return parsed
