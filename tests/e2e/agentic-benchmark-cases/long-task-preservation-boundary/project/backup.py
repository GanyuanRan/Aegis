"""Backup planning."""

from settings_ini import load_ini


def plan():
    backup = load_ini("backup")
    return {"target": backup["target"], "keep_last": int(backup["keep_last"])}
