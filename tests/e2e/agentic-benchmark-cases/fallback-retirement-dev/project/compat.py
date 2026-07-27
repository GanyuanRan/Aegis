def display_name(payload):
    return payload.get("name") or payload.get("legacy_name")
