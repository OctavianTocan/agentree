import asyncio

import pytest

from agentree.completion import create_completion_client
from agentree.completion.claude import ClaudeCompletionClient
from agentree.completion.codex import CodexCompletionClient
from agentree.completion.disabled import DisabledCompletionClient
from agentree.config import settings
from agentree.models import BoolModel, Outline


def test_create_completion_client_defaults_to_claude(monkeypatch):
  monkeypatch.setattr(settings, 'completions_enabled', True)
  monkeypatch.setattr(settings, 'completion_client', 'claude')

  client = create_completion_client()

  assert isinstance(client, ClaudeCompletionClient)


def test_create_completion_client_selects_codex(monkeypatch):
  monkeypatch.setattr(settings, 'completions_enabled', True)

  client = create_completion_client('codex')

  assert isinstance(client, CodexCompletionClient)


def test_create_completion_client_rejects_unknown_provider(monkeypatch):
  monkeypatch.setattr(settings, 'completions_enabled', True)
  monkeypatch.setattr(settings, 'completion_client', 'bogus')

  with pytest.raises(ValueError, match='Invalid completion client'):
    create_completion_client()


def test_create_completion_client_returns_disabled_when_completions_off(monkeypatch):
  monkeypatch.setattr(settings, 'completions_enabled', False)

  client = create_completion_client('codex')

  assert isinstance(client, DisabledCompletionClient)


def test_disabled_completion_client_returns_empty_structured_responses():
  client = DisabledCompletionClient()

  bool_result = asyncio.run(client.complete('prompt', BoolModel, system_prompt='system'))
  sections_result = asyncio.run(client.complete('prompt', Outline, system_prompt='system'))

  assert bool_result == BoolModel(value=False)
  assert sections_result == Outline(sections=[])
