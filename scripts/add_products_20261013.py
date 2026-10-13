"""Import the 10.13 supplied-photo batch, preserving source values and existing SKUs."""
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
DATE = '2026-10-13'
PAGES = {'polymer-clay-slices':'polymer-clay-sprinkles.html','plastic-beads':'acrylic-beads.html'}
QUOTE = {'resin-charms':'Resin Charms','polymer-clay-slices':'Polymer Clay Sprinkles','plastic-beads':'Acrylic Beads','keychain':'Keychains','pvc-plastic-charms':'Other','beads-for-pens':'Beads for Pens'}
MIXED = 'RW20423/RW22336/RW22338'

def source_records(path):
    cells = json.loads(path.read_text())
    headers = list(cells[0].values())
    return {int(re.search(r'\d+',next(iter(row)))[0]):dict(zip(headers,row.values())) for row in cells[1:]}

def public_source_specs(raw, sku):
    specs = specs_from_source(raw)
    if sku == MIXED:
        specs['Material'] = 'Resin antler components and plastic black hats; confirm composition per design'
        specs.pop('Size', None)
        specs['Size reference'] = '24 × 15 mm source reference; confirm each antler and hat design size by inquiry'
        specs['Mix components'] = 'RW20423 antlers / RW22336 antlers / RW22338 miniature black hats'
        specs['Assortment'] = 'Mixed product; confirm the selected designs and mixing ratio by inquiry'
        specs['Hole'] = 'No stringing hole specified; confirm attachment requirements per design'
    elif sku == 'YX3803':
        specs['Material'] = 'Polymer clay slices with mixed decorative fillers; confirm component composition'
        specs['Hole'] = 'Configuration varies by included component; confirm the selected mix by inquiry'
    elif sku == 'YX3242':
        specs['Hole'] = 'Confirm component openings and attachment requirements by inquiry'
    if '/' in sku or sku == 'RW2504-YX416':
        specs['SKU group'] = 'Grouped assortment; confirm selected designs and mix by inquiry'
    return specs

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--plan',type=Path,required=True)
    ap.add_argument('--source',type=Path,required=True)
    ap.add_argument('--baseline',required=True)
    args=ap.parse_args()
    plans=json.loads(args.plan.read_text()); records=source_records(args.source)
    assert len(plans)==20 and sum(p['operation']=='new' for p in plans)==18
    catpath=ROOT/'assets/data/product-catalog.json'; pdppath=ROOT/'assets/data/pdp-data.json'
    cat=json.loads(catpath.read_text()); pdp=json.loads(pdppath.read_text())
    copies=json.loads((ROOT/'assets/data/pdp-copy.json').read_text())
    details=json.loads((ROOT/'assets/data/pdp-description-details.json').read_text())
    oldcat=copy.deepcopy(cat); oldpdp=copy.deepcopy(pdp)
    oldflat=[p for c in cat['categories'] for p in c['products']]
    assert len(oldflat)==274
    byslug={c['slug']:c for c in cat['categories']}; bysku={p['sku']:p for p in oldflat}
    pdpbykey={p['assetKey']:p for p in pdp}; additions={}; changed=[]; manifest=[]; batch={p['sku'] for p in plans}
    for plan in plans:
        sku,key=plan['sku'],plan['key']; raw=records[plan['sourceRow']]
        assert str(raw['sku']).strip()==sku
        images=plan['imagesLocal']; assert len(images)==len(set(images))==3
        imageinfo=[]
        for n,rel in enumerate(images,1):
            with Image.open(ROOT/rel) as im:
                w,h=im.size; assert 0<w<=1000 and not im.getexif()
            imageinfo.append({'path':rel,'role':['main','scene','detail'][n-1],'width':w,'height':h,'sha256':sha256(ROOT/rel),'bytes':(ROOT/rel).stat().st_size,'origin':'AI-assisted composition from three verified references' if sku==MIXED and n==1 else 'supplied reference' if n==1 else 'AI-assisted styling illustration'})
        w,h=imageinfo[0]['width'],imageinfo[0]['height']
        category=byslug[plan['category']]
        if plan['operation']=='new':
            assert sku not in bysku
            row={'category':category['name'],'categorySlug':category['slug'],'sourceSheet':'Sheet1','sourceRow':plan['sourceRow'],'sortOrder':0,'sku':sku,'title':plan['title'],'titleFull':plan['title'],'titleShort':plan['title'],'sourceTitle':raw['标题'],'sourceCategory':raw['分类'],'alibabaUrl':'','cleanAlibabaUrl':'','alibabaProductId':'','status':'ok','anchorNote':'','pdp':f'p-{key}.html'}
            entry={'catalogIndex':0,'assetKey':key,'sku':sku,'category':category['name'],'categorySlug':category['slug'],'url':'','status':'ok','reason':'','titleFull':raw['标题'],'moq':'','priceTiers':[],'stockStatus':'In stock; confirm the available quantity with your quote','specs':public_source_specs(raw,sku),'images':[],'sourceWorkbook':'10.11(4).xlsx','sourceSheet':'Sheet1','sourceRow':plan['sourceRow'],'sourceFields':raw,'importedAt':datetime.now(timezone.utc).isoformat(),'metaTitle':plan['metaTitle'],'metaDescription':plan['description'],'shortProductDescription':plan['description']}
            copies[key]={'sku':sku,'displayTitle':plan['title'],'metaTitle':plan['metaTitle'],'metaDescription':plan['description'],'isFamilyFriendly':True}; details[key]=plan['description']
            additions.setdefault(category['slug'],[]).append(row); pdp.append(entry)
        else:
            row=bysku[sku]; entry=pdpbykey[key]
        row.update(image=images[0],imageAlt=sku+' '+row['title'],imageWidth=w,imageHeight=h,imageHash=hashlib.md5((ROOT/images[0]).read_bytes()).hexdigest())
        row['inquiryUrl']=f'quote.html?product={quote(sku+" "+row["title"],safe="")}&sku={quote(sku,safe="")}&image={quote(images[0],safe="/")}&category={quote(QUOTE[category["slug"]],safe="")}'
        entry['imagesLocal']=images; changed.append((plan,row,entry))
        manifest.append({'sku':sku,'operation':plan['operation'],'sourceRow':plan['sourceRow'],'sourceFields':raw,'sourceReferences':plan.get('sourceReferences',[{'file':plan['source'],'sha256':plan['sourceImageSha256']}]),'pdp':row['pdp'],'imageOutputs':imageinfo})
    for c in cat['categories']:
        c['products']=additions.get(c['slug'],[])+c['products']; c['productCount']=len(c['products'])
        for i,p in enumerate(c['products'],1):p['sortOrder']=i
    flat=[p for c in cat['categories'] for p in c['products']]; index={p['pdp']:i for i,p in enumerate(flat,1)}
    for e in pdp:e['catalogIndex']=index[f'p-{e["assetKey"]}.html']
    cat.update(totalProducts=len(flat),totalImages=len(flat),generatedAt=datetime.now(timezone.utc).isoformat())
    assert len(flat)==292
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
        page=page.replace('detail view 2','styled scene illustration').replace('detail view 3','styled detail illustration')
        if plan['operation']=='new':
            page=page.replace('Decorative craft material — non-edible. Batch test reports (EN 71, ASTM F963, CPC, REACH) available on request.','Confirm the selected assortment, minimum order quantity and dispatch date with your inquiry.')
            page,n=re.subn(r'<div class="answer-box" style="margin:14px 0">.*?</div>','<div class="answer-box" style="margin:14px 0"><b>Wholesale pricing by quotation</b> · Minimum order quantity confirmed by inquiry.</div>',page,count=1,flags=re.S);assert n==1
        note='Images 1–3: compositions and styling illustrations based on the three verified product references.' if row['sku']==MIXED else 'Image 1: supplied product reference. Images 2–3: styled illustrations.'
        marker='</div>\n<div>\n  <div class="answer-box"';assert marker in page
        page=page.replace(marker,'<p class="pdp-image-note" style="font-size:.85rem;color:#667085">'+note+' Props are not included; confirm selected designs and assortment before ordering.</p>'+marker,1)
        page,n=re.subn(r'quote\.html\?product=[^"<>]+',html.escape(row['inquiryUrl'],quote=True),page,count=1);assert n==1
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
        path=ROOT/filename;text=path.read_text().replace('274 live stock items','292 live stock items')
        if filename=='llms-full.txt':
            for slug,rows in additions.items():
                heading='## '+byslug[slug]['name']+'\n';assert heading in text
                text=text.replace(heading,heading+''.join(f'- [{p["title"]}]({BASE+p["pdp"]}): SKU {p["sku"]} · packing, MOQ and pricing by inquiry\n' for p in rows),1)
        path.write_text(text)
    protected={'sortOrder','image','imageAlt','imageWidth','imageHeight','imageHash','inquiryUrl'}
    now={p['pdp']:p for p in flat}
    for p in oldflat:
        ignored=protected if p['sku'] in {'RW24891','RW20175'} else {'sortOrder'}
        assert {k:v for k,v in p.items() if k not in ignored}=={k:v for k,v in now[p['pdp']].items() if k not in ignored},p['sku']
    for old in oldpdp:
        cur=next(e for e in pdp if e['assetKey']==old['assetKey']);ignored={'catalogIndex','imagesLocal'} if old['sku'] in {'RW24891','RW20175'} else {'catalogIndex'}
        assert {k:v for k,v in old.items() if k not in ignored}=={k:v for k,v in cur.items() if k not in ignored},old['sku']
    save_json(ROOT/'docs/product-batch-manifest-20261013.json',{'batchId':'qula-products-20261013','baselineCommit':args.baseline,'newProductCount':18,'updatedProductCount':2,'catalogCountBefore':274,'catalogCountAfter':292,'imageCount':60,'userClarification':'RW20423/RW22336/RW22338 is one mixed product of two antler styles and existing black miniature hats; use the full mixed SKU.','products':manifest})
    print(json.dumps({'new':18,'updated':2,'catalog':292,'images':60}))

if __name__=='__main__':main()
