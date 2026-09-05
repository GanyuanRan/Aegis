"""Line pricing."""


def line_total(item, discount_percent=0):
    """Total for one line after a percentage discount."""
    return round(item.qty * item.unit_price * (1 - discount_percent), 2)
