import asyncio

import pytest

from PDFindex.models import TreeStructure
from PDFindex.settings import settings
from PDFindex.toc_extraction import (
  generate_toc_continuation_structure,
  generate_toc_initial_structure,
)

requires_live_claude = pytest.mark.skipif(
  not settings.claude_code_oauth_token,
  reason='requires a live Claude Agent SDK OAuth token',
)

FIRST_CHUNK = """<physical_index_1>
TABLE OF CONTENTS
1. Overview .......... 3
2. Methods ........... 5
2.1 Data Collection ... 5
<physical_index_1>

<physical_index_2>
1. Overview
This report covers Q1 activity.
<physical_index_2>
"""

SECOND_CHUNK = """<physical_index_5>
2. Methods
This section describes our methods.
<physical_index_5>

<physical_index_6>
3. Results
This section describes our results.
<physical_index_6>
"""


@requires_live_claude
def test_generate_toc_initial_structure_finds_overview_section():
  sections = asyncio.run(generate_toc_initial_structure(FIRST_CHUNK))

  assert any(section.title.strip().lower() == 'overview' for section in sections)
  assert all(isinstance(section, TreeStructure) for section in sections)


@requires_live_claude
def test_generate_toc_continuation_structure_finds_new_section_not_in_previous():
  previous_structure = [
    TreeStructure(structure='1', title='Overview', physical_index='<physical_index_2>'),
    TreeStructure(structure='2', title='Methods', physical_index=None),
  ]

  new_sections = asyncio.run(generate_toc_continuation_structure(SECOND_CHUNK, previous_structure))

  assert any(section.title.strip().lower() == 'results' for section in new_sections)
