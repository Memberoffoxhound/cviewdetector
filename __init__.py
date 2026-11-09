"""cviewdetector: CommaView second-screen widgets for openpilot forks. See README.md."""
from .detect import ViewerDetector, installed, viewer_connected
from .viewer import ALERT_PICK, ALERT_SWITCH, TEAL, Viewer

__all__ = ["ViewerDetector", "installed", "viewer_connected", "Viewer", "ALERT_PICK", "ALERT_SWITCH", "TEAL"]
