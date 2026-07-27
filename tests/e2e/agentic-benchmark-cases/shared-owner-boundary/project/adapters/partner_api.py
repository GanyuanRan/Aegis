from core.keys import normalize_tracking_id


def imported_id(payload):
    return normalize_tracking_id(payload["tracking_id"])
