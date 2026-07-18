"""Draft and ranged-flat outline schemas (pre-nesting)."""

from pydantic import BaseModel, Field

from agentree.models.base import StrictModel


class SectionRef(BaseModel):
  """Depth + title — shared by draft and ranged-flat stages."""

  depth: int = Field(
    description=(
      'How deeply the section is nested: 0 for a top-level section, 1 for a subsection of '
      'one, 2 for a subsection of that, and so on. Base it on the visual hierarchy, not on '
      "the document's own numbering."
    )
  )
  title: str = Field(description='Section heading text.')


class OutlineSection(SectionRef, StrictModel):
  """One flat draft-outline row as extracted by the model (before ranges/nesting).

  Example::

      {'depth': 1, 'title': 'Key Points', 'physical_index': 1}
  """

  physical_index: int = Field(
    default=1,
    description=(
      '1-indexed physical page number where this section starts, taken from the'
      '`<physical_index_N>` tags in the input text.'
    ),
  )


# TODO: Isn't this a model? This comes from the LLM, no?
class Outline(StrictModel):
  """Flat list of outline sections extracted from one chunk of the document.

  Example::

      {
        'sections': [
          {'depth': 0, 'title': 'Results', 'physical_index': 1},
          {'depth': 1, 'title': 'Key Points', 'physical_index': 1},
        ]
      }
  """

  sections: list[OutlineSection] = Field(
    description='One entry per section found in the given text.'
  )


class FlatSection(SectionRef):
  """Draft row after page ranges are derived; still flat (not nested).

  Not an LLM response schema — assembly-only. ``depth`` is kept so nesting can
  find the parent (``0`` → ``1``).

  Example::

      {'depth': 0, 'title': 'Results', 'start_index': 1, 'end_index': 1}
  """

  start_index: int = Field(description='First physical PDF page (1-indexed) this section spans.')
  end_index: int = Field(description='Last physical PDF page (1-indexed) this section spans.')
