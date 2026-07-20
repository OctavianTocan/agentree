import asyncio

from agentree.completion import create_completion_client
from agentree.indexing.toc_extraction import (
  extract_outline_continuation,
  extract_outline_initial,
)
from agentree.models import OutlineSection
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
def test_extract_outline_initial_finds_overview_section() -> None:
  client = create_completion_client('claude')
  outline = asyncio.run(extract_outline_initial(FIRST_CHUNK, client=client))

  assert any(section.title.strip().lower() == 'overview' for section in outline.sections)
  assert all(isinstance(section, OutlineSection) for section in outline.sections)


@requires_live_claude
def test_extract_outline_continuation_finds_new_section_not_in_previous() -> None:
  client = create_completion_client('claude')
  spine = [
    OutlineSection(depth=0, title='Overview', physical_index=2),
    OutlineSection(depth=0, title='Methods', physical_index=5),
  ]

  new_outline = asyncio.run(extract_outline_continuation(SECOND_CHUNK, spine, client=client))

  assert any(section.title.strip().lower() == 'results' for section in new_outline.sections)
