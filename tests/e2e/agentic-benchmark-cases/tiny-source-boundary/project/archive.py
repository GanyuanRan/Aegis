def is_safe_archive_name(name):
    return isinstance(name, str) and not name.startswith("/")
