"""JSON feed consumed by the partner. Field names and order are part of the contract."""

import json


def export_json(items):
    rows = [
        {"sku": item.sku, "name": item.name, "qty": item.qty, "unit_price": item.unit_price}
        for item in items
    ]
    return json.dumps(rows, indent=2)
