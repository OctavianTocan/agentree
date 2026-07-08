import pytest

from pdfindex.completion import create_completion_client
from pdfindex.completion.claude import ClaudeCompletionClient
from pdfindex.completion.codex import CodexCompletionClient
from pdfindex.config import settings


def test_create_completion_client_defaults_to_claude(monkeypatch):
  monkeypatch.setattr(settings, 'completion_client', 'claude')

  client = create_completion_client()

  assert isinstance(client, ClaudeCompletionClient)


def test_create_completion_client_selects_codex():
  client = create_completion_client('codex')

  assert isinstance(client, CodexCompletionClient)


def test_create_completion_client_rejects_unknown_provider(monkeypatch):
  monkeypatch.setattr(settings, 'completion_client', 'bogus')

  with pytest.raises(ValueError, match='Invalid completion client'):
    create_completion_client()
