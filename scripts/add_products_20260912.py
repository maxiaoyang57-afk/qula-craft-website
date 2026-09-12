# -*- coding: utf-8 -*-
"""Add the verified 2026-09-12 QULA product batch.

The migration is idempotent: it adds only SKUs that are absent from both the
catalog and PDP data, keeps source titles separate from derived listing copy,
and leaves unsupported commercial fields unpublished.
"""
import hashlib
import html
import json
import re
from pathlib import Path
from urllib.parse import quote

from PIL import Image


SITE = Path(__file__).resolve().parents[1]
CATALOG_PATH = SITE / "assets/data/product-catalog.json"
PDP_PATH = SITE / "assets/data/pdp-data.json"
BASE = "https://www.qulacrafts.com/"
GENERATED_AT = "2026-09-12T00:00:00Z"

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

PRODUCTS = [
    {
        "sku": "RW26692",
        "source_row": 2,
        "source_title": "Cute Bear Resin Embellishments with Heart and Flower Designs for Hair Clips Bows Scrapbooking Phone Case Decoration",
        "title": "Wholesale Cute Bear Resin Embellishments with Heart and Flower Designs for Hair Clips and DIY Crafts",
        "category_slug": "resin-charms",
        "specs": {
            "Material": "Resin",
            "Product type": "cute bear decorative embellishments",
            "Design": "three yellow bear designs with heart and flower details",
            "Color": "yellow with red, pink and white details",
            "Pack reference": "100 pieces per bag",
            "Custom packing": "custom pack quantities available on request",
        },
        "meta_title": "Cute Bear Resin Embellishments Wholesale | Qula Craft",
        "meta_description": "Wholesale yellow bear resin embellishments with heart and flower designs for hair accessories, phone cases and DIY craft projects.",
        "applications": "hair accessories, phone-case decoration, scrapbooking and DIY craft projects",
        "source_sha256": "18630e417e1da991929ca35866dc9eb44674af2f3342dc2860dbcd8018b64190",
    },
    {
        "sku": "YX004",
        "source_row": 3,
        "source_title": "Wholesale Mixed Candy Dessert Polymer Clay Cabochons for Hair Clips Phone Cases Nail Art and DIY Crafts",
        "title": "Wholesale Mixed Candy and Dessert Polymer Clay Slices for Slime, Nail Art and DIY Crafts",
        "category_slug": "polymer-clay-slices",
        "specs": {
            "Material": "Polymer clay",
            "Product type": "mixed miniature clay slices",
            "Design": "assorted candy, lollipop, ice cream and dessert motifs",
            "Color": "mixed bright and pastel colors",
            "Pack reference": "500 g per bag",
            "Custom packing": "custom pack quantities available on request",
        },
        "meta_title": "Mixed Candy Polymer Clay Slices Wholesale | Qula Craft",
        "meta_description": "Wholesale mixed candy and dessert polymer clay slices for slime, nail art, phone cases, hair accessories and DIY craft assortments.",
        "applications": "slime, nail art, phone cases, hair accessories and DIY craft kits",
        "source_sha256": "a69218fe235ae57d8a0ab2302198f5da9522784a2601ee7eab75df890aeafadc",
    },
    {
        "sku": "YX002",
        "source_row": 4,
        "source_title": "Wholesale Purple Berry Polymer Clay Cabochons for Hair Clips Phone Cases Scrapbooking and DIY Crafts",
        "title": "Wholesale Mixed Fruit Polymer Clay Slices with Berry, Citrus and Watermelon Designs for Slime and DIY Crafts",
        "category_slug": "polymer-clay-slices",
        "specs": {
            "Material": "Polymer clay",
            "Product type": "mixed fruit-themed clay slices",
            "Design": "assorted berry, citrus, watermelon, kiwi, flower and swirl motifs",
            "Color": "mixed pink, yellow, green, red and purple",
            "Pack reference": "500 g per bag",
            "Custom packing": "custom pack quantities available on request",
        },
        "meta_title": "Mixed Fruit Polymer Clay Slices Wholesale | Qula Craft",
        "meta_description": "Wholesale mixed fruit polymer clay slices with berry, citrus, watermelon and kiwi designs for slime, scrapbooking and DIY crafts.",
        "applications": "slime, scrapbooking, phone-case decoration and DIY craft mixes",
        "source_sha256": "bf7071ee25d7d98d6886667010def3ed9629ebf956e2a52e83e8eba8a7076f8e",
        "content_note": "The source title says purple berry; the supplied image shows a mixed fruit assortment, so the derived listing title follows the image.",
    },
    {
        "sku": "YX051",
        "source_row": 5,
        "source_title": "5mm Banana Slice Fruit Polymer Clay Sprinkles for Plastic Clay Mud Particles Card Making Tiny Cute DIY Sprinkles",
        "title": "Wholesale 5 mm Banana Polymer Clay Slices for Slime, Nail Art and DIY Craft Decoration",
        "category_slug": "polymer-clay-slices",
        "specs": {
            "Material": "Polymer clay",
            "Product type": "banana fruit slices",
            "Design": "round banana cross-section pattern",
            "Color": "pale yellow with brown detail",
            "Size": "5 mm",
            "Pack reference": "500 g per bag",
            "Custom packing": "custom pack quantities available on request",
        },
        "meta_title": "5 mm Banana Polymer Clay Slices Wholesale | Qula Craft",
        "meta_description": "Wholesale 5 mm banana polymer clay slices for slime, nail art, card making and DIY craft decoration. Custom pack quantities available.",
        "applications": "slime, nail art, card making, shaker crafts and DIY decoration",
        "source_sha256": "799aab06aebe5665a8e6d87f551abaf650065d829c93a275364a0c851d81e416",
    },
    {
        "sku": "RW927",
        "source_row": 6,
        "source_title": "24mm Kawaii Flat Back Resin Sunflower Charms for DIY Decoration Bag Earring Key Chain Patch Jewelry Making DIY",
        "title": "Wholesale 24 mm Sunflower Resin Cabochons for Hair Accessories, Jewelry and DIY Decoration",
        "category_slug": "resin-charms",
        "specs": {
            "Material": "Resin",
            "Product type": "sunflower cabochons",
            "Design": "sunflower with layered orange petals and a dark brown center",
            "Color": "orange and dark brown",
            "Size": "24 mm",
            "Pack reference": "100 pieces per bag",
            "Custom packing": "custom pack quantities available on request",
        },
        "meta_title": "24 mm Sunflower Resin Cabochons Wholesale | Qula Craft",
        "meta_description": "Wholesale 24 mm sunflower resin cabochons for hair accessories, jewelry, keychains, bags and DIY decoration projects.",
        "applications": "hair accessories, jewelry, keychains, bags and DIY decoration",
        "source_sha256": "794c46bb3ee1f208fad114468a68c5cbb7374693cd31154e632b857b330a183c",
    },
    {
        "sku": "YX4138",
        "source_row": 7,
        "source_title": "Wholesale Strawberry Polymer Clay Sprinkles Custom Mini Fruit Pieces for Slime Phone Hair Scrapbook Decoration",
        "title": "Wholesale Strawberry Polymer Clay Sprinkle Mix for Slime, Shakers and DIY Craft Decoration",
        "category_slug": "polymer-clay-slices",
        "specs": {
            "Material": "Polymer clay",
            "Product type": "strawberry-themed sprinkle mix",
            "Design": "mini white strawberry slices with pink and clear decorative pieces",
            "Color": "pink, clear and white with red and green details",
            "Pack reference": "500 g per bag",
            "Custom packing": "custom pack quantities available on request",
        },
        "meta_title": "Strawberry Polymer Clay Sprinkle Mix Wholesale | Qula Craft",
        "meta_description": "Wholesale strawberry polymer clay sprinkle mix for slime, shakers, phone cases, hair accessories and scrapbook decoration.",
        "applications": "slime, shakers, phone cases, hair accessories and scrapbook decoration",
        "source_sha256": "55a75db5c7b9892cfa6d468dbf3454cdd41efa7664ac3c3f891c1628ca93a1c0",
    },
    {
        "sku": "RW2445",
        "source_row": 8,
        "source_title": "Wholesale Chocolate Bar Cabochons Custom 3D Mini Dessert Decorations for Hair Accessories Phone Keychain Projects",
        "title": "Wholesale Chocolate Bar Resin Cabochons in Pink, Brown and Cream for Hair Accessories and DIY Crafts",
        "category_slug": "resin-charms",
        "specs": {
            "Material": "Resin",
            "Product type": "mini chocolate bar cabochons",
            "Design": "segmented chocolate bar shape",
            "Color": "pink, dark brown and cream",
            "Pack reference": "100 pieces per bag",
            "Custom packing": "custom pack quantities available on request",
        },
        "meta_title": "Chocolate Bar Resin Cabochons Wholesale | Qula Craft",
        "meta_description": "Wholesale chocolate bar resin cabochons in pink, brown and cream for hair accessories, phone cases, keychains and DIY crafts.",
        "applications": "hair accessories, phone cases, keychains, decoden and DIY crafts",
        "source_sha256": "b1db5417715eea83bcbf82e8be300122f54ba9028ceb965fbb8e8bb2d2c2b693",
    },
    {
        "sku": "RW370",
        "source_row": 9,
        "source_title": "100pcs Resin Creamy Candy Cabochons Flatback for Scrapbook Home Decoration Mini 3D Sweet Food Resin Ornament DIY Slime Charm",
        "title": "Wholesale Pastel Whipped Cream Resin Cabochons for Slime, Scrapbooking and DIY Decoration",
        "category_slug": "resin-charms",
        "specs": {
            "Material": "Resin",
            "Product type": "whipped cream flatback cabochons",
            "Design": "swirled cream shape",
            "Color": "assorted pastel colors, cream and brown",
            "Pack reference": "100 pieces per bag",
            "Custom packing": "custom pack quantities available on request",
        },
        "meta_title": "Pastel Whipped Cream Resin Cabochons Wholesale | Qula Craft",
        "meta_description": "Wholesale pastel whipped cream resin cabochons for slime, scrapbooking, phone-case decoden and miniature dessert craft projects.",
        "applications": "slime, scrapbooking, phone-case decoden and miniature dessert crafts",
        "source_sha256": "c527ceca5d65e0b1d87b7165b69e54a07f21a2e8a434820c8ba02ebdc992edff",
    },
    {
        "sku": "RW22405",
        "source_row": 10,
        "source_title": "100Pcs Cartoon Animal Plate Flatback Resin Fox Banana Duck Bread Egg Charms for Jewelry Making Accessories Earring Keychain Deco",
        "title": "Wholesale Cartoon Animal and Food Resin Cabochon Mix for Jewelry, Keychains and DIY Accessories",
        "category_slug": "resin-charms",
        "specs": {
            "Material": "Resin",
            "Product type": "mixed cartoon cabochons",
            "Design": "fox, panda, banana, chick, bread and egg plate motifs",
            "Color": "mixed yellow, orange and white with multicolor details",
            "Pack reference": "100 pieces per bag",
            "Custom packing": "custom pack quantities available on request",
        },
        "meta_title": "Cartoon Animal and Food Resin Cabochon Mix Wholesale",
        "meta_description": "Wholesale cartoon animal and food resin cabochons with fox, panda, banana, chick, bread and egg designs for jewelry and DIY crafts.",
        "applications": "jewelry, earrings, keychains, phone-case decoration and DIY accessories",
        "source_sha256": "255042b4c1d08bde2b4e7f7280eb43de9203e616620162ded9230066d573afb3",
    },
    {
        "sku": "RW1394",
        "source_row": 11,
        "source_title": "100Pcs Mini Mushroom House Figurines Micro Fairy Garden Miniature Forest Terrarium Decor Resin Craft DIY Accessories",
        "title": "Wholesale Mini Mushroom House Resin Figurines for Fairy Gardens, Terrariums and DIY Crafts",
        "category_slug": "resin-charms",
        "specs": {
            "Material": "Resin",
            "Product type": "mini mushroom house figurines",
            "Design": "assorted rounded mushroom houses with doors, windows and dotted roofs",
            "Color": "red, pink, yellow and green roofs with cream bases",
            "Pack reference": "100 pieces per bag",
            "Custom packing": "custom pack quantities available on request",
        },
        "meta_title": "Mini Mushroom House Resin Figurines Wholesale | Qula Craft",
        "meta_description": "Wholesale mini mushroom house resin figurines for fairy gardens, terrariums, miniature displays and DIY craft accessories.",
        "applications": "fairy gardens, terrariums, miniature displays and DIY craft accessories",
        "source_sha256": "2026b1b2a08adaf136d1d5fdc31143ed2a736fd136a6ddef3276d50421916b0f",
    },
    {
        "sku": "RW001078",
        "source_row": 12,
        "source_title": "Cute Blue Flat Back Dolphin Resin Scrapbooking DIY Series Handmade Craft Decoration",
        "title": "Wholesale 28 x 20 mm Blue Dolphin Resin Cabochons for Scrapbooking and DIY Decoration",
        "category_slug": "resin-charms",
        "specs": {
            "Material": "Resin",
            "Product type": "blue dolphin cabochons",
            "Design": "curved dolphin with pink flower detail",
            "Color": "light blue with pink, white and black details",
            "Size": "28 x 20 mm",
            "Pack reference": "100 pieces per bag",
            "Custom packing": "custom pack quantities available on request",
        },
        "meta_title": "28 x 20 mm Blue Dolphin Resin Cabochons Wholesale",
        "meta_description": "Wholesale 28 x 20 mm blue dolphin resin cabochons with pink flower detail for scrapbooking, phone cases and DIY decoration.",
        "applications": "scrapbooking, phone cases, hair accessories and DIY decoration",
        "source_sha256": "4adb078aa4dfdceb0f8cdc4104d33b0c6dbb12abf9080eb470a372a431974bb3",
    },
    {
        "sku": "RW26637",
        "source_row": 13,
        "source_title": "4Pcs Cute Mini Scuba Diver Figurines Cartoon Chibi Diving Dolls with Snorkel Mask Flippers for Kids Toy Cake Topper Party Favor",
        "title": "Wholesale Mini Scuba Diver Resin Figurines in Assorted Colors for Cake Toppers and DIY Decoration",
        "category_slug": "resin-charms",
        "specs": {
            "Material": "Resin",
            "Product type": "mini scuba diver figurines",
            "Design": "cartoon divers with snorkel masks and flippers",
            "Color": "assorted black, blue, white, pink, yellow and mint",
            "Pack reference": "4 pieces per bag",
            "Custom packing": "custom pack quantities available on request",
        },
        "meta_title": "Mini Scuba Diver Resin Figurines Wholesale | Qula Craft",
        "meta_description": "Wholesale mini scuba diver resin figurines in assorted colors for cake toppers, party favors, miniature displays and DIY decoration.",
        "applications": "cake toppers, party favors, miniature displays and DIY decoration",
        "source_sha256": "1a3b29e4c589d18743074ee70c86a21da8198e86c0f10cc8f004782fb6766690",
    },
]


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path, value):
    indent = 2 if path == PDP_PATH else 1
    path.write_text(json.dumps(value, ensure_ascii=False, indent=indent) + "\n", encoding="utf-8")


