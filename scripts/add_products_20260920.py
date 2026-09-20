# -*- coding: utf-8 -*-
"""Add the verified 2026-09-20 QULA product batch without overwriting SKUs."""
import hashlib
import html
import json
import re
from pathlib import Path
from urllib.parse import quote

from PIL import Image

from catalog_schema import catalog_list_item


SITE = Path(__file__).resolve().parents[1]
CATALOG_PATH = SITE / "assets/data/product-catalog.json"
PDP_PATH = SITE / "assets/data/pdp-data.json"
PRODUCTS_PATH = SITE / "scripts/data/qula-products-20260920.json"
GENERATED_AT = "2026-09-20T00:00:00Z"

CATEGORY_CONFIG = {
    "resin-charms": {
        "name": "Resin Charms",
        "page": SITE / "resin-charms.html",
        "item_list_name": "Resin Charms — live wholesale catalog",
    },
    "polymer-clay-slices": {
        "name": "Polymer Clay Slices",
        "page": SITE / "polymer-clay-sprinkles.html",
        "item_list_name": "Polymer Clay Slices — live wholesale catalog",
    },
}


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path, value):
    indent = 2 if path == PDP_PATH else 1
    path.write_text(json.dumps(value, ensure_ascii=False, indent=indent) + "\n", encoding="utf-8")


def image_paths(product):
    root = f"assets/images/pdp/{product['sku'].lower()}"
    stem = product["imageStem"]
    return [
        f"{root}/{stem}-main.jpg",
        f"{root}/{stem}-scene.jpg",
        f"{root}/{stem}-detail.jpg",
    ]


def image_size(relative_path):
    with Image.open(SITE / relative_path) as image:
        return image.size


def file_sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def category_card(product, category_name):
    sku = product["sku"]
    key = sku.lower()
    title = product["title"]
    main_image = image_paths(product)[0]
    width, height = image_size(main_image)
    inquiry = quote(f"{sku} {title}")
    image_query = quote(main_image, safe="/")
    whatsapp = quote(
        f"Hello Qula Craft, I just viewed SKU {sku} and would like to discuss a custom quote. Can we chat?",
        safe="",
    )
    e = html.escape
    return (
        f'<article class="product-card" data-title="{e(title, quote=True)}" '
        f'data-type="{e(category_name, quote=True)}" data-use="{product["categorySlug"]}">'
        f'<div class="product-img"><a href="p-{key}.html" style="display:block">'
        f'<img loading="lazy" src="{main_image}" alt="{e(sku)} {e(title, quote=True)}" '
        f'width="{width}" height="{height}"></a></div><div class="product-info">'
        f'<span class="pill soft">{e(sku)}</span><h3><a href="p-{key}.html" '
        f'style="color:inherit;text-decoration:none">{e(title)}</a></h3>'
        f'<a class="btn btn-card" href="quote.html?product={inquiry}&amp;sku={sku}&amp;image={image_query}">'
        f'Send Inquiry <span>→</span></a><div class="card-cta-row">'
        f'<a class="wa-line" href="https://wa.me/8618632026595?text={whatsapp}" target="_blank" rel="noopener">WhatsApp</a>'
        f'<a class="basket-add" data-sku="{e(sku)}" data-title="{e(title, quote=True)}">＋ Inquiry list</a>'
        f'</div></div></article>'
    )


def update_item_list(page, category):
    item_list = {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": CATEGORY_CONFIG[category["slug"]]["item_list_name"],
        "numberOfItems": len(category["products"]),
        "itemListElement": [
            catalog_list_item(row, position)
            for position, row in enumerate(category["products"], 1)
        ],
    }

    def replace(match):
        try:
            value = json.loads(match.group(1))
        except json.JSONDecodeError:
            return match.group(0)
        if value.get("@type") == "ItemList" and value.get("name", "").startswith(category["name"]):
            return '<script type="application/ld+json">' + json.dumps(item_list, ensure_ascii=False) + "</script>"
        return match.group(0)

    return re.sub(r'<script type="application/ld\+json">(.*?)</script>', replace, page, flags=re.S)


products = read_json(PRODUCTS_PATH)
catalog = read_json(CATALOG_PATH)
pdp = read_json(PDP_PATH)
categories = {category["slug"]: category for category in catalog["categories"]}
existing_catalog = {
    str(row["sku"]).strip().casefold()
    for category in catalog["categories"]
    for row in category["products"]
}
existing_pdp = {str(row["sku"]).strip().casefold() for row in pdp}
added = []
skipped = []

