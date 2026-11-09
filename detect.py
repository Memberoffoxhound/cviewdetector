"""CommaView detection. Installed (dependencies present) and active (someone watching) are separate checks."""
from __future__ import annotations

import os
from collections import deque

PORTS = (8200, 8201, 8202)        # CommaView video ports: road, wide, driver
ESTABLISHED = "01"
LOOPBACK = ("0100007F", "00000000000000000000000001000000", "0000000000000000FFFF00000100007F")
TCP_TABLES = ("/proc/net/tcp", "/proc/net/tcp6")


def installed(root: str = "/data") -> bool:
  """CommaView's install: its folder, its boot hook in continue.sh and its daemon."""
  base = os.path.join(root, "commaview")
  try:
    with open(os.path.join(root, "continue.sh")) as f:
      hook = "# commaview-hook" in f.read()
  except OSError:
    return False
  return os.path.isdir(base) and hook and os.access(os.path.join(base, "commaviewd"), os.X_OK)


def viewer_connected(table: str, ports=PORTS) -> bool:
  """True if a /proc/net/tcp(6) table has a remote peer ESTABLISHED on one of ports."""
  for line in table.splitlines()[1:]:
    f = line.split()
    if len(f) < 4 or f[3] != ESTABLISHED:
      continue
    local, remote = f[1].split(":"), f[2].split(":")
    if int(local[1], 16) in ports and remote[0] not in LOOPBACK:
      return True
  return False


def _read_tables(paths=TCP_TABLES) -> str:
  out = []
  for p in paths:
    try:
      with open(p) as f:
        out.append(f.read())
    except OSError:
      pass
  return "".join(out)


class ViewerDetector:
  """Samples at most once per interval. On after 2 of the last 3 samples hit, off after 3 misses."""

  def __init__(self, read=_read_tables, interval: float = 1.0):
    self._read = read
    self._interval = interval
    self._samples: deque[bool] = deque(maxlen=3)
    self._t = -1e9
    self.active = False

  def update(self, now: float) -> bool:
    if now - self._t >= self._interval:
      self._t = now
      self._samples.append(viewer_connected(self._read()))
      hits = sum(self._samples)
      if hits >= 2:
        self.active = True
      elif hits == 0 and len(self._samples) == self._samples.maxlen:
        self.active = False
    return self.active
