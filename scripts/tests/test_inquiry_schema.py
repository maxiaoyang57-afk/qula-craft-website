"""Prevent fake offers and preserve inquiry content when removing ineligible markup."""
import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from inquiry_schema import pdp_schemas, remove_inquiry_product_schema
from pdp_image_batch import update_product_schema


class InquirySchemaTests(unittest.TestCase):
    def setUp(self):
        self.product = {"@context": "https://schema.org", "@type": "Product", "name": "Test charm", "sku": "SKU1"}
        self.crumb = {"@type": "BreadcrumbList", "itemListElement": [{"name": "SKU1", "item": "https://www.qulacrafts.com/p-sku1.html"}]}

    def test_generator_does_not_fabricate_rich_result_fields(self):
        original = copy.deepcopy(self.product)
        self.assertEqual(pdp_schemas(self.product, self.crumb), [self.crumb])
        self.assertEqual(self.product, original)
        self.product.update(offers={}, review=None, aggregateRating={})
        self.assertEqual(pdp_schemas(self.product, self.crumb), [self.crumb])

    def test_existing_offer_or_review_is_not_changed(self):
        for field, value in (("offers", {"@type": "Offer", "price": "2.50", "priceCurrency": "USD"}),
                             ("review", {"@type": "Review", "name": "A supplied review"})):
            product = dict(self.product, **{field: value})
            self.assertEqual(pdp_schemas(product, self.crumb), [product, self.crumb])

    def test_removal_preserves_body_other_jsonld_and_is_idempotent(self):
        for heading in ("Quoted by pack and quantity", "Wholesale pricing by quotation", "Packaging &amp; MOQ"):
            body = f'<div class="answer-box"><b>{heading}</b></div><a href="quote.html?sku=SKU1">Request Quote</a>'
            crumb = '<script type="application/ld+json">' + json.dumps(self.crumb) + '</script>\n'
            product = '<script type="application/ld+json">' + json.dumps(self.product) + '</script>\n'
            original = '<head>' + product + crumb + '</head>' + body
            result = remove_inquiry_product_schema(original)
            self.assertEqual(result, '<head>' + crumb + '</head>' + body)
            self.assertEqual(remove_inquiry_product_schema(result), result)
            self.assertEqual(update_product_schema(result, ['https://www.qulacrafts.com/image.jpg']), result)

    def test_unknown_copy_requires_review_instead_of_silent_removal(self):
        page = '<script type="application/ld+json">' + json.dumps(self.product) + '</script>'
        with self.assertRaises(ValueError):
            remove_inquiry_product_schema(page)
        with self.assertRaises(ValueError):
            update_product_schema('<html>broken page</html>', [])


if __name__ == "__main__":
    unittest.main()
