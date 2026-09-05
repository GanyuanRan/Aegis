"""Service registry. A service may pin a retry profile explicitly."""

from config import LEGACY_DEFAULT

SERVICES = {
    "billing": {"profile": LEGACY_DEFAULT, "owner": "payments"},
    "search": {"profile": None, "owner": "platform"},
    "reports": {"profile": None, "owner": "analytics"},
}
