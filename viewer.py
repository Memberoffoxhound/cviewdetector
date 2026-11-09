"""What the screen shows while CommaView is being watched: a CommaView alert first, then a widget or the camera."""
from __future__ import annotations

from .detect import ViewerDetector

SWITCH_S = 2.5    # "switching to widgets" alert, then the widget
PICK_S = 3.5      # "pick widgets in settings" alert, once per viewer session

ALERT_SWITCH = ("CommaView detected", "Switching to widgets")
ALERT_PICK = ("CommaView detected", "Pick widgets in settings")

# CommaView teal, left to right (its logo gradient)
TEAL = ((0x1C, 0x9A, 0x8D), (0x5C, 0xE6, 0xD6))


class Viewer:
  """Call update() every frame. alert is (text1, text2) or None; widget is True when the widget owns the screen."""

  def __init__(self, detector: ViewerDetector | None = None):
    self.detector = detector or ViewerDetector()
    self.alert: tuple[str, str] | None = None
    self.widget = False
    self._active = False
    self._enabled = False
    self._since = 0.0
    self._picked = False      # pick alert shown this session

  def update(self, now: float, enabled: bool) -> None:
    active = self.detector.update(now)
    if active and (not self._active or (enabled and not self._enabled)):
      self._since = now       # viewer arrived, or widgets turned on while watching
    if not active:
      self._picked = False
    self._active, self._enabled = active, enabled

    self.alert, self.widget = None, False
    if not active:
      return
    dt = now - self._since
    if enabled:
      self.alert = ALERT_SWITCH if dt < SWITCH_S else None
      self.widget = dt >= SWITCH_S
    elif not self._picked:
      if dt < PICK_S:
        self.alert = ALERT_PICK
      else:
        self._picked = True
