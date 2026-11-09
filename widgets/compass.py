"""Flat tape compass: drive stats on top, cardinals biggest at the center and shrinking toward the sides."""
from __future__ import annotations

import math

from . import register
from .base import Context, Widget

CARDINALS = {0: "N", 45: "NE", 90: "E", 135: "SE", 180: "S", 225: "SW", 270: "W", 315: "NW"}
STATS_H = 64          # stats row at the top
SPAN = 80.0           # marks fade out this far from the center
WHITE = (255, 255, 255)
GREY = (255, 255, 255, 140)


def marks(heading: float):
  """(lon, deg) for every 15 deg mark in view; lon is -SPAN..SPAN from the center."""
  for deg in range(0, 360, 15):
    lon = (deg - heading + 180.0) % 360.0 - 180.0
    if abs(lon) < SPAN:
      yield lon, deg


@register
class Compass(Widget):
  name = "compass"
  title = "compass"

  def __init__(self):
    self._heading: float | None = None

  def _smooth(self, deg: float | None) -> float | None:
    if deg is None:
      return self._heading
    if self._heading is None:
      self._heading = deg % 360.0
    else:
      self._heading = (self._heading + 0.2 * ((deg - self._heading + 180.0) % 360.0 - 180.0)) % 360.0
    return self._heading

  def draw(self, rect, ctx: Context) -> None:
    rl = ctx.rl
    rl.draw_rectangle_rec(rect, rl.BLACK)
    self._draw_stats(rect, ctx)
    heading = self._smooth(ctx.heading())
    if heading is None:
      return

    bold, regular = ctx.font("bold"), ctx.font("regular")
    cx, half = rect.x + rect.width / 2, rect.width / 2 - 24
    line_y = rect.y + STATS_H + (rect.height - STATS_H) * 0.42
    rl.begin_scissor_mode(int(rect.x), int(rect.y + STATS_H + 4), int(rect.width), int(rect.height - STATS_H - 4))
    rl.draw_line_ex(rl.Vector2(rect.x + 12, line_y), rl.Vector2(rect.x + rect.width - 12, line_y), 1, rl.Color(255, 255, 255, 50))
    for lon, deg in marks(heading):
      s = math.cos(math.radians(lon))                      # 1 at the center, 0 at the edges
      x = cx + half * math.sin(math.radians(lon)) / math.sin(math.radians(SPAN))
      a = int(255 * min(1.0, 0.25 + s))
      if deg in CARDINALS:
        txt, size = CARDINALS[deg], 30 + 46 * s ** 2
        w, h = ctx.measure(bold, txt, size)
        rl.draw_text_ex(bold, txt, rl.Vector2(x - w / 2, line_y - h * 0.62), size, 0, rl.Color(255, 255, 255, a))
      elif deg % 30 == 0:
        txt, size = str(deg), 16 + 18 * s
        w, h = ctx.measure(regular, txt, size)
        rl.draw_line_ex(rl.Vector2(x, line_y + 26), rl.Vector2(x, line_y + 26 + 4 + 6 * s), 2, rl.Color(255, 255, 255, a))
        rl.draw_text_ex(regular, txt, rl.Vector2(x - w / 2, line_y + 36 + 6 * s), size, 0, rl.Color(255, 255, 255, a))
      else:
        rl.draw_line_ex(rl.Vector2(x, line_y + 34), rl.Vector2(x, line_y + 34 + 6 * s), 2, rl.Color(255, 255, 255, a // 2))
    rl.end_scissor_mode()

  @staticmethod
  def _draw_stats(rect, ctx: Context) -> None:
    stats = ctx.stats()
    if not stats:
      return
    rl, bold, regular = ctx.rl, ctx.font("bold"), ctx.font("regular")
    slot = rect.width / len(stats)
    for i, st in enumerate(stats):
      vw, vh = ctx.measure(bold, st.value, 40)
      uw, _ = ctx.measure(bold, st.unit, 22) if st.unit else (0, 0)
      gap = 4 if st.unit else 0
      x = rect.x + slot * i + (slot - vw - gap - uw) / 2
      color = rl.Color(*ctx.accent, 255) if st.accent else rl.Color(*WHITE, 255)
      rl.draw_text_ex(bold, st.value, rl.Vector2(x, rect.y + 2), 40, 0, color)
      if st.unit:
        rl.draw_text_ex(bold, st.unit, rl.Vector2(x + vw + gap, rect.y + 2 + vh - 30), 22, 0, rl.Color(*WHITE, 255))
      lw, _ = ctx.measure(regular, st.label, 22)
      rl.draw_text_ex(regular, st.label, rl.Vector2(rect.x + slot * i + (slot - lw) / 2, rect.y + 38), 22, 0, rl.Color(*GREY))
