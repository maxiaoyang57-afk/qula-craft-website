# -*- coding: utf-8 -*-
"""Add the verified 2026-09-11 QULA product batch.

The migration is idempotent. It adds only SKUs absent from the current catalog,
keeps unsupported commercial fields blank, and updates the Resin Charms page.
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
        "sku": "RW26746",
        "key": "rw26746",
        "title": "Wholesale Christmas Gingerbread Box Miniatures Custom 3D Dessert Set Decorations for Tabletop Holiday Scene Accessories",
        "source_row": 1,
        "specs": {
            "Product type": "decorative Christmas box miniature set",
            "Motif": "gingerbread, snowman, Santa, Christmas tree, wreath and snowflake designs",
            "Color": "red, cream, green and brown with multicolor holiday graphics",
            "Finish": "glossy printed box surfaces with molded miniature dessert pieces",
            "Supply format": "assorted Christmas box and dessert miniature set",
            "Customization": "available; final options are confirmed with the quotation and approved sample",
        },
        "meta_title": "Christmas Gingerbread Box Miniatures Wholesale | Qula Craft",
        "meta_description": "Wholesale Christmas gingerbread box miniatures and 3D dessert decorations for tabletop holiday scenes. Custom options available by quotation.",
        "applications": "tabletop holiday scenes, miniature displays, Christmas gift sets and seasonal craft projects",
    },
    {
        "sku": "RW26768",
        "key": "rw26768",
        "title": "Wholesale Christmas Gingerbread Cabochons Custom 3D Holiday Mini Charms for Hair Phone Keychain Accessories",
        "source_row": 2,
        "specs": {
            "Product type": "3D flatback Christmas cabochon assortment",
            "Motif": "gingerbread person, snowman, wreath, Santa, Christmas tree, stocking, snowflake and hat designs",
            "Color": "gingerbread brown with red, green, white and yellow details",
            "Finish": "glossy molded surface",
            "Back style": "flat back",
            "Supply format": "assorted Christmas shapes",
            "Customization": "available; final options are confirmed with the quotation and approved sample",
        },
        "meta_title": "Christmas Gingerbread Cabochons Wholesale | Qula Craft",
        "meta_description": "Wholesale Christmas gingerbread cabochons and 3D holiday mini charms for hair, phone and keychain accessories. Custom options by quotation.",
        "applications": "hair accessories, phone-case decoration, keychain accessories and seasonal DIY crafts",
    },
]


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path, value):
    indent = 2 if path == PDP_PATH else 1
    path.write_text(json.dumps(value, ensure_ascii=False, indent=indent) + "\n", encoding="utf-8")


def image_hash(rel):
    return hashlib.md5((SITE / rel).read_bytes()).hexdigest()


catalog = read_json(CATALOG_PATH)
pdp = read_json(PDP_PATH)
resin = next(category for category in catalog["categories"] if category["slug"] == "resin-charms")
existing_catalog = {row["sku"] for category in catalog["categories"] for row in category["products"]}
existing_pdp = {row["sku"] for row in pdp}
added = []
skipped = []

for product in PRODUCTS:
    sku, key, title = product["sku"], product["key"], product["title"]
    local_images = [f"assets/images/pdp/{key}/{index:02d}.webp" for index in range(1, 4)]
    for rel in local_images:
        assert (SITE / rel).exists(), f"missing verified image: {rel}"

    if sku in existing_catalog or sku in existing_pdp:
        assert sku in existing_catalog and sku in existing_pdp, f"partial duplicate state for {sku}"
        skipped.append(sku)
        continue

    main_image = local_images[0]
    resin["products"].append({
        "category": "Resin Charms",
        "categorySlug": "resin-charms",
        "sourceSheet": "Sheet1",
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
        "inquiryUrl": (
            "quote.html?product=" + quote(f"{sku} {title}") +
            f"&sku={sku}&image={main_image}"
        ),
    })
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
        "stockStatus": "",
        "specs": product["specs"],
        "images": [],
        "imagesLocal": local_images,
        "fetchedAt": "2026-09-11T00:00:00Z",
        "pageTitle": product["meta_title"],
        "pageUrl": "",
        "sourceWorkbook": "9.11.xls",
        "sourceSheet": "Sheet1",
        "sourceRow": product["source_row"],
        "originalProductTitle": title,
        "shortProductDescription": product["meta_description"],
        "recommendedApplications": product["applications"],
        "metaTitle": product["meta_title"],
        "metaDescription": product["meta_description"],
        "publishingCheck": "Exact material, dimensions, pack quantity, MOQ, lead time and detailed custom options require quotation confirmation.",
    })
    existing_catalog.add(sku)
    existing_pdp.add(sku)
    added.append(sku)

flat = [row for category in catalog["categories"] for row in category["products"]]
# These legacy importer fields expose obsolete local workstation paths and are
# not used by the public catalog. Remove them before publishing the JSON asset.
for internal_key in ("sourceWorkbook", "siteRoot", "warnings"):
    catalog.pop(internal_key, None)
catalog["generatedAt"] = "2026-09-11T00:00:00Z"
catalog["totalProducts"] = len(flat)
catalog["totalImages"] = len(flat)
resin["productCount"] = len(resin["products"])
index_by_pdp = {row["pdp"]: index for index, row in enumerate(flat, 1)}
for entry in pdp:
    entry["catalogIndex"] = index_by_pdp[f"p-{entry['assetKey']}.html"]

write_json(CATALOG_PATH, catalog)
write_json(PDP_PATH, pdp)


def card(product):
    sku, key, title = product["sku"], product["key"], product["title"]
    e = html.escape
    main_image = f"assets/images/pdp/{key}/01.webp"
    inquiry = quote(f"{sku} {title}")
    image_query = quote(main_image, safe="/")
    wa = quote(
        f"Hello Qula Craft, I just viewed SKU {sku} and would like to discuss a custom quote. Can we chat?",
        safe="",
    )
    return (
        f'<article class="product-card" data-title="{e(title, quote=True)}" '
        f'data-type="Resin Charms" data-use="resin-charms"><div class="product-img">'
        f'<a href="p-{key}.html" style="display:block"><img loading="lazy" '
        f'src="{main_image}" alt="{e(sku)} {e(title, quote=True)}" width="1000" height="1000"></a>'
        f'</div><div class="product-info"><span class="pill soft">{e(sku)}</span>'
        f'<h3><a href="p-{key}.html" style="color:inherit;text-decoration:none">{e(title)}</a></h3>'
        f'<a class="btn btn-card" href="quote.html?product={inquiry}&amp;sku={sku}&amp;image={image_query}">'
        f'Send Inquiry <span>→</span></a><div class="card-cta-row">'
        f'<a class="wa-line" href="https://wa.me/8618632026595?text={wa}" target="_blank" rel="noopener">WhatsApp</a>'
        f'<a class="basket-add" data-sku="{e(sku)}" data-title="{e(title, quote=True)}">＋ Inquiry list</a>'
        f'</div></div></article>'
    )


page = CATEGORY_PAGE.read_text(encoding="utf-8")
missing_cards = [product for product in PRODUCTS if f'data-sku="{product["sku"]}"' not in page]
if missing_cards:
    boundary = '</article></div></div></section><section class="section"><div class="container detail-grid">'
    assert page.count(boundary) == 1, "resin product-grid boundary changed"
    page = page.replace(
        boundary,
        '</article>' + "".join(card(product) for product in missing_cards) + boundary[len('</article>'):],
        1,
    )

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
    try:
        value = json.loads(match.group(1))
    except json.JSONDecodeError:
        return match.group(0)
    if value.get("@type") == "ItemList" and value.get("name", "").startswith("Resin Charms"):
        return '<script type="application/ld+json">' + json.dumps(item_list, ensure_ascii=False) + "</script>"
    return match.group(0)


page = re.sub(r'<script type="application/ld\+json">(.*?)</script>', replace_item_list, page, flags=re.S)
CATEGORY_PAGE.write_text(page, encoding="utf-8")

print(f"Added: {', '.join(added) if added else 'none'}")
print(f"Skipped existing: {', '.join(skipped) if skipped else 'none'}")
print(f"Catalog/PDP total: {len(flat)}")
