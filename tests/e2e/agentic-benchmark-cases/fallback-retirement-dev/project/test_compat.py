from pathlib import Path

from compat import display_name
from consumer import greeting


assert display_name({"name": "Ada"}) == "Ada"
assert greeting({"name": "Lin"}) == "Hello, Lin"
assert "legacy_name" not in Path("compat.py").read_text(encoding="utf-8")
