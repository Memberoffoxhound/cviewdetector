"""Widget library: a widget registers once and shows up in the host's selector."""
from __future__ import annotations

from .base import Context, Stat, Widget

_registry: dict[str, type[Widget]] = {}


def register(cls: type[Widget]) -> type[Widget]:
  assert cls.name and cls.name not in _registry, cls.name
  _registry[cls.name] = cls
  return cls


def names() -> list[str]:
  return list(_registry)


def title(name: str) -> str:
  return _registry[name].title


def resolve(name: str | None) -> str:
  """A known widget name; an unknown or empty one falls back to the first."""
  return name if name in _registry else next(iter(_registry))


def next_name(name: str | None) -> str:
  n = names()
  return n[(n.index(resolve(name)) + 1) % len(n)]


def create(name: str | None) -> Widget:
  return _registry[resolve(name)]()


from . import compass  # noqa: F401  registers the built-in widgets

__all__ = ["Context", "Stat", "Widget", "register", "names", "title", "resolve", "next_name", "create"]
