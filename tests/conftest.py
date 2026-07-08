import os

import pytest

from pdfindex.config import settings


def live_claude_tests_enabled() -> bool:
  """Return whether live Claude Agent SDK integration tests should run."""
  return (
    os.getenv('PDFINDEX_RUN_LIVE_TESTS') == '1' and settings.claude_code_oauth_token is not None
  )


requires_live_claude = pytest.mark.skipif(
  not live_claude_tests_enabled(),
  reason='live Claude tests require PDFINDEX_RUN_LIVE_TESTS=1 and an OAuth token',
)
