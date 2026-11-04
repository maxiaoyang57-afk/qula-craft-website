import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from pdp_public_copy import VERIFIED_SPECS, public_specs


class VerifiedProductSpecsTests(unittest.TestCase):
    def test_verified_fields_match_exact_sku_and_leave_import_intact(self):
        rows = json.loads((ROOT / "assets/data/pdp-data.json").read_text())
        keyed = {entry["sku"]: entry for entry in rows}
        for sku, reviewed in VERIFIED_SPECS.items():
            with self.subTest(sku=sku):
                raw = keyed[sku]
                saved = copy.deepcopy(raw)
                published = public_specs(raw)
                self.assertEqual({key: published[key] for key in reviewed}, reviewed)
                self.assertEqual(saved, raw)

    def test_jelly_bean_sizes_are_distinct(self):
        for sku, size in (("RW4252", "12 × 22 mm"), ("RW002854", "10 × 24 mm")):
            page = (ROOT / f"p-{sku.lower()}.html").read_text()
            self.assertIn(f"<b>Size</b></td><td>{size}</td>", page)
            self.assertIn("<b>Source packing</b></td><td>100 pieces per bag</td>", page)
        self.assertIn("12 × 22 mm", (ROOT / "guide-decoden-supplies.html").read_text())
