"""Import reviewed Monica source records using exact-SKU media and inquiry-only pricing."""
import copy
import hashlib
import html
import json
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import quote

from add_products_20261012 import card, save_json
from catalog_schema import catalog_list_item

ROOT = Path(__file__).resolve().parents[1]
BASE, DATE = 'https://www.qulacrafts.com/', '2026-10-26'


def main():
    plans = json.loads((ROOT/'scripts/data/product-plan-20261026-monica.json').read_text())
    cat = json.loads((ROOT/'assets/data/product-catalog.json').read_text())
    pdp = json.loads((ROOT/'assets/data/pdp-data.json').read_text())
    copies = json.loads((ROOT/'assets/data/pdp-copy.json').read_text())
    details = json.loads((ROOT/'assets/data/pdp-description-details.json').read_text())
    before = copy.deepcopy(cat)
    prior_pdp = copy.deepcopy(pdp)
    prior_flat = [p for c in cat['categories'] for p in c['products']]
    byslug = {c['slug']:c for c in cat['categories']}
    selected = {p['sku'] for p in plans}
    assert len(selected) == len(plans) == 42
    assert not selected.intersection(p['sku'] for p in prior_flat)
    additions, changed, manifest = {}, [], []
    for plan in plans:
        sku, key = plan['sku'], plan['key']
        category = byslug[plan['category']]
        images = plan['imagesLocal']
        assert len(images) == len(set(images)) == 3
        for rel in images:
            assert (ROOT/rel).is_file(), rel
        row = dict(category=category['name'], categorySlug=category['slug'],
                   sourceSheet='Monica JSON', sortOrder=0, sku=sku,
                   title=plan['title'], titleFull=plan['title'], titleShort=plan['title'],
                   sourceTitle=plan['sourceFields']['title'], sourceCategory=category['name'],
                   alibabaUrl=plan['sourceUrl'], cleanAlibabaUrl=plan['sourceUrl'],
                   alibabaProductId=plan['sourceProductId'], status='ok', anchorNote='',
                   pdp=f'p-{key}.html', image=images[0], imageAlt=sku+' '+plan['title'],
                   imageWidth=plan['imageDimensions'][0]['width'],
                   imageHeight=plan['imageDimensions'][0]['height'],
                   imageHash=hashlib.md5((ROOT/images[0]).read_bytes()).hexdigest())
        row['inquiryUrl'] = ('quote.html?product='+quote(sku+' '+plan['title'],safe='')+
                             '&sku='+quote(sku,safe='')+'&image='+quote(images[0],safe='/')+
                             '&category='+quote(category['name'],safe=''))
        entry = dict(catalogIndex=0, assetKey=key, sku=sku, category=category['name'],
                     categorySlug=category['slug'], url=plan['sourceUrl'], status='ok', reason='',
                     titleFull=plan['sourceFields']['title'], moq='', priceTiers=[],
                     stockStatus='Confirm current availability by inquiry',
                     specs={'Material':plan['material'],'Size':plan['dimensions'],
                            'Standard pack':plan['packing'], 'Attachment':plan['attachment'],
                            'Selection note':plan['factNote'],
                            'Packing and MOQ':'Packing quantity is not the MOQ. Confirm minimum order quantity and dispatch date by inquiry.'},
                     images=[plan['sourceImageUrl']], imagesLocal=images,
                     sourceJson='Monica_第8页起_monica-1793018390982-0gii0pc.json',
                     sourceProductId=plan['sourceProductId'], sourceFields=plan['sourceFields'],
                     materialBasis=plan['materialBasis'], metaTitle=plan['metaTitle'],
                     metaDescription=plan['description'], shortProductDescription=plan['description'],
                     galleryLabels=plan['galleryLabels'],galleryNote=plan['galleryNote'])
        copies[key] = dict(sku=sku,displayTitle=plan['title'],metaTitle=plan['metaTitle'],
                           metaDescription=plan['description'],isFamilyFriendly=True)
        details[key] = plan['factNote']+' '+plan['uses']+' Reference '+sku+' and confirm the required quantity, assortment, packing and destination with your inquiry.'
        additions.setdefault(category['slug'],[]).append(row)
        pdp.append(entry)
        changed.append((plan,row,entry))
        manifest.append(dict(sku=sku,operation='new',pdp=row['pdp'],sourceFields=plan['sourceFields'],
                             sourceUrl=plan['sourceUrl'],materialBasis=plan['materialBasis'],
                             imageOutputs=[dict(path=rel,role=plan['galleryLabels'][i],
                                                sha256=hashlib.sha256((ROOT/rel).read_bytes()).hexdigest(),
                                                **plan['imageDimensions'][i]) for i,rel in enumerate(images)]))
    for c in cat['categories']:
        c['products'] = additions.get(c['slug'],[])+c['products']
        c['productCount'] = len(c['products'])
        for i,p in enumerate(c['products'],1):p['sortOrder']=i
    flat = [p for c in cat['categories'] for p in c['products']]
    indices = {p['pdp']:i for i,p in enumerate(flat,1)}
    for entry in pdp:entry['catalogIndex']=indices[f'p-{entry["assetKey"]}.html']
    cat.update(totalProducts=len(flat),totalImages=len(flat),generatedAt=DATE)
    for filename,data,indent in [('product-catalog.json',cat,1),('pdp-data.json',pdp,2),
                                  ('pdp-copy.json',copies,2),('pdp-description-details.json',details,2)]:
        save_json(ROOT/'assets/data'/filename,data,indent)
    editorial_script=ROOT/'scripts/revise_monica_copy_20261026.py'
    if editorial_script.exists():
        subprocess.run([sys.executable,str(editorial_script),'--brand','qula'],check=True)
    generator = (ROOT/'scripts/gen_pdp.py').read_text().split('# ---- 2)')[0]
    marker = 'for e in pdp:\n    sku, key'
    assert generator.count(marker)==1
    generator = generator.replace(marker,'for e in pdp:\n    if e["sku"] not in BATCH_SKUS: continue\n    sku, key')
    exec(compile(generator,str(ROOT/'scripts/gen_pdp.py'),'exec'),
         {'__file__':str(ROOT/'scripts/gen_pdp.py'),'BATCH_SKUS':selected})
    for plan,row,entry in changed:
        path=ROOT/row['pdp'];page=path.read_text()
        if editorial_script.exists():
            # The generator already renders the reviewed specs, image notes,
            # selection section and full inquiry URL from the editorial overlay.
            path.write_text('\n'.join(line.rstrip() for line in page.splitlines())+'\n')
            continue
        for i,label in enumerate(plan['galleryLabels'][1:],2):
            page=page.replace(row['sku']+' detail view '+str(i),row['sku']+' '+label)
        page=page.replace('Batch test reports (EN 71, ASTM F963, CPC, REACH) available on request.',
                          'Confirm the applicable testing scope for the selected product and destination.')
        marker='</div>\n<div>\n  <div class="answer-box"'
        assert marker in page
        page=page.replace(marker,'<p class="pdp-image-note" style="font-size:.85rem;color:#667085">'+html.escape(plan['galleryNote'])+'</p>'+marker,1)
        page,n=re.subn(r'quote\.html\?product=[^"<>]+',html.escape(row['inquiryUrl'],quote=True),page,count=1)
        assert n==1
        path.write_text('\n'.join(line.rstrip() for line in page.splitlines())+'\n')
    for slug,rows in additions.items():
        path=ROOT/(slug+'.html');page=path.read_text()
        first=re.search(r'<article class="product-card"',page);assert first
        page=page[:first.start()]+''.join(card(row) for row in rows)+page[first.start():]
        def schema(m):
            value=json.loads(m[1])
            if value.get('@type')=='ItemList':
                value.update(numberOfItems=len(byslug[slug]['products']),
                             itemListElement=[catalog_list_item(p,i) for i,p in enumerate(byslug[slug]['products'],1)])
            return '<script type="application/ld+json">'+json.dumps(value,ensure_ascii=False,separators=(',',':'))+'</script>'
        page=re.sub(r'<script type="application/ld\+json">(.*?)</script>',schema,page,flags=re.S)
        path.write_text(page)
    xml=(ROOT/'sitemap.xml').read_text()
    for plan,row,entry in changed:
        loc=BASE+row['pdp'];assert loc not in xml
        node='<url><loc>'+loc+'</loc><lastmod>'+DATE+'</lastmod><changefreq>monthly</changefreq><priority>0.7</priority>'+''.join('<image:image><image:loc>'+BASE+p+'</image:loc><image:title>'+html.escape(row['sku']+' '+row['title'])+'</image:title></image:image>' for p in entry['imagesLocal'])+'</url>'
        xml=xml.replace('</urlset>','  '+node+'\n</urlset>')
    (ROOT/'sitemap.xml').write_text(xml)
    for filename in ['llms-full.txt','llms.txt']:
        path=ROOT/filename;text=path.read_text().replace(f'{len(prior_flat)} live stock items',f'{len(flat)} live stock items')
        if filename=='llms-full.txt':
            for slug,rows in additions.items():
                heading='## '+byslug[slug]['name']+'\n';assert heading in text
                text=text.replace(heading,heading+''.join(f'- [{p["title"]}]({BASE+p["pdp"]}): SKU {p["sku"]} · selected specifications, packing and MOQ by inquiry\n' for p in rows),1)
        path.write_text(text)
    now={p['pdp']:p for p in flat}
    for old in prior_flat:
        assert {k:v for k,v in old.items() if k!='sortOrder'}=={k:v for k,v in now[old['pdp']].items() if k!='sortOrder'}
    for old in prior_pdp:
        current=next(e for e in pdp if e['assetKey']==old['assetKey'])
        assert {k:v for k,v in old.items() if k!='catalogIndex'}=={k:v for k,v in current.items() if k!='catalogIndex'}
    save_json(ROOT/'docs/product-batch-manifest-20261026-monica.json',
              dict(batchId='qula-products-20261026-monica',catalogCountBefore=len(prior_flat),
                   catalogCountAfter=len(flat),newProductCount=len(plans),updatedProductCount=0,
                   imageCount=3*len(plans),products=manifest))
    print(json.dumps(dict(new=len(plans),catalog=len(flat),images=3*len(plans))))


if __name__=='__main__':main()
