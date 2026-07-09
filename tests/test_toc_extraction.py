import asyncio

from agentree.completion import create_completion_client
from agentree.indexing.toc_extraction import (
  generate_toc_continuation_structure,
  generate_toc_initial_structure,
)
from agentree.models import TreeStructure
from tests.conftest import requires_live_claude

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
  client = create_completion_client('claude')
  sections = asyncio.run(generate_toc_initial_structure(FIRST_CHUNK, client=client))

  assert any(section.title.strip().lower() == 'overview' for section in sections)
  assert all(isinstance(section, TreeStructure) for section in sections)


@requires_live_claude
def test_generate_toc_continuation_structure_finds_new_section_not_in_previous():
  client = create_completion_client('claude')
  previous_structure = [
    TreeStructure(structure='1', title='Overview', physical_index='<physical_index_2>'),
    TreeStructure(structure='2', title='Methods', physical_index=None),
  ]

  new_sections = asyncio.run(
    generate_toc_continuation_structure(SECOND_CHUNK, previous_structure, client=client)
  )

  assert any(section.title.strip().lower() == 'results' for section in new_sections)
