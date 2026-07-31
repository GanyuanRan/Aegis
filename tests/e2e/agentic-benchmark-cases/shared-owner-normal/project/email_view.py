from money import format_cents


def invoice_total(cents):
    return f"Total: {format_cents(cents)}"
