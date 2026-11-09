# cviewdetector

Second-screen widgets for openpilot forks. While someone is watching the device on [CommaView](https://commaview.com), the comma 4 screen can show a widget, like a compass with drive stats, instead of the camera. openpilot alerts still draw on top. It only draws on the screen; it never touches controls.

Pure Python. Nothing here imports openpilot or raylib; your fork passes those in. Contains no CommaView code.

## What's in it

| File | Does |
|---|---|
| `detect.py` | `installed()`: CommaView's folder, boot hook and daemon are on the device. `ViewerDetector`: a viewer is connected on ports 8200 to 8202, read from `/proc/net/tcp` once a second, on after 2 of 3 hits, off after 3 misses. |
| `viewer.py` | `Viewer`: shows a CommaView alert first, then the widget if widgets are on, or a one-time "pick widgets in settings" alert if they're off. |
| `widgets/` | `Widget` base, registry, and `Context` (what the host passes in). First widget: `compass`. |

Installed and connected are separate on purpose: installed unlocks the settings, connected runs the widgets.

## Porting

1. Add the submodule:
   ```
   git submodule add https://github.com/Memberoffoxhound/cviewdetector.git selfdrive/ui/cviewdetector
   ```
2. Hook it in three places:
   - **UI loop:** call `viewer.update(time.monotonic(), widgets_enabled)` every frame. Onroad, if `viewer.widget`, draw `widgets.create(name).draw(rect, ctx)` instead of the camera. If `viewer.alert`, draw it with your alert renderer in the `TEAL` gradient. Your own alerts always win.
   - **Settings:** a top-level CommaView entry. Show a short explainer the first time. Then, if `installed()`, show an enable toggle and a widget picker (`widgets.names()`, `widgets.next_name()`); otherwise show a warning with a QR code to https://commaview.com.
   - **Params:** one bool for widgets on, one string for the widget name, one bool for the explainer seen.
3. Build a `widgets.Context` with your raylib module, fonts, a text measure function, heading and drive stats.

TeslaPilot's glue is a working example: `selfdrive/ui/mici/onroad/commaview.py` and `selfdrive/ui/mici/layouts/settings/commaview.py` in [TeslaPilot](https://github.com/Memberoffoxhound/TeslaPilot/tree/Highland-Dev).

## Writing a widget

```python
from cviewdetector.widgets import Widget, register

@register
class Clock(Widget):
  name = title = "clock"
  def draw(self, rect, ctx):
    ctx.rl.draw_text_ex(ctx.font("bold"), "12:00", ctx.rl.Vector2(rect.x, rect.y), 80, 0, ctx.rl.WHITE)
```

Keep `draw` allocation-free; it runs every frame.

## Tests

```
python -m pytest cviewdetector/tests
```

MIT licensed. CommaView is its own project; this only checks whether it's installed and connected.
