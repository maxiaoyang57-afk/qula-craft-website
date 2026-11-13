#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TITLES = {
    'RW25974': 'Rainbow Gummy Resin Flatbacks | RW25974',
    'RW002817': 'Gradient Bow Resin Flatbacks | RW002817',
    'RW6015': '7 mm Translucent Flower Resin Flatbacks | RW6015',
    'RW1613': 'Soft-Serve Resin Miniatures | RW1613',
    'RW692': 'Heart Cupcake Resin Miniatures | RW692',
    'RW1824': 'Glitter Star Resin Flatbacks | RW1824',
    'RW001724': 'Mini Macaron Resin Decorations | RW001724',
    'RW26131': 'Candied Fruit Skewer Resin Flatbacks | RW26131',
    'RW312': 'Glitter Crescent Moon Resin Flatbacks | RW312',
    'RW25542': 'Mini Waffle Cookie Resin Flatbacks | RW25542',
    'RW3598': 'Glitter Scallop Shell Resin Flatbacks | RW3598',
    'RW002712': 'Heart Biscuit Resin Flatbacks | RW002712',
    'RW25867': 'Mini Strawberry Resin Pieces | RW25867',
    'RW3345': 'Christmas Candy Resin Flatbacks | RW3345',
    'RW26091': 'Pastel Heart Resin Flatbacks | RW26091',
    'RW25671': 'Tropical Flip-Flop Resin Miniatures | RW25671',
    'RW004005': 'Pastel Popsicle Resin Flatbacks | RW004005',
    'RW3251': 'Translucent Gummy Bear Resin Flatbacks | RW3251',
    'RW004343': 'Snowflake Heart Resin Flatbacks | RW004343',
    'RW26114': 'Fruit Butterfly Resin Flatbacks | RW26114',
}

plan_path = ROOT / 'scripts/data/monica-reviewed-batch-44-20261113.json'
plan = json.loads(plan_path.read_text())
for product in plan['products']:
    product['metaTitle'] = TITLES[product['sku']]
plan_path.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + '\n')

pdp_path = ROOT / 'assets/data/pdp-data.json'
pdp = json.loads(pdp_path.read_text())
for product in pdp:
    if product['sku'] in TITLES:
        product['metaTitle'] = TITLES[product['sku']]
pdp_path.write_text(json.dumps(pdp, ensure_ascii=False, indent=2) + '\n')

copy_path = ROOT / 'assets/data/pdp-copy.json'
copies = json.loads(copy_path.read_text())
for key, product in copies.items():
    if product.get('sku') in TITLES:
        product['metaTitle'] = TITLES[product['sku']]
copy_path.write_text(json.dumps(copies, ensure_ascii=False, indent=2) + '\n')

selected = set(TITLES)
generator = (ROOT / 'scripts/gen_pdp.py').read_text().split('# ---- 2)')[0]
marker = 'for e in pdp:\n    sku, key'
assert generator.count(marker) == 1
generator = generator.replace(marker, 'for e in pdp:\n    if e["sku"] not in BATCH_SKUS: continue\n    sku, key')
exec(compile(generator, str(ROOT / 'scripts/gen_pdp.py'), 'exec'), {'__file__': str(ROOT / 'scripts/gen_pdp.py'), 'BATCH_SKUS': selected})

for sku in selected:
    path = ROOT / ('p-' + sku.lower() + '.html')
    text = path.read_text().replace(
        'full pricing comes back with your quote within 12&#8211;24 hours.',
        'confirm your selected quantity, assortment and destination for a quotation.',
    )
    path.write_text('\n'.join(line.rstrip() for line in text.splitlines()) + '\n')

print(json.dumps({'updated': len(selected), 'max_title_length': max(map(len, TITLES.values()))}))
