"""Loguru configuration for the agentree application."""

from __future__ import annotations

import sys
from typing import Any

from loguru import logger

CONSOLE_FORMAT = (
  '<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | '
  '<level>{level: <8}</level> | '
  '<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - '
  '<level>{message}</level>'
)

FILE_FORMAT = '{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}'


def _format_with_extra(base_format: str, *, colorize_extra: bool) -> Any:
  """Build a Loguru format callable that appends bound extras when present.

  Args:
    base_format: Format string without the optional extras suffix.
    colorize_extra: Whether to wrap extras in a dim markup tag (console only).

  Returns:
    A callable suitable for Loguru's `format=` sink argument.

  """

  def formatter(record: dict[str, Any]) -> str:
    if record['extra']:
      extra_part = ' | <dim>{extra}</dim>' if colorize_extra else ' | {extra}'
      return base_format + extra_part + '\n'
    return base_format + '\n'

  return formatter


def configure_logging(
  *,
  level: str = 'DEBUG',
  log_file: str = 'agentree.log',
) -> None:
  """Configure Loguru sinks for colored console output and a rotating file.

  Args:
    level: Minimum level for both sinks.
    log_file: Path for the plain-text file sink.

  """
  logger.remove()
  logger.add(
    sys.stderr,
    level=level,
    format=_format_with_extra(CONSOLE_FORMAT, colorize_extra=True),
    colorize=True,
    backtrace=True,
    diagnose=True,
  )
  logger.add(
    log_file,
    level=level,
    format=_format_with_extra(FILE_FORMAT, colorize_extra=False),
    rotation='10 MB',
    retention='14 days',
    enqueue=True,
    backtrace=True,
    diagnose=True,
  )
