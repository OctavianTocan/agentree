"""Draft and ranged-flat outline schemas (pre-nesting)."""

from pydantic import BaseModel, Field

from agentree.models.base import StrictModel


class SectionRef(BaseModel):
  """Dotted code + title — shared by draft and ranged-flat stages."""

  code: str = Field(description='Dotted hierarchy code, e.g. "1", "1.1", "2".')
  title: str = Field(description='Section heading text.')


class OutlineSection(SectionRef, StrictModel):
  """One flat draft-outline row as extracted by the model (before ranges/nesting).

  Example::

      {'code': '1.1', 'title': 'Key Points', 'physical_index': 1}
  """

  physical_index: int | None = Field(
    default=None,
    description=(
      '1-indexed physical page number where this section starts, taken from the'
      '`<physical_index_N>` tags in the input text. null if it does not start in this chunk.'
    ),
  )


# TODO: Isn't this a model? This comes from the LLM, no?
class Outline(StrictModel):
  """Flat list of outline sections extracted from one chunk of the document.

  Example::

      {
        'sections': [
          {'code': '1', 'title': 'Results', 'physical_index': 1},
          {'code': '1.1', 'title': 'Key Points', 'physical_index': 1},
        ]
      }
  """

  sections: list[OutlineSection] = Field(
    description='One entry per section found in the given text.'
  )


class FlatSection(SectionRef):
  """Draft row after page ranges are derived; still flat (not nested).

  Not an LLM response schema — assembly-only. ``code`` is kept so nesting can
  find the parent (``"1.1"`` → ``"1"``).

  Example::

      {'code': '1', 'title': 'Results', 'start_index': 1, 'end_index': 1}
  """

  start_index: int = Field(description='First physical PDF page (1-indexed) this section spans.')
  end_index: int = Field(description='Last physical PDF page (1-indexed) this section spans.')
