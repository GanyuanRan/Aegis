"""JSON settings loader (replacement for settings_ini)."""

import json
from pathlib import Path

JSON_PATH = Path(__file__).with_name("settings.json")


def load_section(section):
    with JSON_PATH.open(encoding="utf-8") as handle:
        return json.load(handle)[section]
