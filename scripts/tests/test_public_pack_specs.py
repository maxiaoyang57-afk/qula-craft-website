"""Keep packing weights out of physical-size fields without inventing facts."""
import copy
import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from pdp_public_copy import public_specs


class PublicPackSpecsTests(unittest.TestCase):
    def test_packing_and_dimension_are_distinct(self):
        for captured, expected in (("500g/bag", "500 g/bag"), ("5g*100bag/Parcel", "5 g × 100bag/Parcel")):
            with self.subTest(captured=captured):
                entry = {"sku": "fixture", "specs": {"Size": captured, "Color": "Size"}}
                original = copy.deepcopy(entry)
                published = public_specs(entry)
                self.assertEqual(published, {"Reference packing": expected})
                self.assertEqual(entry, original)
        self.assertEqual(public_specs({"sku": "fixture", "specs": {"Size": "25*37mm", "Color": "Red"}}),
                         {"Size": "25 × 37 mm", "Color": "Red"})

    def test_ambiguous_size_and_existing_packing_are_preserved(self):
        for specs in ({"Size": "500g"}, {"Size": "Assorted"},
                      {"Size": "500g/bag", "Reference packing": "Confirm with quotation"}):
            with self.subTest(specs=specs):
                published = public_specs({"sku": "fixture", "specs": specs})
                self.assertIn("Size", published)
                if "Reference packing" in specs:
                    self.assertEqual(published["Reference packing"], specs["Reference packing"])

    def test_published_pages_use_packing_without_changing_the_value(self):
        for key, value in (("yx3531", "500 g/bag"), ("yx3400", "500 g/bag"), ("ma225", "5 g × 100bag/Parcel")):
            with self.subTest(key=key):
                html = (ROOT / f"p-{key}.html").read_text(encoding="utf-8")
                product = next(json.loads(s) for s in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)
                               if json.loads(s).get("@type") == "Product")
                self.assertNotIn("size", product)
                self.assertIn({"@type": "PropertyValue", "name": "Reference packing", "value": value}, product["additionalProperty"])
                self.assertIn(f"<b>Reference packing</b></td><td>{value}</td>", html)
        for key in ("yx3400", "ma225", "rx823", "czb26022", "cdk003767"):
            with self.subTest(key=key):
                html = (ROOT / f"p-{key}.html").read_text(encoding="utf-8")
                self.assertNotIn('<b>Color</b></td><td>Size</td>', html)
                self.assertNotRegex(html, r'"color"\s*:\s*"Size"')


if __name__ == "__main__":
    unittest.main()