def file_sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def image_size(rel):
    with Image.open(SITE / rel) as image:
        return image.size


def category_card(product, category_name):
    sku = product["sku"]
    key = sku.lower()
    title = product["title"]
    main_image = f"assets/images/pdp/{key}/01.webp"
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
        f'data-type="{e(category_name, quote=True)}" data-use="{product["category_slug"]}">'
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
    items = []
    for position, row in enumerate(category["products"], 1):
        items.append({
            "@type": "ListItem",
            "position": position,
            "item": {
                "@type": "Product",
                "name": row.get("titleFull") or row["title"],
                "sku": row["sku"],
                "image": BASE + row["image"],
                "brand": {"@type": "Brand", "name": "Qula Craft"},
                "category": category["name"],
                "url": BASE + row["pdp"],
            },
        })
    item_list = {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": CATEGORY_CONFIG[category["slug"]]["item_list_name"],
        "numberOfItems": len(items),
        "itemListElement": items,
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


catalog = read_json(CATALOG_PATH)
pdp = read_json(PDP_PATH)
categories = {category["slug"]: category for category in catalog["categories"]}
existing_catalog = {str(row["sku"]).strip().casefold() for category in catalog["categories"] for row in category["products"]}
existing_pdp = {str(row["sku"]).strip().casefold() for row in pdp}
added = []
skipped = []

for product in PRODUCTS:
    sku = product["sku"]
    key = sku.lower()
    normalized_sku = sku.casefold()
    category = categories[product["category_slug"]]
    local_images = [f"assets/images/pdp/{key}/{index:02d}.webp" for index in range(1, 4)]
    for rel in local_images:
        assert (SITE / rel).exists(), f"missing verified image: {rel}"

    if normalized_sku in existing_catalog or normalized_sku in existing_pdp:
        assert normalized_sku in existing_catalog and normalized_sku in existing_pdp, f"partial duplicate state for {sku}"
        skipped.append(sku)
        continue

    width, height = image_size(local_images[0])
    title = product["title"]
    category_name = CATEGORY_CONFIG[product["category_slug"]]["name"]
    category["products"].append({
        "category": category_name,
        "categorySlug": product["category_slug"],
        "sourceSheet": "Sheet1",
        "sourceRow": product["source_row"],
        "sortOrder": len(category["products"]) + 1,
        "sku": sku,
        "title": title,
        "alibabaUrl": "",
        "cleanAlibabaUrl": "",
        "alibabaProductId": "",
        "image": local_images[0],
        "imageAlt": f"{sku} {title}",
        "imageWidth": width,
        "imageHeight": height,
        "imageHash": hashlib.md5((SITE / local_images[0]).read_bytes()).hexdigest(),
        "status": "ok",
        "anchorNote": "",
        "titleShort": title,
        "titleFull": title,
        "pdp": f"p-{key}.html",
        "inquiryUrl": (
            "quote.html?product=" + quote(f"{sku} {title}") +
            f"&sku={sku}&image={local_images[0]}"
        ),
    })
    pdp.append({
        "catalogIndex": 0,
        "assetKey": key,
        "sku": sku,
        "category": category_name,
        "categorySlug": product["category_slug"],
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
        "fetchedAt": GENERATED_AT,
        "pageTitle": product["meta_title"],
        "pageUrl": "",
        "sourceWorkbook": "9.12上品(1).xlsx",
        "sourceSheet": "Sheet1",
        "sourceRow": product["source_row"],
        "originalProductTitle": product["source_title"],
        "shortProductDescription": product["meta_description"],
        "recommendedApplications": product["applications"],
        "metaTitle": product["meta_title"],
        "metaDescription": product["meta_description"],
        "publishingCheck": "Price, MOQ, lead time and unlisted technical details require quotation confirmation.",
        **({"contentNormalizationNote": product["content_note"]} if product.get("content_note") else {}),
    })
    existing_catalog.add(normalized_sku)
    existing_pdp.add(normalized_sku)
    added.append(sku)

flat = [row for category in catalog["categories"] for row in category["products"]]
for internal_key in ("sourceWorkbook", "siteRoot", "warnings"):
    catalog.pop(internal_key, None)
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
    page_path = config["page"]
    page = page_path.read_text(encoding="utf-8")
    category_products = [p for p in PRODUCTS if p["category_slug"] == category_slug]
    missing_cards = [p for p in category_products if f'data-sku="{p["sku"]}"' not in page]
    if missing_cards:
        assert page.count(boundary) == 1, f"{page_path.name} product-grid boundary changed"
        cards = "".join(category_card(product, config["name"]) for product in missing_cards)
        page = page.replace(boundary, "</article>" + cards + boundary[len("</article>"):], 1)
    page = update_item_list(page, categories[category_slug])
    page_path.write_text(page, encoding="utf-8")

manifest_products = []
for product in PRODUCTS:
    sku = product["sku"]
    key = sku.lower()
    outputs = []
    for index, role in enumerate(("main", "detail", "detail"), 1):
        rel = f"assets/images/pdp/{key}/{index:02d}.webp"
        width, height = image_size(rel)
        outputs.append({
            "path": rel,
            "role": role,
            "width": width,
            "height": height,
            "sha256": file_sha256(SITE / rel),
        })
    manifest_products.append({
        "sku": sku,
        "sourceRow": product["source_row"],
        "sourceTitle": product["source_title"],
        "derivedTitle": product["title"],
        "category": CATEGORY_CONFIG[product["category_slug"]]["name"],
        "slug": f"p-{key}.html",
        "sourceImage": {
            "name": "RW26692 .jpg" if sku == "RW26692" else f"{sku}.jpg",
            "sha256": product["source_sha256"],
        },
        "imageOutputs": outputs,
        "duplicateStatus": "new" if sku in added else "existing_skipped",
        "listingStatus": "generated" if sku in added else "skipped",
        "validationStatus": "pending full repository checks",
        "previewStatus": "pending Git-connected deployment",
        **({"contentNote": product["content_note"]} if product.get("content_note") else {}),
    })

manifest = {
    "batchId": "qula-20260912-rw-yx-12-skus",
    "target": "QULA",
    "repository": "maxiaoyang57-afk/qula-craft-website",
    "baselineBranch": "main",
    "baselineCommit": "b0dd566b65d1546e20a02926d213b0b1ad8124e5",
    "taskBranch": "pro/qula-new-products-20260912",
    "mode": "preview",
    "productionAuthorized": False,
    "sourceWorkbook": {
        "name": "9.12上品(1).xlsx",
        "sheet": "Sheet1",
        "sha256": "360712d526778b96b3e2a4ae5bf4cf346d0c47eea4b499052a1396c9173746f2",
    },
    "deduplication": {
        "catalogCountBefore": len(flat) - len(added),
        "batchSkuCount": len(PRODUCTS),
        "duplicateSkusInBatch": [],
        "duplicateSkusInCurrentCatalog": skipped,
        "newSkuCount": len(added),
        "exactDuplicateSourceImagesInBatch": [],
    },
    "products": manifest_products,
    "unsupportedPublicFieldsOmitted": ["price", "MOQ", "lead time", "weight", "certification specific to this SKU"],
}
(SITE / "docs/product-batch-manifest-20260912.json").write_text(
    json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)

print(f"Added: {', '.join(added) if added else 'none'}")
print(f"Skipped existing: {', '.join(skipped) if skipped else 'none'}")
print(f"Catalog/PDP total: {len(flat)}")
