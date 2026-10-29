"""Add the image-reviewed Monica batches, retaining every existing product's facts."""
import copy, hashlib, html, json, re
from pathlib import Path
from urllib.parse import quote
from add_products_20261012 import card, save_json
from catalog_schema import catalog_list_item

ROOT=Path(__file__).resolve().parents[1]
BASE='https://www.qulacrafts.com/'
DATE='2026-10-29'

def main():
    plan=json.loads((ROOT/'scripts/data/monica-reviewed-batch-27-20261029.json').read_text())
    products=plan['products'];selected={p['sku'] for p in products}
    cat=json.loads((ROOT/'assets/data/product-catalog.json').read_text())
    pdp=json.loads((ROOT/'assets/data/pdp-data.json').read_text())
    copies=json.loads((ROOT/'assets/data/pdp-copy.json').read_text())
    details=json.loads((ROOT/'assets/data/pdp-description-details.json').read_text())
    oldcat=copy.deepcopy(cat);oldpdp=copy.deepcopy(pdp)
    prior=[p for c in cat['categories'] for p in c['products']]
    assert len(selected)==len(products)==plan['newProductCount']
    assert not selected.intersection(p['sku'] for p in prior)
    categories={c['slug']:c for c in cat['categories']};additions={};manifest=[]
    for p in products:
        sku,key=p['sku'],p['key'];category=categories[p['category']];images=p['qulaImages']
        for info in p['qulaImageInfo']:
            assert hashlib.sha256((ROOT/info['path']).read_bytes()).hexdigest()==info['sha256']
        row=dict(category=category['name'],categorySlug=category['slug'],sourceSheet='Monica JSON',sortOrder=0,
                 sku=sku,title=p['title'],titleFull=p['title'],titleShort=p['title'],sourceTitle=p['sourceFields']['title'],
                 sourceCategory=category['name'],alibabaUrl=p['sourceUrl'],cleanAlibabaUrl=p['sourceUrl'],
                 alibabaProductId=p['sourceProductId'],status='ok',anchorNote='',pdp='p-'+key+'.html',
                 image=images[0],imageAlt=sku+' '+p['title'],imageWidth=p['imageDimensions'][0]['width'],
                 imageHeight=p['imageDimensions'][0]['height'],imageHash=hashlib.md5((ROOT/images[0]).read_bytes()).hexdigest())
        row['inquiryUrl']='quote.html?product='+quote(sku+' '+p['title'],safe='')+'&sku='+quote(sku,safe='')+'&image='+quote(images[0],safe='/')+'&category='+quote(category['name'],safe='')
        verified=dict(material=p['material'],size=p['dimensions'],additionalProperty=[{'@type':'PropertyValue','name':'Standard pack','value':p['packing']}])
        specs={'Material':p['material'],'Size':p['dimensions'],'Standard pack':p['packing'],
               'Attachment':p['attachment'],'Selection':p['variantSizeNotes'],
               'Packing and MOQ':'The reference pack quantity is not the MOQ. Confirm minimum quantity and dispatch timing in your quotation.'}
        entry=dict(catalogIndex=0,assetKey=key,sku=sku,category=category['name'],categorySlug=category['slug'],
                   url=p['sourceUrl'],status='ok',reason='',titleFull=p['sourceFields']['title'],moq='',priceTiers=[],
                   stockStatus='Confirm current availability by inquiry',specs=specs,images=[p['sourceImageUrl']],imagesLocal=images,
                   sourceJson=plan['sourceFile'],sourceFileSha256=plan['sourceSha256'],sourceProductId=p['sourceProductId'],
                   sourceFields=p['sourceFields'],materialBasis=p['materialBasis'],
                   metaTitle=p['metaTitle'],metaDescription=p['description'],shortProductDescription=p['description'],
                   galleryLabels=p['galleryLabels'],galleryNote=p['galleryNote'],verifiedStructuredSpecifications=verified)
        copies[key]=dict(sku=sku,displayTitle=p['title'],metaTitle=p['metaTitle'],metaDescription=p['description'],
                         isFamilyFriendly=True,selectionAdvice=p['factNote'],projectUse=p['uses'],variantSizeNotes='')
        details[key]=p['caption']+' '+p['uses']
        additions.setdefault(p['category'],[]).append(row);pdp.append(entry)
        manifest.append(dict(sku=sku,pdp=row['pdp'],batchNumber=p['batchNumber'],sourceUrl=p['sourceUrl'],
                             sourceFields=p['sourceFields'],imageOutputs=p['qulaImageInfo']))
    for c in cat['categories']:
        c['products']=additions.get(c['slug'],[])+c['products'];c['productCount']=len(c['products'])
        for i,p in enumerate(c['products'],1):p['sortOrder']=i
    flat=[p for c in cat['categories'] for p in c['products']];index={p['pdp']:i for i,p in enumerate(flat,1)}
    for e in pdp:e['catalogIndex']=index['p-'+e['assetKey']+'.html']
    cat.update(totalProducts=len(flat),totalImages=len(flat),generatedAt=DATE)
    for filename,data,indent in [('product-catalog.json',cat,1),('pdp-data.json',pdp,2),('pdp-copy.json',copies,2),('pdp-description-details.json',details,2)]:
        save_json(ROOT/'assets/data'/filename,data,indent)
    generator=(ROOT/'scripts/gen_pdp.py').read_text().split('# ---- 2)')[0]
    marker='for e in pdp:\n    sku, key';assert generator.count(marker)==1
    generator=generator.replace(marker,'for e in pdp:\n    if e["sku"] not in BATCH_SKUS: continue\n    sku, key')
    exec(compile(generator,str(ROOT/'scripts/gen_pdp.py'),'exec'),{'__file__':str(ROOT/'scripts/gen_pdp.py'),'BATCH_SKUS':selected})
    for p in products:
        path=ROOT/('p-'+p['key']+'.html');text=path.read_text()
        text=text.replace('full pricing comes back with your quote within 12&#8211;24 hours.','confirm your selected quantity, assortment and destination for a quotation.')
        path.write_text('\n'.join(line.rstrip() for line in text.splitlines())+'\n')
    for slug,rows in additions.items():
        path=ROOT/(slug+'.html');page=path.read_text();first=re.search(r'<article class="product-card"',page);assert first
        page=page[:first.start()]+''.join(card(row) for row in rows)+page[first.start():]
        def schema(m):
            v=json.loads(m[1])
            if v.get('@type')=='ItemList':v.update(numberOfItems=len(categories[slug]['products']),itemListElement=[catalog_list_item(p,i) for i,p in enumerate(categories[slug]['products'],1)])
            return '<script type="application/ld+json">'+json.dumps(v,ensure_ascii=False,separators=(',',':'))+'</script>'
        page=re.sub(r'<script type="application/ld\+json">(.*?)</script>',schema,page,flags=re.S);path.write_text(page)
    xml=(ROOT/'sitemap.xml').read_text()
    for p in products:
        loc=BASE+'p-'+p['key']+'.html';assert loc not in xml
        node='<url><loc>'+loc+'</loc><lastmod>'+DATE+'</lastmod><changefreq>monthly</changefreq><priority>0.7</priority>'+''.join('<image:image><image:loc>'+BASE+i+'</image:loc><image:title>'+html.escape(p['sku']+' '+p['title'])+'</image:title></image:image>' for i in p['qulaImages'])+'</url>'
        xml=xml.replace('</urlset>','  '+node+'\n</urlset>')
    (ROOT/'sitemap.xml').write_text(xml)
    for filename in ['llms-full.txt','llms.txt']:
        path=ROOT/filename;text=path.read_text().replace(f'{len(prior)} live stock items',f'{len(flat)} live stock items')
        if filename=='llms-full.txt':
            for slug,rows in additions.items():
                heading='## '+categories[slug]['name']+'\n';assert heading in text
                text=text.replace(heading,heading+''.join(f'- [{p["title"]}]({BASE+p["pdp"]}): SKU {p["sku"]} · dimensions and reference packing listed; MOQ by inquiry\n' for p in rows),1)
        path.write_text(text)
    now={p['pdp']:p for p in flat};nowpdp={p['assetKey']:p for p in pdp}
    for old in prior:assert {k:v for k,v in old.items() if k!='sortOrder'}=={k:v for k,v in now[old['pdp']].items() if k!='sortOrder'}
    for old in oldpdp:assert {k:v for k,v in old.items() if k!='catalogIndex'}=={k:v for k,v in nowpdp[old['assetKey']].items() if k!='catalogIndex'}
    save_json(ROOT/'docs/product-batch-manifest-20261029-monica-27.json',dict(date=DATE,batchCount=plan['batchCount'],batchSize=20,catalogCountBefore=len(prior),catalogCountAfter=len(flat),newProductCount=len(products),imageCount=3*len(products),products=manifest))
    print(json.dumps(dict(new=len(products),batches=plan['batchCount'],catalog=len(flat))))

if __name__=='__main__':main()
