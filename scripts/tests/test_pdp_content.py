"""Guard published product content against duplicate paragraphs and lost facts."""
import copy
import html
import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from pdp_content import buying_copy, product_summary, render_buying_guide
from pdp_public_copy import CONTENT_REVIEWS, is_generic_occasion_list, public_specs


def text(value):
    return ' '.join(html.unescape(re.sub(r'<[^>]*>', '', value)).split())


class ProductContentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.entries = json.loads((ROOT / 'assets/data/pdp-data.json').read_text())
        cls.copies = json.loads((ROOT / 'assets/data/pdp-copy.json').read_text())
        catalog = json.loads((ROOT / 'assets/data/product-catalog.json').read_text())
        cls.public = {p['pdp'] for c in catalog['categories'] for p in c['products']}

    def test_public_pages_do_not_repeat_long_product_paragraphs(self):
        for filename in sorted(self.public):
            with self.subTest(page=filename):
                page = (ROOT / filename).read_text()
                main = re.search(r'<main\b[^>]*>(.*?)</main>', page, re.S).group(1)
                main = re.sub(r'<article\b.*?</article>', '', main, flags=re.S)
                paragraphs = [text(p) for p in re.findall(r'<p\b[^>]*>(.*?)</p>', main, re.S)]
                long = [p for p in paragraphs if len(p.split()) >= 35]
                for i, paragraph in enumerate(long):
                    self.assertFalse(any(paragraph in other or other in paragraph for other in long[i + 1:]), filename)

    def test_reviewed_facts_and_missing_measurements_stay_explicit(self):
        for key, review in CONTENT_REVIEWS.items():
            page = (ROOT / f'p-{key}.html').read_text()
            self.assertIn(review['summary'], html.unescape(page))
            self.assertIn('data-product-buying-guide=', page)
        for key in ('yx605', 'cdk3075'):
            entry = next(e for e in self.entries if e['assetKey'] == key)
            self.assertNotIn('Size', public_specs(entry))
            self.assertNotIn('Standard pack', public_specs(entry))
        for key, fact in (('rw927', '24 mm'), ('yx162', '3 × 3 × 23 mm'), ('rw22754', '20 × 55 mm'), ('yx4138', '500 g')):
            self.assertIn(fact, html.unescape((ROOT / f'p-{key}.html').read_text()))

    def test_source_records_are_untouched_and_generic_occasions_are_not_published(self):
        for entry in self.entries:
            saved = copy.deepcopy(entry)
            published = public_specs(entry)
            self.assertEqual(entry, saved)
            self.assertFalse(is_generic_occasion_list(published.get('Application', '')))
            filename = f'p-{entry["assetKey"]}.html'
            if filename not in self.public:
                continue
            page = (ROOT / filename).read_text()
            match = re.search(r'<b>Application</b></td><td>(.*?)</td>', page, re.S)
            if match:
                self.assertFalse(is_generic_occasion_list(text(match.group(1))))
        tie = next(e for e in self.entries if e['assetKey'] == 'cdk199')
        self.assertEqual(tie['specs']['Material'], 'resin')
        self.assertEqual(public_specs(tie)['Material'], 'Silicone')

    def test_regeneration_preserves_each_unique_buying_paragraph(self):
        for entry in self.entries:
            key = entry['assetKey']
            copy_row = self.copies[key]
            rendered = html.unescape(render_buying_guide(entry, copy_row))
            effective = buying_copy(entry, copy_row)
            for name in ('projectUse', 'selectionAdvice', 'variantSizeNotes'):
                paragraph = CONTENT_REVIEWS.get(key, {}).get(name, copy_row.get(name, ''))
                if paragraph:
                    self.assertIn(paragraph, rendered)
            summary = product_summary(entry, copy_row)
            for paragraph in effective.values():
                if len(paragraph.split()) >= 35:
                    self.assertNotIn(paragraph, summary)


if __name__ == '__main__':
    unittest.main()
