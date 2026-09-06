# -*- coding: utf-8 -*-
"""Restore the verified 2026-09-05 product upload into the QULA catalog.

The source workbook and ZIP contain three matching SKUs. This migration is
idempotent and deliberately leaves unknown commercial fields blank.
"""
import hashlib
import html
import json
import re
from pathlib import Path
from urllib.parse import quote

SITE = Path(__file__).resolve().parents[1]
CATALOG_PATH = SITE / "assets/data/product-catalog.json"
PDP_PATH = SITE / "assets/data/pdp-data.json"
CATEGORY_PAGE = SITE / "resin-charms.html"
BASE = "https://www.qulacrafts.com/"

PRODUCTS = [
    {
        "sku": "RW967",
        "key": "rw967",
        "title": "Resin Fried Egg 1:12 White Egg Flatback Miniature Food Cabochons for DIY Scrapbooking",
        "size": "35*31*8mm",
        "packing": "100PCS/bag",
        "source_row": 2,
    },
    {
        "sku": "RW474",
        "key": "rw474",
        "title": "100PCS Resin Mixed Sweet Candy Charms Artificial Food Slime Parts Jewelry Making Accessory Home Table Decor",
        "size": "24mm*15mm",
        "packing": "100PCS/bag",
        "source_row": 3,
    },
    {
        "sku": "RW326",
        "key": "rw326",
        "title": "100pcs DIY Resin Drink Jam Jars Charms Hand Made Accessories Fun Fruit Personal Earrings Pendant Material Earrings Finding",
        "size": "",
        "packing": "100PCS/bag",
        "source_row": 4,
    },
]


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path, value):
    # Preserve the repository's existing formatting to keep reviews focused.
    indent = 2 if path == PDP_PATH else 1
    path.write_text(json.dumps(value, ensure_ascii=False, indent=indent) + "\n", encoding="utf-8")


def image_hash(rel):
    return hashlib.md5((SITE / rel).read_bytes()).hexdigest()


catalog = read_json(CATALOG_PATH)
pdp = read_json(PDP_PATH)
resin = next(c for c in catalog["categories"] if c["slug"] == "resin-charms")
existing_catalog = {p["sku"] for c in catalog["categories"] for p in c["products"]}
existing_pdp = {p["sku"] for p in pdp}

for product in PRODUCTS:
    sku, key, title = product["sku"], product["key"], product["title"]
    main_image = f"assets/images/pdp/{key}/01.webp"
    local_images = [f"assets/images/pdp/{key}/{i:02d}.webp" for i in range(1, 4)]
    for rel in local_images:
        assert (SITE / rel).exists(), f"missing verified image: {rel}"

    if sku not in existing_catalog:
        resin["products"].append({
            "category": "Resin Charms",
            "categorySlug": "resin-charms",
            "sourceSheet": "9.5产品上架.xlsx",
            "sourceRow": product["source_row"],
            "sortOrder": len(resin["products"]) + 1,
            "sku": sku,
            "title": title,
            "alibabaUrl": "",
            "cleanAlibabaUrl": "",
            "alibabaProductId": "",
            "image": main_image,
            "imageAlt": f"{sku} {title}",
            "imageWidth": 1000,
            "imageHeight": 1000,
            "imageHash": image_hash(main_image),
            "status": "ok",
            "anchorNote": "",
            "titleShort": title,
            "titleFull": title,
            "pdp": f"p-{key}.html",
        })
        existing_catalog.add(sku)

    if sku not in existing_pdp:
        specs = {"Material": "resin"}
        if product["size"]:
            specs["Size"] = product["size"]
        specs["Packaging"] = product["packing"]
        pdp.append({
            "catalogIndex": 0,
            "assetKey": key,
            "sku": sku,
            "category": "Resin Charms",
            "categorySlug": "resin-charms",
            "url": "",
            "status": "ok",
            "reason": "",
            "titleFull": title,
            "moq": "",
            "priceTiers": [],
            "specs": specs,
            "images": [],
            "imagesLocal": local_images,
            "fetchedAt": "2026-09-05T00:00:00Z",
            "pageTitle": "",
            "pageUrl": "",
        })
        existing_pdp.add(sku)

