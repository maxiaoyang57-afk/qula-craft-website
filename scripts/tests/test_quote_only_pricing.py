"""Legacy pricing cleanup preserves product facts and cannot restore offers."""
import importlib.util
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
spec = importlib.util.spec_from_file_location("pricing_cleanup", ROOT / "scripts/harden-product-pricing.py")
cleanup = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cleanup)


class QuoteOnlyPricingTests(unittest.TestCase):
    def test_legacy_import_is_cleared_without_changing_product_facts(self):
        old = {"sku": "CDK3075", "moq": "10 pieces", "specs": {"Material": "Resin"},
               "imagesLocal": ["image.webp"], "priceTiers": [{"qty": "10", "unit": "pieces", "price": "0.29"}]}
        new = cleanup.inquiry_source(old)
        self.assertEqual(new["priceTiers"], [])
        self.assertEqual(new["pricingMode"], "quote_only")
        self.assertEqual({k: v for k, v in new.items() if k not in ("priceTiers", "pricingMode")},
                         {k: v for k, v in old.items() if k != "priceTiers"})
        self.assertTrue(old["priceTiers"])
        self.assertEqual(cleanup.inquiry_source(new), new)

    def test_public_price_and_offer_removed_but_moq_and_content_retained(self):
        for moq in ("1 bag", "10 pieces", "100 pairs"):
            crumb = '<script type="application/ld+json">{"@type":"BreadcrumbList"}</script>\n'
            product = '<script type="application/ld+json">' + json.dumps({"@type": "Product", "offers": {"@type": "AggregateOffer", "lowPrice": "11.41"}}) + '</script>\n'
            block = (f'<div class="answer-box" style="margin:14px 0"><b>From $11.41 / bag</b> · MOQ {moq} — tiered pricing by quantity; '
                     'the full tier table comes back with your quote within 12&#8211;24 hours.</div>')
            body = '<h1>Exact product</h1><img src="image.webp"><a href="quote.html?sku=SKU1">Request Quote</a>'
            result = cleanup.inquiry_page(product + crumb + block + body)
            self.assertNotIn("11.41", result)
            self.assertNotIn("AggregateOffer", result)
            self.assertIn(f"MOQ {moq}", result)
            self.assertIn(crumb, result)
            self.assertTrue(result.endswith(body))
            self.assertEqual(cleanup.inquiry_page(result), result)

    def test_llms_cleanup_preserves_sku_pack_and_link(self):
        line = '- [Charm](https://www.qulacrafts.com/p-sku1.html): SKU SKU1 · MOQ 10 pieces · from $0.29/pieces'
        self.assertEqual(cleanup.LLMS_PRICE.sub('', line), line.split(' · from $')[0])


if __name__ == "__main__":
    unittest.main()
