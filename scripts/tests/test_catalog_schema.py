"""Regression tests: inquiry-only category lists must not invent offers."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from catalog_schema import catalog_list_item


class CatalogSchemaTests(unittest.TestCase):
    def test_links_without_product_or_offer(self):
        row = {"sku": "RW22372", "title": "Cookie cabochons", "titleFull": "Chocolate Chip Cookie Cabochons", "pdp": "p-rw22372.html", "image": "assets/images/pdp/rw22372/01.webp"}
        item = catalog_list_item(row, 12)
        self.assertEqual(item["@type"], "ListItem")
        self.assertEqual(item["position"], 12)
        self.assertEqual(item["name"], row["titleFull"])
        self.assertEqual(item["url"], "https://www.qulacrafts.com/p-rw22372.html")
        self.assertEqual(set(item), {"@type", "position", "name", "url", "image"})
        self.assertNotIn("offers", row)

    def test_short_title_fallback(self):
        item = catalog_list_item({"title": "Beads", "pdp": "p-beads.html", "image": "beads.webp"}, 1)
        self.assertEqual(item["name"], "Beads")


if __name__ == "__main__":
    unittest.main()
