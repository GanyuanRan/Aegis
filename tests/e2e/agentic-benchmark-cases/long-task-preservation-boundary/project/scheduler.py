"""Nightly scheduler."""

from settings_ini import load_ini


def run_once():
    app = load_ini("app")
    return {"job": app["name"], "retention_days": int(app["retention_days"])}
