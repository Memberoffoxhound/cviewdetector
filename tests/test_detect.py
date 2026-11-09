from .. import detect
from ..detect import ViewerDetector, installed, viewer_connected

HDR = "  sl  local_address rem_address   st tx_queue rx_queue tr tm->when retrnsmt   uid  timeout inode\n"


def row(local_port, remote="0A00002A", st="01"):
  return f"   0: 00000000:{local_port:04X} {remote}:D431 {st} 00000000:00000000 00:00000000 00000000     0        0 1\n"


def test_parse():
  assert viewer_connected(HDR + row(8200))
  assert viewer_connected(HDR + row(8202))
  assert not viewer_connected(HDR + row(8203))
  assert not viewer_connected(HDR + row(8201, st="0A"))            # LISTEN
  assert not viewer_connected(HDR + row(8201, remote="0100007F"))  # loopback
  tcp6 = HDR + "   0: 00000000000000000000000000000000:2009 0000000000000000FFFF00002A00000A:D431 01 0 0 0 0 0 0 1\n"
  assert viewer_connected(tcp6)
  assert not viewer_connected("")


def test_debounce_2_of_3_on_3_misses_off():
  seq = iter([False, True, False, True, True, False, False, False])
  d = ViewerDetector(read=lambda: HDR + (row(8200) if next(seq) else ""), interval=1.0)
  got = [d.update(float(t)) for t in range(8)]
  assert got == [False, False, False, True, True, True, True, False]


def test_sample_rate():
  calls = []
  d = ViewerDetector(read=lambda: calls.append(1) or "", interval=1.0)
  for i in range(30):
    d.update(i * 0.1)
  assert len(calls) == 3


def test_installed(tmp_path):
  assert not installed(str(tmp_path))
  (tmp_path / "commaview").mkdir()
  (tmp_path / "continue.sh").write_text("#!/bin/bash\n# commaview-hook\n")
  assert not installed(str(tmp_path))
  daemon = tmp_path / "commaview" / "commaviewd"
  daemon.write_text("")
  daemon.chmod(0o755)
  assert installed(str(tmp_path))
  (tmp_path / "continue.sh").write_text("#!/bin/bash\n")
  assert not installed(str(tmp_path))


def test_never_reads_live_streaming():
  import inspect
  assert "IsLiveStreaming" not in inspect.getsource(detect)
