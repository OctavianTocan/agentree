"""No-op completion client used when AI completions are disabled."""

from pdfindex.completion.protocol import StructuredCompletionClient
from pdfindex.models import BoolModel, TreeStructureList
from pdfindex.types.completion import ResponseModel


class DisabledCompletionClient(StructuredCompletionClient):
  """Returns empty structured responses without calling a model provider."""

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
    if response_model is TreeStructureList:
      return response_model(sections=[])
    raise TypeError(f'No disabled default for response model: {response_model!r}')
