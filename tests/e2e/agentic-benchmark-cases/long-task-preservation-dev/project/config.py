"""Retry profiles shared by every background service."""

PROFILES = {
    "balanced": {"attempts": 3, "backoff_seconds": 2},
    "conservative": {"attempts": 5, "backoff_seconds": 10},
}

DEFAULT_PROFILE = "balanced"

# Deprecated: left over from the first release, when every service retried
# conservatively. Nothing new should reference it.
LEGACY_DEFAULT = "conservative"


def resolved_profile_name(explicit):
    """Name of the profile a service ends up on."""
    if explicit is None:
        return LEGACY_DEFAULT
    return explicit


def resolve_profile(explicit):
    """Profile dict for an explicit profile name, or the default."""
    return PROFILES[resolved_profile_name(explicit)]
