import json,re,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
class OwnerSkuCorrection(unittest.TestCase):
 def test_one_corrected_product_preserves_source_and_old_link(self):
  products=[p for c in json.loads((ROOT/'assets/data/product-catalog.json').read_text())['categories'] for p in c['products']]
  self.assertEqual(len(products),402)
  self.assertEqual(len([p for p in products if p['sku']=='RW26808' and 'Acorn' in p['title']]),1)
  self.assertEqual(len([p for p in products if p['sku']=='RW20809']),1)
  entry=next(p for p in json.loads((ROOT/'assets/data/pdp-data.json').read_text()) if p['sku']=='RW20809')
  self.assertEqual(entry['sourceFields']['sku'],'RW26808')
  page=(ROOT/'p-rw20809.html').read_text()
  schema=next(json.loads(m) for m in re.findall(r'<script type="application/ld\+json"[^>]*>(.*?)</script>',page,re.S) if json.loads(m).get('@type')=='Product')
  self.assertEqual(schema['sku'],'RW20809')
  self.assertEqual(len(schema['image']),3)
  self.assertFalse((ROOT/'p-rw26808.html').exists())
  redirect=next(r for r in json.loads((ROOT/'vercel.json').read_text())['redirects'] if r['source']=='/p-rw26808.html')
  self.assertEqual(redirect['destination'],'https://www.qulacrafts.com/p-rw20809.html')
  self.assertTrue(redirect['permanent'])
if __name__=='__main__':unittest.main()
