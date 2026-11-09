from ..viewer import ALERT_PICK, ALERT_SWITCH, PICK_S, SWITCH_S, Viewer


class Det:
  active = False

  def update(self, now):
    return self.active


def run(v, t0, t1, enabled, dt=0.1):
  out, t = [], t0
  while t < t1:
    v.update(t, enabled)
    out.append((round(t, 1), v.alert, v.widget))
    t += dt
  return out


def test_enabled_alert_then_widget():
  d = Det()
  v = Viewer(d)
  v.update(0.0, True)
  assert v.alert is None and not v.widget
  d.active = True
  v.update(1.0, True)
  assert v.alert == ALERT_SWITCH and not v.widget
  v.update(1.0 + SWITCH_S, True)
  assert v.alert is None and v.widget
  d.active = False
  v.update(10.0, True)
  assert v.alert is None and not v.widget


def test_disabled_pick_once_per_session():
  d = Det()
  v = Viewer(d)
  d.active = True
  v.update(0.0, False)
  assert v.alert == ALERT_PICK and not v.widget
  v.update(PICK_S + 0.1, False)
  assert v.alert is None
  v.update(20.0, False)
  assert v.alert is None                     # same session: once
  d.active = False
  v.update(21.0, False)
  d.active = True
  v.update(22.0, False)
  assert v.alert == ALERT_PICK               # new session


def test_enable_while_watching():
  d = Det()
  v = Viewer(d)
  d.active = True
  v.update(0.0, False)
  v.update(5.0, True)
  assert v.alert == ALERT_SWITCH and not v.widget
  v.update(5.0 + SWITCH_S, True)
  assert v.widget
  v.update(9.0, False)
  assert v.alert is None and not v.widget
