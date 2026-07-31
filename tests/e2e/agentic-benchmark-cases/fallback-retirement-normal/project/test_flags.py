from pathlib import Path

from flags import canonical_flag
from menu import enabled


assert canonical_flag("navigation") == "navigation"
assert canonical_flag("nav_v1") == "nav_v1"
assert enabled({"navigation": True}, "navigation") is True
assert "nav_v1" not in Path("flags.py").read_text(encoding="utf-8")
