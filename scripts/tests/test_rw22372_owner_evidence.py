"""Guard the distinction between packing, conditional MOQ and measured evidence."""
import hashlib
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from pdp_public_copy import public_specs


class CookieEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.entry = next(p for p in json.loads((ROOT / "assets/data/pdp-data.json").read_text()) if p["sku"] == "RW22372")
        self.record = json.loads((ROOT / "docs/rw22372-owner-evidence-20261107.json").read_text())

    def test_bag_count_does_not_become_an_unconditional_stock_or_moq_claim(self):
        facts = public_specs(self.entry)
        self.assertEqual(facts["Standard pack"], "100 pieces per bag")
        self.assertIn("1 bag when in stock; 10 bags when not in stock", self.entry["moq"])
        self.assertIn("Random mixed designs and colors", facts["Assortment"])
        self.assertIn("not selectable", facts["Assortment"])
        self.assertFalse(self.entry["specificationUpdates"][-1]["minimumOrder"]["currentStockStatusVerified"])
        self.assertEqual(self.entry["priceTiers"], [])
        self.assertEqual(self.entry["pricingMode"], "quote_only")

    def test_new_photographs_match_original_upload_fingerprints_and_old_images_remain(self):
        self.assertEqual(len(self.entry["imagesLocal"]), 3)
        for item in self.record["sources"] + self.record["currentGallery"]:
            self.assertEqual(hashlib.sha256((ROOT / item["path"]).read_bytes()).hexdigest(), item["sha256"])
        for old in self.record["previousPublishedReferences"]["imagesLocal"]:
            self.assertTrue((ROOT / old).is_file())
        self.assertNotEqual(self.entry["imagesLocal"][0], self.record["previousPublishedReferences"]["imagesLocal"][0])

    def test_ruler_image_does_not_invent_thickness_holes_or_hanging_hardware(self):
        evidence = self.entry["specificationUpdates"][-1]["sizeEvidence"]
        self.assertEqual(evidence["referenceSizeMm"], 21)
        self.assertFalse(evidence["instrumentMeasurementAdded"])
        for key in ["thicknessMm", "holeDiameterMm", "toleranceMm"]:
            self.assertIsNone(evidence[key])
        specs = public_specs(self.entry)
        self.assertNotIn("Hole", specs)
        self.assertIn("Confirm the attachment method", specs["Application"])
        page = (ROOT / "p-rw22372.html").read_text()
        self.assertNotIn("confirm how many pieces the current bag contains", page)
        self.assertIn("100 pieces per bag", page)


if __name__ == "__main__":
    unittest.main()
