"""Internal restock calculation for the warehouse view."""


def units_to_restock(items, threshold=5):
    """Return the units needed to bring every item up to ``threshold``."""
    return sum(max(threshold - item.qty, 0) for item in items)
