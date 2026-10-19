"""Import the October 19 image supplement and owner material correction, preserving source values and existing SKUs."""
import argparse, copy, hashlib, html, json, re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote
from PIL import Image
from add_products_20261012 import card, save_json, sha256
from add_products_20261012_v3 import specs_from_source
from catalog_schema import catalog_list_item

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://www.qulacrafts.com/'
DATE = '2026-10-19'
PAGES = {'polymer-clay-slices':'polymer-clay-sprinkles.html','plastic-beads':'acrylic-beads.html','plastic-sequins':'glitter-sequins-fillers.html'}
QUOTE = {'resin-charms':'Resin Charms','polymer-clay-slices':'Polymer Clay Sprinkles','plastic-beads':'Acrylic Beads','keychain':'Keychains','jewelry-accessories':'Jewelry Accessories','pvc-plastic-charms':'Other','beads-for-pens':'Beads for Pens','slime-charms':'Slime Charms','plastic-sequins':'Glitter & Fillers'}
MIXED = 'RW20423/RW22336/RW22338'

def source_records(path):
    cells = json.loads(path.read_text())
    headers = list(cells[0].values())
    return {int(re.search(r'\d+',next(iter(row)))[0]):dict(zip(headers,row.values())) for row in cells[1:]}

def public_source_specs(raw, sku):
    plan = next(p for p in CURRENT_PLANS if p['sku'] == sku)
    specs={'Material': plan['material'], 'Size': plan['dimensions'], 'Attachment' if plan['category']=='keychain' else 'Hole': plan['attachment'], 'Standard pack':plan['packing']+'; custom packing by inquiry', 'Selection note':plan['factNote'], 'Assortment':'Mixed or single-color selection by inquiry' if '单色' in raw['颜色'] else 'Mixed assortment; selected designs by inquiry', 'Packing and MOQ':'Packing quantity is not the minimum order quantity. Confirm MOQ and dispatch date by inquiry.'}
    if len(plan['photos'])>1: specs['SKU group']='One grouped assortment. Specify the selected component codes and mixing proportions when requesting a quote.'
    if plan.get('sourceSkuCorrection'): specs['Original source code group']=plan['sourceSkuCorrection']['original']
    return specs

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--plan',type=Path,required=True)
    ap.add_argument('--source',type=Path,required=True)
    ap.add_argument('--baseline',required=True)
    args=ap.parse_args()
    global CURRENT_PLANS
    plans=json.loads(args.plan.read_text()); CURRENT_PLANS=plans; records=source_records(args.source)
    assert len(plans)==2 and {p['operation'] for p in plans}=={'new','update'}
    catpath=ROOT/'assets/data/product-catalog.json'; pdppath=ROOT/'assets/data/pdp-data.json'
    cat=json.loads(catpath.read_text()); pdp=json.loads(pdppath.read_text())
    copies=json.loads((ROOT/'assets/data/pdp-copy.json').read_text())
    details=json.loads((ROOT/'assets/data/pdp-description-details.json').read_text())
    oldcat=copy.deepcopy(cat); oldpdp=copy.deepcopy(pdp)
    previousSchemas={}
    for plan in plans:
        if plan['operation']=='update':
            previousSchemas[plan['sku']]=[m[0] for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>',(ROOT/f'p-{plan["key"]}.html').read_text(),re.S) if json.loads(m[1]).get('@type') in {'Organization','WebSite'}]
    oldflat=[p for c in cat['categories'] for p in c['products']]
    assert len(oldflat)==416
    byslug={c['slug']:c for c in cat['categories']}; bysku={p['sku']:p for p in oldflat}
    pdpbykey={p['assetKey']:p for p in pdp}; additions={}; changed=[]; manifest=[]; batch={p['sku'] for p in plans}
    for plan in plans:
        sku,key=plan['sku'],plan['key']; raw=records[plan['sourceRow']]
        source_sku=str(raw['sku']).strip()
        effective_sku=plan.get('sourceSkuCorrection',{}).get('normalized',source_sku)
        assert effective_sku==sku
        images=plan['imagesLocal']; assert len(images)==len(set(images))==len(plan['galleryLabels'])
        imageinfo=[]
        for n,rel in enumerate(images,1):
            with Image.open(ROOT/rel) as im:
                w,h=im.size; assert 0<w<=1000 and not im.getexif()
            imageinfo.append({'path':rel,'role':plan['galleryLabels'][n-1],'width':w,'height':h,'sha256':sha256(ROOT/rel),'bytes':(ROOT/rel).stat().st_size,'origin':('brand-neutral edited styling reference' if n==1 and plan['sku'] in {'RX327','YX3257','YX354','YX194','CDK518-1/CDK26511-3/CDK26511-1/CDK004217-1/CDK26511-2'} else plan['imageOrigins'][n-1])})
        w,h=imageinfo[0]['width'],imageinfo[0]['height']
        category=byslug[plan['category']]
        if plan['operation']=='new':
            assert sku not in bysku
            row={'category':category['name'],'categorySlug':category['slug'],'sourceSheet':'Sheet1','sourceRow':plan['sourceRow'],'sortOrder':0,'sku':sku,'title':plan['title'],'titleFull':plan['title'],'titleShort':plan['title'],'sourceTitle':raw['标题'],'sourceCategory':raw['分类'],'alibabaUrl':'','cleanAlibabaUrl':'','alibabaProductId':'','status':'ok','anchorNote':'','pdp':f'p-{key}.html'}
            entry={'catalogIndex':0,'assetKey':key,'sku':sku,'category':category['name'],'categorySlug':category['slug'],'url':'','status':'ok','reason':'','titleFull':raw['标题'],'moq':'','priceTiers':[],'stockStatus':'In stock; confirm the available quantity with your quote','specs':public_source_specs(raw,sku),'images':[],'sourceWorkbook':'10.11(20261019-032556).xlsx','sourceSheet':'Sheet1','sourceRow':plan['sourceRow'],'sourceFields':raw,'sourceSkuCorrection':plan.get('sourceSkuCorrection'),'importedAt':datetime.now(timezone.utc).isoformat(),'metaTitle':plan['metaTitle'],'metaDescription':plan['description'],'shortProductDescription':plan['description']}
            copies[key]={'sku':sku,'displayTitle':plan['title'],'metaTitle':plan['metaTitle'],'metaDescription':plan['description'],'isFamilyFriendly':True}; details[key]=plan['description']+' '+plan['uses']+' Confirm the selected designs, assortment, sample and destination when requesting a wholesale quote.'
            additions.setdefault(category['slug'],[]).append(row); pdp.append(entry)
        else:
            row=bysku[sku]; entry=pdpbykey[key]
            entry.update(specs=public_source_specs(raw,sku),priceTiers=[],moq='',sourceWorkbook='10.11(20261019-032556).xlsx',sourceRow=plan['sourceRow'],sourceSheet='Sheet1',sourceFields=raw,stockStatus='In stock; confirm current available quantity by inquiry')
            if sku=='YA012': entry.update(priceTiers=[],moq='')
        row.update(image=images[0],imageAlt=sku+' '+row['title'],imageWidth=w,imageHeight=h,imageHash=hashlib.md5((ROOT/images[0]).read_bytes()).hexdigest())
        row['inquiryUrl']=f'quote.html?product={quote(sku+" "+row["title"],safe="")}&sku={quote(sku,safe="")}&image={quote(images[0],safe="/")}&category={quote(QUOTE[category["slug"]],safe="")}'
        if sku=='FHA044': entry['ownerMaterialConfirmation']={'date':'2026-10-19','material':'Plastic','source':'Owner explicitly confirmed FHA044 material in conversation; original workbook field retained.'}
        entry['metaDescription']=plan['description']
        copies[key]['metaDescription']=plan['description']
        details[key]=plan['description']+' '+plan['factNote']
        entry['imagesLocal']=images; changed.append((plan,row,entry))
        manifest.append({'sku':sku,'operation':plan['operation'],'sourceRow':plan['sourceRow'],'sourceFields':raw,'sourceReferences':plan.get('sourceReferences',[{'file':plan['source'],'sha256':plan['sourceImageSha256']}]),'pdp':row['pdp'],'imageOutputs':imageinfo})
    for c in cat['categories']:
        c['products']=additions.get(c['slug'],[])+c['products']; c['productCount']=len(c['products'])
        for i,p in enumerate(c['products'],1):p['sortOrder']=i
    flat=[p for c in cat['categories'] for p in c['products']]; index={p['pdp']:i for i,p in enumerate(flat,1)}
    for e in pdp:e['catalogIndex']=index[f'p-{e["assetKey"]}.html']
    cat.update(totalProducts=len(flat),totalImages=len(flat),generatedAt=datetime.now(timezone.utc).isoformat())
    assert len(flat)==417
    for p,v,indent in [(catpath,cat,1),(pdppath,pdp,2),(ROOT/'assets/data/pdp-copy.json',copies,2),(ROOT/'assets/data/pdp-description-details.json',details,2)]:save_json(p,v,indent)
    # Use dimensions from previously approved HTML for existing related images.
    dimensions={}
    for p in ROOT.glob('*.html'):
        for tag in re.findall(r'<img\b[^>]+>',p.read_text()):
            attrs=dict(re.findall(r'(src|width|height)="([^"]*)"',tag))
            if all(k in attrs for k in ['src','width','height']):dimensions[attrs['src']]=(int(attrs['width']),int(attrs['height']))
    generator=(ROOT/'scripts/gen_pdp.py').read_text().split('# ---- 2)')[0]
    generator=generator.replace('for e in pdp:\n    sku, key','for e in pdp:\n    if e["sku"] not in BATCH_SKUS: continue\n    sku, key')
    generator=generator.replace('def img_dim(rel):','def img_dim(rel):\n    if not (SITE / rel).exists() and rel in APPROVED_DIMS: return APPROVED_DIMS[rel]')
    exec(compile(generator,str(ROOT/'scripts/gen_pdp.py'),'exec'),{'__file__':str(ROOT/'scripts/gen_pdp.py'),'BATCH_SKUS':batch,'APPROVED_DIMS':dimensions})
    for plan,row,e in changed:
        pagepath=ROOT/row['pdp']; page=pagepath.read_text()

        for number,label in enumerate(plan['galleryLabels'][1:],2): page=page.replace('detail view '+str(number),label)
        if True:
            page=page.replace('Decorative craft material — non-edible. Batch test reports (EN 71, ASTM F963, CPC, REACH) available on request.','Confirm the selected assortment, minimum order quantity and dispatch date with your inquiry.')
            page,n=re.subn(r'<div class="answer-box" style="margin:14px 0">.*?</div>','<div class="answer-box" style="margin:14px 0"><b>Wholesale pricing by quotation</b> · Minimum order quantity confirmed by inquiry.</div>',page,count=1,flags=re.S);assert n==1
        note=plan['galleryNote']
        marker='</div>\n<div>\n  <div class="answer-box"';assert marker in page
        page=page.replace(marker,'<p class="pdp-image-note" style="font-size:.85rem;color:#667085">'+note+' Props are not included; confirm selected designs and assortment before ordering.</p>'+marker,1)
        page,n=re.subn(r'quote\.html\?product=[^"<>]+',html.escape(row['inquiryUrl'],quote=True),page,count=1);assert n==1
        if row['sku'] in {'CZB26813','CZB26818','CZB26846'}:
            marker='</div>\n</section>'
            # Public specs already state that a stringing hole is not a fit guarantee.
            assert 'diameter not supplied' in page
        def entity_refs(m):
            schema=json.loads(m[1])
            if schema.get('@type')=='Product':
                schema['manufacturer']={'@id':BASE+'#organization'}
                if schema.get('offers'): schema['offers']['seller']={'@id':BASE+'#organization'}
            return '<script type="application/ld+json">'+json.dumps(schema,ensure_ascii=False,separators=(',',':'))+'</script>'
        page=re.sub(r'<script type="application/ld\+json">(.*?)</script>',entity_refs,page,flags=re.S)
        page=page.replace('</head>',''.join(previousSchemas.get(row['sku'],[]))+'</head>')
        pagepath.write_text('\n'.join(line.rstrip() for line in page.splitlines())+'\n')
    for slug in {p['category'] for p in plans}:
        path=ROOT/PAGES.get(slug,slug+'.html');page=path.read_text()
        updates={row['sku']:row for plan,row,e in changed if plan['operation']=='update' and plan['category']==slug}
        def update_card(m):
            s=html.unescape(re.search(r'<span class="pill soft">([^<]+)',m[0])[1])
            return card(updates[s]) if s in updates else m[0]
        page=re.sub(r'<article class="product-card"[^>]*>.*?</article>',update_card,page,flags=re.S)
        first=re.search(r'<article class="product-card"',page);assert first
        page=page[:first.start()]+''.join(card(p) for p in additions.get(slug,[]))+page[first.start():]
        def schema(m):
            v=json.loads(m[1])
            if v.get('@type')=='ItemList':v.update(numberOfItems=len(byslug[slug]['products']),itemListElement=[catalog_list_item(p,i) for i,p in enumerate(byslug[slug]['products'],1)])
            return '<script type="application/ld+json">'+json.dumps(v,ensure_ascii=False,separators=(',',':'))+'</script>'
        page=re.sub(r'<script type="application/ld\+json">(.*?)</script>',schema,page,flags=re.S);path.write_text(page)
    xml=(ROOT/'sitemap.xml').read_text()
    for plan,row,e in changed:
        loc=BASE+row['pdp'];node='<url><loc>'+loc+'</loc><lastmod>'+DATE+'</lastmod><changefreq>monthly</changefreq><priority>0.7</priority>'+''.join(f'<image:image><image:loc>{BASE+p}</image:loc><image:title>{html.escape(row["sku"]+" "+row["title"])}</image:title></image:image>' for p in e['imagesLocal'])+'</url>'
        if plan['operation']=='new':assert loc not in xml;xml=xml.replace('</urlset>','  '+node+'\n</urlset>')
        else:xml,n=re.subn(r'<url>\s*<loc>'+re.escape(loc)+r'</loc>.*?</url>',lambda m:node,xml,flags=re.S);assert n==1
    (ROOT/'sitemap.xml').write_text(xml)
    for filename in ['llms-full.txt','llms.txt']:
        path=ROOT/filename;text=path.read_text().replace('416 live stock items','417 live stock items')
        if filename=='llms-full.txt':
            for slug,rows in additions.items():
                heading='## '+byslug[slug]['name']+'\n';assert heading in text
                text=text.replace(heading,heading+''.join(f'- [{p["title"]}]({BASE+p["pdp"]}): SKU {p["sku"]} · packing, MOQ and pricing by inquiry\n' for p in rows),1)
        path.write_text(text)
    protected={'sortOrder','image','imageAlt','imageWidth','imageHeight','imageHash','inquiryUrl'}
    now={p['pdp']:p for p in flat}
    for p in oldflat:
        ignored=protected if p['sku'] in batch else {'sortOrder'}
        assert {k:v for k,v in p.items() if k not in ignored}=={k:v for k,v in now[p['pdp']].items() if k not in ignored},p['sku']
    for old in oldpdp:
        cur=next(e for e in pdp if e['assetKey']==old['assetKey']);ignored={'catalogIndex','imagesLocal','specs','sourceWorkbook','sourceRow','sourceSheet','sourceFields','stockStatus','priceTiers','moq','metaDescription'} if old['sku'] in batch else {'catalogIndex'}
        assert {k:v for k,v in old.items() if k not in ignored}=={k:v for k,v in cur.items() if k not in ignored},old['sku']
    save_json(ROOT/'docs/product-batch-manifest-20261019-supplement.json',{'batchId':'qula-products-20261019-supplement','baselineCommit':args.baseline,'newProductCount':1,'updatedProductCount':1,'catalogCountBefore':416,'catalogCountAfter':417,'imageCount':6,'sourceWorkbook':'10.11(20261019-032556).xlsx','products':manifest})
    print(json.dumps({'new':1,'updated':1,'catalog':417,'images':6}))

if __name__=='__main__':main()
