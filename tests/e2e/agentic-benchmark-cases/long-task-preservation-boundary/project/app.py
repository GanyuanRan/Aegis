"""Application description."""

from settings_json import load_section


def describe():
    app = load_section("app")
    return f"{app['name']} ({app['timezone']}), keeps {app['retention_days']} days"
