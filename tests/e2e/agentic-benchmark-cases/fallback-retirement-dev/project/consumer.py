from compat import display_name


def greeting(payload):
    return f"Hello, {display_name(payload)}"
