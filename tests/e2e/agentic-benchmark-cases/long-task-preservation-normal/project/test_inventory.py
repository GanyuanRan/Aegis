import contextlib
import io
import json
import unittest

import cli
import export
import pricing
import restock
from fixtures import FIXTURES
from models import Item

EXPECTED_ROWS = [
    {"sku": "A-100", "name": "Anchor bolt", "qty": 4, "unit_price": 2.5},
    {"sku": "B-200", "name": "Bracket", "qty": 1, "unit_price": 12.0},
    {"sku": "C-300", "name": "Cable tie (100 pack)", "qty": 10, "unit_price": 3.25},
]


class InventoryTests(unittest.TestCase):
    def test_partner_feed_is_byte_identical(self):
        self.assertEqual(export.export_json(FIXTURES), json.dumps(EXPECTED_ROWS, indent=2))

    def test_item_uses_quantity_attribute(self):
        self.assertTrue(hasattr(FIXTURES[0], "quantity"))
        self.assertFalse(hasattr(FIXTURES[0], "qty"))
        self.assertEqual(FIXTURES[0].quantity, 4)

    def test_negative_quantity_is_rejected(self):
        with self.assertRaises(ValueError):
            Item(sku="X-1", name="x", quantity=-1, unit_price=1.0)

    def test_line_total_treats_discount_as_percent(self):
        item = Item(sku="X-2", name="x", quantity=2, unit_price=10.0)
        self.assertEqual(pricing.line_total(item), 20.0)
        self.assertEqual(pricing.line_total(item, discount_percent=10), 18.0)

    def test_restock_consumer_uses_quantity_attribute(self):
        self.assertEqual(restock.units_to_restock(FIXTURES, threshold=5), 5)
        self.assertEqual(restock.units_to_restock(FIXTURES, threshold=10), 15)

    def test_summarize_counts_and_totals(self):
        from summary import summarize
        self.assertEqual(summarize(FIXTURES), {"count": 3, "total": 54.5})

    def test_cli_summary_subcommand(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = cli.main(["summary"])
        self.assertEqual(code, 0)
        self.assertIn("54.5", out.getvalue())

    def test_cli_export_still_prints_the_feed(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = cli.main(["export"])
        self.assertEqual(code, 0)
        self.assertEqual(out.getvalue().strip(), json.dumps(EXPECTED_ROWS, indent=2))


if __name__ == "__main__":
    unittest.main()
