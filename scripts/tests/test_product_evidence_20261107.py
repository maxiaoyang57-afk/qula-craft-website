"""Regression checks for approximate supplier facts and unit-specific references."""
import json,re,sys,unittest
from pathlib import Path
from urllib.parse import parse_qs,urlsplit
from html.parser import HTMLParser
import html
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
from pdp_public_copy import public_specs
from pdp_selection_guides import GUIDES,selection_quote_url

class ProductEvidenceTests(unittest.TestCase):
 def test_ya855_keeps_approximate_hole_and_original_worksheet(self):
  rows=json.loads((ROOT/'assets/data/pdp-data.json').read_text());entry=next(x for x in rows if x['sku']=='YA855')
  self.assertEqual(entry['sourceFields']['孔径'],'有')
  self.assertIn('Approx. 2 mm',public_specs(entry)['Hole'])
  self.assertIsNone(entry['specificationUpdates'][-1]['holeDiameter']['tolerance'])
  self.assertFalse(entry['specificationUpdates'][-1]['holeDiameter']['instrumentMeasurementVerified'])
  page=(ROOT/'p-ya855.html').read_text();self.assertIn('Approx. 2 mm',page)
  self.assertNotIn('hole diameter not supplied',page.lower())
  self.assertIn('ya855-2-reference-specifications-20261107.png',page)
  self.assertTrue((ROOT/entry['specificationUpdates'][-1]['previousSpecificationGraphic']).is_file())
 def test_weight_does_not_become_dimensions_or_piece_count(self):
  for key,weight in [('slm10094','30 g'),('slm10093','500 g'),('slm10012','500 g')]:
   with self.subTest(key=key):
    page=(ROOT/('p-'+key+'.html')).read_text()
    self.assertRegex(page,r'<b>Reference pack weight</b></td><td>'+weight)
    self.assertNotRegex(page,r'<b>Size</b></td><td>'+weight)
    self.assertIn('Mix specification',page)
 def test_unrelated_import_claim_is_not_published_as_application(self):
  rows=json.loads((ROOT/'assets/data/pdp-data.json').read_text());entry=next(x for x in rows if x['sku']=='CDK001208')
  self.assertIn('Fireproof',entry['specs']['Application'])
  self.assertEqual(public_specs(entry)['Application'],'Bag and keychain decoration')
  self.assertNotIn('Fireproof',(ROOT/'p-cdk001208.html').read_text())
 def test_reviewed_inquiry_carries_exact_reference_and_keeps_existing_context(self):
  for key in ['ya855','rw22372','slm10094','slm10093','slm10012','cdk001208']:
   sku=GUIDES[key]['sku'];href=selection_quote_url(key,'quote.html?sku='+sku+'&image=assets/test.jpg&product=Chosen%20design')
   params=parse_qs(href.replace('&amp;','&').split('?',1)[1]);self.assertEqual(params['sku'],[sku]);self.assertEqual(params['image'],['assets/test.jpg']);self.assertEqual(params['product'],['Chosen design'])
   self.assertIn(sku,params['application'][0]);self.assertIn('category',params)
   # Repeated generation must not duplicate the buyer's brief.
   self.assertEqual(selection_quote_url(key,href),href)
 def test_generated_inquiries_preserve_full_catalog_names(self):
  class Links(HTMLParser):
   def __init__(self):super().__init__();self.hrefs=[]
   def handle_starttag(self,tag,attrs):
    if tag=='a':
     href=dict(attrs).get('href','')
     if href.startswith('quote.html?'):self.hrefs.append(href)
  catalog=json.loads((ROOT/'assets/data/product-catalog.json').read_text())
  products=[p for c in catalog['categories'] for p in c['products']]
  copies=json.loads((ROOT/'assets/data/pdp-copy.json').read_text())
  for key in ['ya855','rw22372','slm10094','slm10093','slm10012','cdk001208']:
   sku=GUIDES[key]['sku'];p=next(p for p in products if p['sku']==sku)
   expected=parse_qs(urlsplit(html.unescape(p['inquiryUrl'])).query)['product'][0] if p.get('inquiryUrl') else copies[key]['displayTitle']
   links=Links();links.feed((ROOT/('p-'+key+'.html')).read_text())
   names=[parse_qs(urlsplit(href).query).get('product',[''])[0] for href in links.hrefs if parse_qs(urlsplit(href).query).get('sku')==[sku]]
   self.assertTrue(names,sku);self.assertTrue(all(name==expected for name in names),sku)
 def test_cookie_source_size_is_visible(self):
  self.assertIn('<b>Size</b></td><td>21 mm</td>',(ROOT/'p-rw22372.html').read_text())

if __name__=='__main__':unittest.main()
