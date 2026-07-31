from email_view import invoice_total
from receipt_view import receipt_total


assert invoice_total(1230) == "Total: $12.30"
assert receipt_total(1230) == "$12.30"
