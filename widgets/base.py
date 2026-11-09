from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, NamedTuple


class Stat(NamedTuple):
  value: str
  unit: str
  label: str
  accent: bool = False      # drawn in the theme color


@dataclass
class Context:
  """Everything a widget may use, supplied by the host fork. Widgets import nothing from openpilot."""
  rl: Any                                              # raylib module (pyray API)
  font: Callable[[str], Any]                           # "bold" | "regular" -> rl.Font
  measure: Callable[[Any, str, float], tuple[float, float]]
  heading: Callable[[], float | None] = lambda: None   # degrees, 0 = north
  stats: Callable[[], list[Stat]] = list               # the drive so far
  accent: tuple[int, int, int] = (0x3E, 0x8C, 0xEB)
  extra: dict = field(default_factory=dict)


class Widget:
  name = ""      # stored in the host's selection param
  title = ""     # shown in the selector

  def preferred_h(self, w: int) -> int:
    return 240

  def min_h(self, w: int) -> int:
    return self.preferred_h(w)

  def draw(self, rect, ctx: Context) -> None:
    raise NotImplementedError
