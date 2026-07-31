from adapters.partner_api import imported_id
from adapters.scanner import scanned_id


assert scanned_id(" 0007 ") == "0007"
assert imported_id({"tracking_id": "0007"}) == "0007"
