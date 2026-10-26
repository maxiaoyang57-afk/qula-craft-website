"""Prepare reviewed owner-captured products; never infer missing dimensions or MOQ."""
import argparse, hashlib, json, re
from pathlib import Path

# Display names are edited for clarity. The original marketplace title is retained.
TITLES = {
'RW26723':'Artist Palette and Paint Brush Resin Charms',
'RW26722':'Ladybug on Leaf Resin Charms',
'SLM613':'Butterfly and Lollipop Slime Decoration Mix',
'SLM615':'Bear and Heart Slime Decoration Mix',
'SLM603':'Rose Flower Resin and Clay Slime Decoration Mix',
'SLM10009-1':'Christmas Slime Decoration Sprinkles Mix',
'RW26719':'Colorful Candy Resin Cabochons',
'RW26718':'Chocolate Bowl Dessert Resin Cabochons',
'RW26717':'Sleeping Cat Resin Cabochons',
'RW26716':'Lemon Fruit Resin Cabochons',
'RW1959':'Miniature Fruit Trees and Lotus Pond Ornaments',
'SLM10060':'Valentine Rose Heart and Lip Slime Decoration Mix',
'SLM10058':'Sea Theme Slime Decoration Mix',
'RW24466':'Miniature Tree Resin Flatback Cabochons',
'SLM600':'Slime Decoration Kit with Tools and Containers',
'SLM612':'Mermaid Tail and Pearl Slime Decoration Mix',
'RW5191':'Miniature Baking Tool Accessories',
'RW5003':'Miniature Wooden Broom Models',
'RW3595':'Miniature Squirrel Figurines',
'RW5323':'Miniature Ceramic Casserole Models',
'RW4549':'Miniature Resin Coffee Cup Models',
'RW24634':'Miniature Bread Resin Cabochons',
'RW3092':'Miniature Resin Takeaway Cup Models',
'RW26099':'Bear Star and Dog Resin Cabochons',
'RW5354':'Miniature Tree Stump Resin Figurines',
'RW5709':'Miniature Kitchen Appliance Models',
'RW5150':'Miniature Metal Cutlery Accessories',
'RW5090':'Miniature Potted Succulent Models',
'RW5309':'Miniature Folding Chair Phone Holders',
'RW1514':'Mushroom Fairy Garden Resin Miniatures',
'RW5147':'Miniature Breakfast Tableware and Food Set',
'RW5271':'Miniature Egg and Basket Models',
'RW5410':'Miniature Waste Bin Models',
'RW3859':'Miniature Beach Scene Accessories',
'RW5050':'Miniature Handbag Models',
'RW5236':'Miniature Bicycle Models',
'RW5154':'Miniature Television Display Models',
'RW5256':'Miniature Violin and Bow Models',
'RW003022':'Macaron Resin Pendant Charms',
'RW5104':'Miniature Colorful Bucket Models',
'RW5143':'Miniature Alloy Cooking Pan Models',
'RW5117':'Miniature Caviar Dish and Spoon Models',
}
NOTES = {
'RW26723':'Palette, paint tube and brush designs have separate source size options; confirm which option and assortment is required.',
'RW1959':'Source option 1 lists 23 × 23 × 30 mm; option 2 lists 7 × 31 × 40 mm. Confirm the exact design-to-option mapping before ordering.',
'RW1514':'Source size options 1–6: 20 × 22 × 30; 21 × 26 × 30; 24 × 24 × 25; 18 × 24 × 28; 11 × 11 × 18; 14 × 24 × 30 mm. Confirm the selected design and size option.',
'RW26099':'The source lists an approximate 27 mm size. Dimensions can differ by shape; confirm the selected design.',
'RW5256':'The source title mentions both plastic and wood. Material composition is left for confirmation instead of choosing either claim.',
'RW5709':'Decorative kitchen appliance models. Confirm included pieces; working electronics are not specified.',
'RW5154':'Decorative miniature television model. Confirm included display papers and accessories; electronic operation is not specified.',
'RW5050':'Miniature handbag models for decorative scenes. Confirm material composition and the selected colors.',
'SLM600':'Confirm the included containers, tools and decorative fillers. Slime base ingredients are not specified.',
'SLM10009-1':'The source title lists 1 kg; confirm the sales pack, included shapes and mixture before ordering.',
'SLM10058':'The captured option lists 500 g per bag. Confirm the selected components and mix.',
'SLM10060':'The captured option lists 30 g per bag. Confirm the selected components and mix.',
}


