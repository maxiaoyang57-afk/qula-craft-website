"""Import the reviewed RW26724 JSON record without changing existing product facts.

Uses the sanitized source and prepared media committed with this change. Existing
products retain their content; only catalog positions move for the new first card.
"""
import copy
import hashlib
import html
import json
import re
from pathlib import Path
from urllib.parse import quote

from add_products_20261012 import card, save_json
from catalog_schema import catalog_list_item

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://www.qulacrafts.com/'
SKU, KEY, DATE = 'RW26724', 'rw26724', '2026-10-26'


def main():
    source = json.loads((ROOT/'scripts/data/product-source-20261026-json-trial.json').read_text())
    cat = json.loads((ROOT/'assets/data/product-catalog.json').read_text())
    pdp = json.loads((ROOT/'assets/data/pdp-data.json').read_text())
    copies = json.loads((ROOT/'assets/data/pdp-copy.json').read_text())
    details = json.loads((ROOT/'assets/data/pdp-description-details.json').read_text())
    before_cat, before_pdp = copy.deepcopy(cat), copy.deepcopy(pdp)
    flat_before = [p for c in cat['categories'] for p in c['products']]
    assert source['sku'] == SKU and SKU not in {p['sku'] for p in flat_before}
    category = next(c for c in cat['categories'] if c['slug'] == 'resin-charms')
    title = 'Red and White Mushroom Resin Charms'
    desc = 'Wholesale red and white mushroom resin charms, RW26724. Size 16 × 17 mm, 100 pieces per bag. Ask for selected quantity, samples and packing.'
    images = [f'images/catalog/{KEY}/{i:02}.jpg' for i in range(1, 4)]
    row = dict(category=category['name'], categorySlug=category['slug'],
               sourceSheet='Monica JSON', sortOrder=1, sku=SKU, title=title,
               titleFull=title, titleShort=title, sourceTitle=source['title'],
               sourceCategory='Resin Charms', alibabaUrl=source['product_url'],
               cleanAlibabaUrl=source['product_url'], alibabaProductId=source['product_id'],
               status='ok', anchorNote='', pdp=f'p-{KEY}.html', image=images[0],
               imageAlt=f'{SKU} {title}', imageWidth=1000, imageHeight=1000,
               imageHash=hashlib.md5((ROOT/images[0]).read_bytes()).hexdigest())
    row['inquiryUrl'] = ('quote.html?product='+quote(SKU+' '+title, safe='')+
                         '&sku='+SKU+'&image='+quote(images[0], safe='/')+'&category=Resin%20Charms')
    specs = {'Material':'Resin', 'Size':'16 × 17 mm', 'Color':'Red and white',
             'Standard pack':'100 pieces per bag',
             'Attachment':'Confirm attachment method by inquiry',
             'Packing and MOQ':'Confirm MOQ, sample availability and dispatch date by inquiry.'}
    entry = dict(catalogIndex=0, assetKey=KEY, sku=SKU, category=category['name'],
                 categorySlug=category['slug'], url=source['product_url'], status='ok',
                 reason='', titleFull=source['title'], moq='', priceTiers=[],
                 stockStatus='Confirm current availability by inquiry', specs=specs,
                 images=source['images']+[source['additionalImageUrl']], imagesLocal=images,
                 sourceJson='Monica_第8页起_monica-1793018390982-0gii0pc.json',
                 sourceProductId=source['product_id'], sourceFields=source['verifiedFacts'],
                 sourceFileSha256=source['sourceFileSha256'],
                 metaTitle='RW26724 Mushroom Resin Charms Wholesale | Qula Craft',
                 metaDescription=desc, shortProductDescription=desc,
                 galleryLabels=source['galleryLabels'], galleryNote=source['galleryNote'])
    copies[KEY] = dict(sku=SKU, displayTitle=title, metaTitle=entry['metaTitle'],
                       metaDescription=desc, isFamilyFriendly=True)
    details[KEY] = ('RW26724 features red caps with white dots and white stems. '
                    'The source specification is 16 × 17 mm and 100 pieces per bag. '
                    'Choose these decorative miniatures for handmade craft embellishment '
                    'or miniature scenes. Confirm the attachment method, required quantity '
                    'and sample before ordering. Styling props are not included.')
    category['products'].insert(0, row)
    for c in cat['categories']:
        c['productCount'] = len(c['products'])
        for i, p in enumerate(c['products'], 1):
            p['sortOrder'] = i
    flat = [p for c in cat['categories'] for p in c['products']]
    pdp.append(entry)
    indices = {p['pdp']:i for i,p in enumerate(flat,1)}
    for e in pdp:
        e['catalogIndex'] = indices[f'p-{e["assetKey"]}.html']
    cat.update(totalProducts=len(flat), totalImages=len(flat), generatedAt=DATE)
    for path, data, indent in [('product-catalog.json',cat,1),('pdp-data.json',pdp,2),
                               ('pdp-copy.json',copies,2),('pdp-description-details.json',details,2)]:
        save_json(ROOT/'assets/data'/path, data, indent)

    # Generate only the added PDP with the established generator; dimensions for
    # existing related products come from already approved catalog records.
    dimensions = {p['image']:(p['imageWidth'],p['imageHeight']) for p in flat
                  if p.get('imageWidth') and p.get('imageHeight')}
    for e in pdp:
        if e.get('imagesLocal') and flat[e['catalogIndex']-1]['image'] in dimensions:
            dimensions.setdefault(e['imagesLocal'][0], dimensions[flat[e['catalogIndex']-1]['image']])
    generator = (ROOT/'scripts/gen_pdp.py').read_text().split('# ---- 2)')[0]
    generator = generator.replace('for e in pdp:\n    sku, key',
                                  'for e in pdp:\n    if e["sku"] != "RW26724": continue\n    sku, key')
    generator = generator.replace('def img_dim(rel):',
                                  'def img_dim(rel):\n    if not (SITE / rel).exists() and rel in APPROVED_DIMS: return APPROVED_DIMS[rel]')
    exec(compile(generator,str(ROOT/'scripts/gen_pdp.py'),'exec'),
         {'__file__':str(ROOT/'scripts/gen_pdp.py'),'APPROVED_DIMS':dimensions})
    pagepath = ROOT/row['pdp']
    page = pagepath.read_text().replace('RW26724 detail view 2','RW26724 hand-held product reference')
    page = page.replace('RW26724 detail view 3','RW26724 detail crop of hand-held reference')
    page = page.replace('Batch test reports (EN 71, ASTM F963, CPC, REACH) available on request.',
                        'Confirm the applicable testing scope with your inquiry.')
    marker = '</div>\n<div>\n  <div class="answer-box"'
    assert marker in page
    page = page.replace(marker,'<p class="pdp-image-note" style="font-size:.85rem;color:#667085">'+html.escape(source['galleryNote'])+'</p>'+marker,1)
    page,n = re.subn(r'quote\.html\?product=[^"<>]+',html.escape(row['inquiryUrl'],quote=True),page,count=1)
    assert n == 1
    pagepath.write_text('\n'.join(line.rstrip() for line in page.splitlines())+'\n')
    path = ROOT/'resin-charms.html'
    page = path.read_text()
    first = re.search(r'<article class="product-card"',page)
    assert first
    page = page[:first.start()]+card(row)+page[first.start():]
    def schema(m):
        value = json.loads(m[1])
        if value.get('@type') == 'ItemList':
            value.update(numberOfItems=len(category['products']),
                         itemListElement=[catalog_list_item(p,i) for i,p in enumerate(category['products'],1)])
        return '<script type="application/ld+json">'+json.dumps(value,ensure_ascii=False,separators=(',',':'))+'</script>'
    page = re.sub(r'<script type="application/ld\+json">(.*?)</script>',schema,page,flags=re.S)
    path.write_text(page)
    xml = (ROOT/'sitemap.xml').read_text()
    loc = BASE+row['pdp']
    assert loc not in xml
    node = '<url><loc>'+loc+'</loc><lastmod>'+DATE+'</lastmod><changefreq>monthly</changefreq><priority>0.7</priority>'+''.join('<image:image><image:loc>'+BASE+p+'</image:loc><image:title>'+SKU+' '+title+'</image:title></image:image>' for p in images)+'</url>'
    (ROOT/'sitemap.xml').write_text(xml.replace('</urlset>','  '+node+'\n</urlset>'))
    for filename in ['llms-full.txt','llms.txt']:
        path = ROOT/filename
        text = path.read_text().replace(f'{len(flat_before)} live stock items',f'{len(flat)} live stock items')
        if filename == 'llms-full.txt':
            heading = '## '+category['name']+'\n'
            assert heading in text
            text = text.replace(heading,heading+f'- [{title}]({loc}): SKU {SKU} · Resin · 16 × 17 mm · 100 pieces per bag · MOQ and pricing by inquiry\n',1)
        path.write_text(text)
    now = {p['pdp']:p for p in flat}
    for p in flat_before:
        assert {k:v for k,v in p.items() if k != 'sortOrder'} == {k:v for k,v in now[p['pdp']].items() if k != 'sortOrder'}
    for old in before_pdp:
        cur = next(e for e in pdp if e['assetKey'] == old['assetKey'])
        assert {k:v for k,v in old.items() if k != 'catalogIndex'} == {k:v for k,v in cur.items() if k != 'catalogIndex'}
    save_json(ROOT/'docs/product-batch-manifest-20261026-json-trial.json',
              dict(batchId='qula-products-20261026-json-trial',catalogCountBefore=len(flat_before),
                   catalogCountAfter=len(flat),newProductCount=1,updatedProductCount=0,imageCount=3,
                   products=[dict(sku=SKU,pdp=row['pdp'],sourceUrl=source['product_url'],
                                  imageEdits=source['imageEdits'],galleryNote=source['galleryNote'])]))
    print(json.dumps(dict(new=SKU,catalog=len(flat),images=3)))


if __name__ == '__main__':
    main()
