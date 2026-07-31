ALIASES = {"nav_v1": "navigation"}


def canonical_flag(name):
    return ALIASES.get(name, name)