def source_material(r):
    if r.get('material'): return r['material'], 'captured material field'
    text = r['title'].lower()
    if r['sku'] == 'RW5256': return 'Confirm material composition by inquiry', 'source title contains conflicting plastic/wood claims'
    if r['sku'].startswith('SLM'):
        return 'Mixed decorative components; confirm composition by inquiry', 'source title and reference image describe a decoration mix'
    for token, value in [('resin','Resin'),('wooden','Wood'),('ceramic','Ceramic'),('alloy','Alloy'),('metal ','Metal'),('iron ','Iron'),('plastic','Plastic')]:
        if token in text: return value, 'explicit material wording in captured product title'
    return 'Confirm material composition by inquiry', 'not supplied in captured attributes'


def make_plans(source, scratch):
    records = [r for r in json.loads(source.read_text())['records'] if r.get('_detail_collected') and r['sku'] != 'RW26724']
    plans=[]
    for r in records:
        sku=r['sku']; title=TITLES[sku]; key=sku.lower(); material,basis=source_material(r)
        dimensions=r.get('size','').replace('*',' × ').replace('mm',' mm').strip().rstrip('-')
        if sku=='RW26723': dimensions='14 × 23 mm / 5 × 14 mm / 18 × 25 mm'
        if sku=='RW26099': dimensions='Approx. 27 mm; confirm dimensions by design'
        if not dimensions: dimensions='Confirm dimensions by inquiry'
        packing=re.sub(r'(\d+)pcs/bag',r'\1 pieces per bag',r.get('packaging',''))
        if sku=='SLM10060': packing='30 g per bag'
        if sku=='SLM10058': packing='500 g per bag'
        if not packing: packing='Confirm pack quantity and format by inquiry'
        # Retain same-product scrape evidence only when the retrieved title agrees
        # with the captured source title. Region-blocked recommendation pages fail.
        live=scratch/(sku+'-scrape.json');verified=None
        if live.exists():
            data=json.loads(live.read_text());j=data.get('json') or {}; t=re.sub(r'\W+',' ',j.get('title','').lower()).strip();raw=re.sub(r'\W+',' ',r['title'].lower()).strip()
            if len(t)>20 and (t in raw or raw in t):
                verified=j
                if material.startswith('Confirm') and j.get('material') and sku!='RW5256':material=j['material'];basis='matching same-product live page attributes'
                if dimensions.startswith('Confirm') and j.get('dimensions'):dimensions=j['dimensions'].replace('*',' × ')
                if packing.startswith('Confirm') and j.get('packing'):packing=re.sub(r'(\d+)pcs/bag',r'\1 pieces per bag',j['packing'])
        category='slime-charms' if sku.startswith('SLM') else 'resin-charms'
        haibu=sku.startswith('SLM') or material=='Resin'
        note=NOTES.get(sku,'Decorative craft reference designs are shown. Confirm the selected design, colors and assortment; styling props are not included.')
        if sku=='RW5003':dimensions='15 × 50 mm / 15 × 95 mm; confirm selected option'
        uses=('Slime decoration, themed filler assortments and DIY craft kits.' if sku.startswith('SLM') else 'Miniature scenes, craft embellishment and decorative display projects.')
        description=f'Wholesale {title.lower()}. SKU {sku}. Confirm selected designs, specifications, packing and MOQ by inquiry.'
        assert 80<=len(description)<=160,(sku,len(description))
        source_fields={k:r.get(k,'') for k in ['sku','sku_raw','title','material','size','packaging','moq','attributes']}
        p=dict(sku=sku,key=key,title=title,metaTitle=f'{sku} {title} | Qula',category=category,haibuCategory=category,haibu=haibu,type='Decorative',keywords=re.sub(r'[^a-z0-9]+','-',title.lower()).strip('-'),material=material,materialBasis=basis,dimensions=dimensions,packing=packing,attachment='Confirm attachment method by inquiry',description=description,factNote=note,uses=uses,operation='new',sourceFields=source_fields,sourceProductId=r['product_id'],sourceUrl=r['product_url'],sourceImageUrl=r['images'][0],verifiedLiveSource=verified,galleryLabels=['Product reference','Specification guide','Packing and selection guide'],imageOrigins=['original same-SKU product image; brand badge removed where present','exact source specification graphic','exact source packing and inquiry graphic'],galleryNote='The first image is a product reference. The following images are specification and ordering guides, not additional product angles. Confirm included designs and assortment; props are not included.')
        plans.append(p)
    assert len(plans)==42
    return plans


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,required=True);ap.add_argument('--evidence',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
    plans=make_plans(a.source,a.evidence);a.output.write_text(json.dumps(plans,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(dict(products=len(plans),haibu=sum(p['haibu'] for p in plans),qula=len(plans),explicit_size=sum(not p['dimensions'].startswith('Confirm') for p in plans))))