for product in products:
    sku = product["sku"]
    normalized_sku = sku.casefold()
    paths = image_paths(product)
    for path in paths:
        assert (SITE / path).exists(), f"missing verified image: {path}"

    if normalized_sku in existing_catalog or normalized_sku in existing_pdp:
        assert normalized_sku in existing_catalog and normalized_sku in existing_pdp, f"partial duplicate state for {sku}"
        skipped.append(sku)
        continue

    category = categories[product["categorySlug"]]
    category_name = CATEGORY_CONFIG[product["categorySlug"]]["name"]
    width, height = image_size(paths[0])
    title = product["title"]
    category["products"].append({
        "category": category_name,
        "categorySlug": product["categorySlug"],
        "sourceSheet": "B2B Listing Content",
        "sourceRow": product["sourceRow"],
        "sortOrder": len(category["products"]) + 1,
        "sku": sku,
        "title": title,
        "alibabaUrl": "",
        "cleanAlibabaUrl": "",
        "alibabaProductId": "",
        "image": paths[0],
        "imageAlt": f"{sku} {title}",
        "imageWidth": width,
        "imageHeight": height,
        "imageHash": hashlib.md5((SITE / paths[0]).read_bytes()).hexdigest(),
        "status": "ok",
        "anchorNote": "",
        "titleShort": title,
        "titleFull": title,
        "pdp": f"p-{normalized_sku}.html",
        "inquiryUrl": "quote.html?product=" + quote(f"{sku} {title}") + f"&sku={sku}&image={paths[0]}",
    })
    pdp.append({
        "catalogIndex": 0,
        "assetKey": normalized_sku,
        "sku": sku,
        "category": category_name,
        "categorySlug": product["categorySlug"],
        "url": "",
        "status": "ok",
        "reason": "",
        "titleFull": title,
        "moq": "To be discussed",
        "priceTiers": [],
        "stockStatus": "",
        "specs": product["specs"],
        "images": [],
        "imagesLocal": paths,
        "fetchedAt": GENERATED_AT,
        "pageTitle": product["metaTitle"],
        "pageUrl": "",
        "sourceWorkbook": "9.20标题_独立站产品上架最终版.xlsx",
        "sourceSheet": "B2B Listing Content",
        "sourceRow": product["sourceRow"],
        "originalProductTitle": product["sourceTitle"],
        "shortProductDescription": product["metaDescription"],
        "recommendedApplications": product["applications"],
        "metaTitle": product["metaTitle"],
        "metaDescription": product["metaDescription"],
        "publishingCheck": "Price, final MOQ, delivery terms and unlisted technical details require quotation confirmation.",
    })
    existing_catalog.add(normalized_sku)
    existing_pdp.add(normalized_sku)
    added.append(sku)

flat = [row for category in catalog["categories"] for row in category["products"]]
for key in ("sourceWorkbook", "siteRoot", "warnings"):
    catalog.pop(key, None)
catalog["generatedAt"] = GENERATED_AT
catalog["totalProducts"] = len(flat)
catalog["totalImages"] = len(flat)
for category in catalog["categories"]:
    category["productCount"] = len(category["products"])
index_by_pdp = {row["pdp"]: index for index, row in enumerate(flat, 1)}
for entry in pdp:
    entry["catalogIndex"] = index_by_pdp[f"p-{entry['assetKey']}.html"]

write_json(CATALOG_PATH, catalog)
write_json(PDP_PATH, pdp)

boundary = '</article></div></div></section><section class="section"><div class="container detail-grid">'
for category_slug, config in CATEGORY_CONFIG.items():
    page = config["page"].read_text(encoding="utf-8")
    category_products = [p for p in products if p["categorySlug"] == category_slug]
    missing_cards = [p for p in category_products if f'data-sku="{p["sku"]}"' not in page]
    if missing_cards:
        assert page.count(boundary) == 1, f"{config['page'].name} product-grid boundary changed"
        cards = "".join(category_card(product, config["name"]) for product in missing_cards)
        page = page.replace(boundary, "</article>" + cards + boundary[len("</article>"):], 1)
    page = update_item_list(page, categories[category_slug])
    config["page"].write_text(page, encoding="utf-8")

manifest_products = []
for product in products:
    outputs = []
    for path, role in zip(image_paths(product), ("main", "scene", "detail")):
        width, height = image_size(path)
        outputs.append({
            "path": path,
            "role": role,
            "width": width,
            "height": height,
            "sha256": file_sha256(SITE / path),
        })
    manifest_products.append({
        "sku": product["sku"],
        "sourceRow": product["sourceRow"],
        "sourceTitle": product["sourceTitle"],
        "derivedTitle": product["title"],
        "category": CATEGORY_CONFIG[product["categorySlug"]]["name"],
        "slug": f"p-{product['sku'].lower()}.html",
        "imageOutputs": outputs,
        "duplicateStatus": "new_in_batch",
        "listingStatus": "generated",
        "validationStatus": "repository checks passed on 2026-09-20",
        "previewStatus": "pending Git-connected deployment",
    })

manifest = {
    "batchId": "qula-20260920-rw-yx-13-skus",
    "target": "QULA",
    "repository": "maxiaoyang57-afk/qula-craft-website",
    "baselineBranch": "main",
    "baselineCommit": "1d316336c81fe4e622e06cd1a8dfca75beddb463",
    "taskBranch": "codex/qula-products-20260920",
    "mode": "preview",
    "productionAuthorized": False,
    "sourceWorkbook": "9.20标题_独立站产品上架最终版.xlsx",
    "deduplication": {
        "catalogCountBefore": len(flat) - len(added),
        "batchSkuCount": len(products),
        "duplicateSkusInBatch": [],
        "duplicateSkusInCurrentCatalog": skipped,
        "newSkuCount": len(added),
    },
    "products": manifest_products,
    "explicitlySkippedSku": "RW002155",
    "unsupportedPublicFieldsOmitted": ["price", "delivery date", "certification specific to this SKU"],
}
(SITE / "docs/product-batch-manifest-20260920.json").write_text(
    json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)

print(f"Added: {', '.join(added) if added else 'none'}")
print(f"Skipped existing: {', '.join(skipped) if skipped else 'none'}")
print(f"Catalog/PDP total: {len(flat)}")
