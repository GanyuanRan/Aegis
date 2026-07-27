from flags import canonical_flag


def enabled(flags, name):
    return bool(flags.get(canonical_flag(name), False))
