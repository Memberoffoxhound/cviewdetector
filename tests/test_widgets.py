from types import SimpleNamespace as NS

from .. import widgets
from ..widgets import Context, Stat
from ..widgets.compass import SPAN, marks


def test_registry():
  assert widgets.names()[0] == "compass"
  assert widgets.resolve("nope") == "compass" and widgets.resolve(None) == "compass"
  assert widgets.next_name("compass") in widgets.names()
  assert widgets.title("compass") == "compass"
  w = widgets.create("compass")
  assert w.min_h(536) <= w.preferred_h(536) <= 240


def test_marks():
  m = {deg: lon for lon, deg in marks(270.0)}
  assert m[270] == 0 and m[225] == -45 and m[315] == 45
  assert 90 not in m and all(abs(lon) < SPAN for lon in m.values())
  assert {d: lon for lon, d in marks(350.0)}[0] == 10


class FakeRL:
  """Records draw calls; enough of the pyray API for the compass."""
  BLACK = "black"

  def __init__(self):
    self.calls = []

  def __getattr__(self, name):
    if name[0].isupper():
      return lambda *a: a
    return lambda *a: self.calls.append((name, a))


def ctx(rl, heading=270.0):
  return Context(rl=rl, font=lambda w: w, measure=lambda f, t, s: (len(t) * s * 0.6, s),
                 heading=lambda: heading,
                 stats=lambda: [Stat("6.7", "mi", "driven"), Stat("80%", "", "engaged", True), Stat("8:39", "", "time"),
                                Stat("2.3", "mi", "streak")])


def test_compass_draws_inside_rect():
  rl = FakeRL()
  rect = NS(x=0, y=0, width=536, height=240)
  widgets.create("compass").draw(rect, ctx(rl))
  texts = [a[1] for n, a in rl.calls if n == "draw_text_ex"]
  assert {"6.7", "80%", "8:39", "2.3", "engaged", "streak", "W", "SW", "NW", "240", "300"} <= set(texts)
  for n, a in rl.calls:
    if n == "draw_text_ex":
      pos = a[2]
      assert 0 <= pos[1] < 240, (a[1], pos)


def test_compass_without_heading_draws_stats_only():
  rl = FakeRL()
  widgets.create("compass").draw(NS(x=0, y=0, width=536, height=240), ctx(rl, heading=None))
  texts = [a[1] for n, a in rl.calls if n == "draw_text_ex"]
  assert "W" not in texts and "driven" in texts
