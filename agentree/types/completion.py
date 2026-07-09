"""Type variables shared across completion clients and SDK wrappers."""

from typing import TypeVar

from pydantic import BaseModel

ResponseModel = TypeVar('ResponseModel', bound=BaseModel)
"""Pydantic model type returned by structured completion calls."""