# Keep the fragile historical catalogIndex field aligned without relying on SKU
# uniqueness (the legacy catalog contains one intentional duplicate SKU).
flat = [p for c in catalog["categories"] for p in c["products"]]
catalog["totalProducts"] = len(flat)
catalog["totalImages"] = len(flat)
resin["productCount"] = len(resin["products"])
index_by_pdp = {p["pdp"]: i for i, p in enumerate(flat, 1)}
for entry in pdp:
    entry["catalogIndex"] = index_by_pdp[f"p-{entry['assetKey']}.html"]

write_json(CATALOG_PATH, catalog)
write_json(PDP_PATH, pdp)


def card(product):
    sku, key, title = product["sku"], product["key"], product["title"]
    e = html.escape
    inquiry = quote(f"{sku} {title[:46]}")
    wa = quote(
        f"Hello Qula Craft, I just viewed SKU {sku} and would like to discuss "
        "a custom quote. Can we chat?",
        safe="",
    )
    return (
        f'<article class="product-card" data-title="{e(title, quote=True)}" '
        f'data-type="Resin Charms" data-use="resin-charms"><div class="product-img">'
        f'<a href="p-{key}.html" style="display:block"><img loading="lazy" '
        f'src="assets/images/pdp/{key}/01.webp" alt="{e(sku)} {e(title, quote=True)}" '
        f'width="1000" height="1000"></a></div><div class="product-info">'
        f'<span class="pill soft">{e(sku)}</span><h3><a href="p-{key}.html" '
        f'style="color:inherit;text-decoration:none">{e(title)}</a></h3>'
        f'<a class="btn btn-card" href="quote.html?product={inquiry}">Send Inquiry <span>→</span></a>'
        f'<div class="card-cta-row"><a class="wa-line" href="https://wa.me/8618632026595?text={wa}" '
        f'target="_blank" rel="noopener">WhatsApp</a><a class="basket-add" '
        f'data-sku="{e(sku)}" data-title="{e(title, quote=True)}">＋ Inquiry list</a>'
        f'</div></div></article>'
    )


page = CATEGORY_PAGE.read_text(encoding="utf-8")
missing_cards = [p for p in PRODUCTS if f'data-sku="{p["sku"]}"' not in page]
if missing_cards:
    boundary = '</article></div></div></section><section class="section"><div class="container detail-grid">'
    assert page.count(boundary) == 1, "resin product-grid boundary changed"
    page = page.replace(boundary, '</article>' + "".join(card(p) for p in missing_cards) + boundary[len('</article>'):], 1)

# Rebuild only the Resin Charms ItemList from the verified catalog records.
items = []
for position, row in enumerate(resin["products"], 1):
    items.append({
        "@type": "ListItem",
        "position": position,
        "item": {
            "@type": "Product",
            "name": row.get("titleFull") or row["title"],
            "sku": row["sku"],
            "image": BASE + row["image"],
            "brand": {"@type": "Brand", "name": "Qula Craft"},
            "category": "Resin Charms",
            "url": BASE + row["pdp"],
        },
    })
item_list = {
    "@context": "https://schema.org",
    "@type": "ItemList",
    "name": "Resin Charms — live wholesale catalog",
    "numberOfItems": len(items),
    "itemListElement": items,
}

def replace_item_list(match):
    raw = match.group(1)
    try:
        obj = json.loads(raw)
    except json.JSONDecodeError:
        return match.group(0)
    if obj.get("@type") == "ItemList" and obj.get("name", "").startswith("Resin Charms"):
        return '<script type="application/ld+json">' + json.dumps(item_list, ensure_ascii=False) + "</script>"
    return match.group(0)

page = re.sub(r'<script type="application/ld\+json">(.*?)</script>', replace_item_list, page, flags=re.S)
CATEGORY_PAGE.write_text(page, encoding="utf-8")

print(f"Restored {len(PRODUCTS)} verified SKUs; catalog and PDP indexes now contain {len(flat)} products.")
