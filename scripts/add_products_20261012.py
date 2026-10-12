"""Import the user-confirmed QULA batch without inferring missing specifications.

Run from latest main with a plan JSON, the original workbook, and prepared
three-image asset paths. CDK080 is updated in place; its original record is
retained in the batch manifest. The workbook itself is never modified.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import html
import json
import re
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

import openpyxl
from PIL import Image
from catalog_schema import catalog_list_item

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://www.qulacrafts.com/"
DATE = "2026-10-12"
CARD = re.compile(r'<article class="product-card"[^>]*>.*?</article>', re.S)
MATERIALS = {"resin": "Resin", "acrylic": "Acrylic", "plastic": "Plastic", "alloy": "Alloy", "resin and alloy": "Resin and alloy"}


def save_json(path, value, indent=2):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=indent) + "\n", encoding="utf-8")


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def size_text(value):
    value = str(value).strip()
    if value.lower() in {"none", ""}:
        return None
    value = value.replace("长度", "Length: ").replace("MM", "mm")
    value = re.sub(r"\s*\*\s*", " × ", value)
    return re.sub(r"\s*mm\b", " mm", value)


def specs_from_source(raw):
    specs = {}
    material = re.sub(r"\s+", " ", raw["材质"].strip()).lower()
    if material not in {"none", ""}:
        assert material in MATERIALS, material
        specs["Material"] = MATERIALS[material]
    size = size_text(raw["尺寸"])
    if size:
        specs["Size"] = size
    else:
        specs["Dimensions"] = "Confirm dimensions by inquiry"
    hole = raw["孔径"].strip()
    specs["Hole"] = {"无": "No hole", "有": "Present; diameter confirmed by inquiry", "咨询客服": "Confirm hole diameter by inquiry"}[hole]
    if raw["颜色"].strip() == "混款":
        specs["Assortment"] = "Mixed assortment; confirm the exact selection by inquiry"
    # A bag count is a packaging reference, never an inferred MOQ.
    pack = raw["包装规格"]
    if "100pcs/bag" in pack:
        specs["Standard pack"] = "100 pieces per bag; custom packing by inquiry"
    elif "50pair/bag" in pack:
        specs["Standard pack"] = "50 pairs per bag; custom packing by inquiry"
    else:
        assert pack == "可以定制，咨询客服", pack
        specs["Packing"] = "Custom packing available; confirm the pack specification by inquiry"
    specs["Customization"] = "Available; details confirmed by inquiry"
    return specs


def card(row):
    e = html.escape
    sku, title = row["sku"], row["title"]
    wa = quote(f"Hello Qula Craft, I just viewed SKU {sku} and would like to discuss a custom quote. Can we chat?", safe="")
    return (f'<article class="product-card" data-title="{e(title)}" data-type="{e(row["category"])}" data-use="{row["categorySlug"]}">'
            f'<div class="product-img"><a href="{row["pdp"]}" style="display:block"><img loading="lazy" src="{row["image"]}" alt="{e(row["imageAlt"])}" width="{row["imageWidth"]}" height="{row["imageHeight"]}"></a></div>'
            f'<div class="product-info"><span class="pill soft">{sku}</span><h3><a href="{row["pdp"]}" style="color:inherit;text-decoration:none">{e(title)}</a></h3>'
            f'<a class="btn btn-card" href="{e(row["inquiryUrl"], quote=True)}">Send Inquiry <span>→</span></a>'
            f'<div class="card-cta-row"><a class="wa-line" href="https://wa.me/8618632026595?text={wa}" target="_blank" rel="noopener">WhatsApp</a>'
            f'<a class="basket-add" data-sku="{sku}" data-title="{e(title)}" data-image="{row["image"]}">＋ Inquiry list</a></div></div></article>')


def update_category_copy(path):
    page = path.read_text()
    if path.name == "keychain.html":
        meta_title = "Keychains Wholesale: Christmas Charms & Wire Rings | Qula Craft"
        meta_description = "Wholesale Christmas charm keychains, novelty bag pendants and wire key rings. Browse styles and SKU-specific pack sizes, then request a B2B quote."
        hero = "Browse finished Christmas charm keychains, novelty bag pendants and colorful wire key rings. Check each SKU for its material, listed size and packing, then request a wholesale quote."
        replacements = {
            "Novelty Food Keychains": "Wholesale Keychains and Bag Charms",
            "Finished goods, not parts: resin food keychains — ice cream cones, cookies, peaches, bubble-tea cups, candy corn and seashells — assembled with hardware and packed in small lots. Hang them on a display and they sell themselves.": hero,
            "Finished resin food keychains — ice-cream cones, cookies, bubble-tea cups — assembled with hardware, not DIY parts. Stock designs sell in small counted lots, so gift shops can hang a display without committing to bulk. Custom themes are quoted from your reference photo.": "Choose from Christmas charm keychains, novelty food styles and screw-lock wire key rings. Product format and packing vary by SKU. Select a design and reference its code when asking about quantities, custom packing and a wholesale quote.",
            "Fully assembled keychains with metal hardware": "Finished charm keychains and wire key rings; refer to the selected SKU",
            "1pc samples and 10pcs lots, theme-sorted": "SKU-specific packs; selected styles have 100 pieces per bag",
            "Ice cream, cookies, fruit, drinks, summer beach, candy": "Christmas, ice cream, cookies, fruit, drinks, beach and candy designs",
            "OPP bags per piece; retail cards and private label available": "Pack quantities listed per SKU; custom packing confirmed by inquiry",
            "Finished — resin charm, jump ring and key ring assembled. Out of the bag and onto a display hook; no assembly labor on your side.": "The catalog includes finished charm keychains and screw-lock wire key rings. Check the selected SKU and its product image to confirm the format and included components.",
            "Most stock designs come in 10pcs lots with 1pc samples available, so a display of 10 designs costs one small test order before you commit deeper.": "Pack sizes vary by SKU. The listed Christmas charm keychains and CDK080 have a 100-piece bag reference. Confirm your assortment, sample packing and minimum order quantity by inquiry.",
        }
    elif path.name == "jewelry-accessories.html":
        meta_title = "Jewelry Findings & Accessories Wholesale | Qula Craft"
        meta_description = "Browse jewelry findings, acrylic pendants, phone tether tabs and finished earrings. Check SKU-specific sizes and packing, then request a wholesale quote."
        replacements = {
            "The hardware that turns charms into products: lobster clasps, spring buckles, chain connectors, extension chains, carabiners and key rings — most in pastel and candy colors that match our charm lines, packed in 100pcs lots.": "Browse jewelry findings, acrylic pendants, phone tether tabs, snowflake cabochons and finished earrings. Choose a SKU, confirm its size and packing, then request a wholesale quote.",
            "The hardware that turns charms into sellable products: lobster clasps, spring buckles, extension chains, carabiners and key rings. We stock 21 listings in 100pcs lots, most in pastel and candy tones matched to our charm lines — one order covers the charm and the hardware that carries it.": "Browse components and finished accessories for jewelry and craft projects: findings, pendants, clear phone tether tabs, snowflake cabochons and pink hat earrings. Materials and packing vary by SKU, so reference the product code to confirm fit, quantity and customization.",
            "Lobster clasps, spring buckles, connectors, extension chains, carabiners, silicone bands": "Jewelry findings, pendants, earrings, phone tether tabs and decorative cabochons",
            "Pastel and candy coated metal, gold and rainbow finishes": "Colors and assortments vary by SKU; confirm with your quote",
            "100pcs lots, single color or assorted": "SKU-specific packing; YV353 earrings have 50 pairs per bag",
            "Bulk bags; compartment-boxed assortments available": "Pack specifications listed per SKU; custom packing confirmed by inquiry",
        }
    else:
        return
    for old, new in replacements.items():
        assert old in page, f"{path.name}: missing expected category wording: {old[:65]}"
        page = page.replace(old, new)
    page = re.sub(r'<title>.*?</title>', '<title>' + html.escape(meta_title) + '</title>', page, count=1, flags=re.S)
    for attr in ['name="description"', 'property="og:description"', 'name="twitter:description"']:
        page = re.sub(r'(<meta ' + re.escape(attr) + r' content=")[^"]*(")', lambda m: m[1] + html.escape(meta_description, quote=True) + m[2], page)
    for attr in ['property="og:title"', 'name="twitter:title"']:
        page = re.sub(r'(<meta ' + re.escape(attr) + r' content=")[^"]*(")', lambda m: m[1] + html.escape(meta_title, quote=True) + m[2], page)

    def patch_collection(match):
        value = json.loads(match[1])
        if value.get("@type") == "CollectionPage":
            value["description"] = meta_description
        return '<script type="application/ld+json">' + json.dumps(value, ensure_ascii=False, separators=(",", ":")) + '</script>'

    page = re.sub(r'<script type="application/ld\+json">(.*?)</script>', patch_collection, page, flags=re.S)
    path.write_text(page, encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--workbook", type=Path, required=True)
    parser.add_argument("--plan", type=Path, required=True)
    args = parser.parse_args()
    plans = json.loads(args.plan.read_text())
    workbook = openpyxl.load_workbook(args.workbook, data_only=True, read_only=True)
    sheet = workbook["Sheet1"]
    source_rows = list(sheet.values)
    headers = source_rows[0]
    records = {}
    for source_row, values in enumerate(source_rows[1:], 2):
        if not values[0]:
            continue
        raw = dict(zip(headers, values))
        sku = raw["sku"].strip()
        assert sku not in records, f"Duplicate source SKU: {sku}"
        records[sku] = (source_row, raw)
    workbook.close()
    batch_skus = {p["sku"] for p in plans}
    assert len(plans) == 16 and batch_skus == set(records)
    cat_path = ROOT / "assets/data/product-catalog.json"
    pdp_path = ROOT / "assets/data/pdp-data.json"
    copy_path = ROOT / "assets/data/pdp-copy.json"
    detail_path = ROOT / "assets/data/pdp-description-details.json"
    catalog = json.loads(cat_path.read_text())
    pdp = json.loads(pdp_path.read_text())
    copies = json.loads(copy_path.read_text())
    details = json.loads(detail_path.read_text())
    flat_before = [p for c in catalog["categories"] for p in c["products"]]
    existing = {p["sku"] for p in flat_before} & batch_skus
    assert existing == {"CDK080"}, f"Unexpected existing batch SKU(s): {existing}"
    before_count = len(flat_before)
    before_categories = {c["slug"]: len(c["products"]) for c in catalog["categories"]}
    previous = {"catalog": copy.deepcopy(next(p for p in flat_before if p["sku"] == "CDK080")),
                "pdp": copy.deepcopy(next(p for p in pdp if p["sku"] == "CDK080")),
                "copy": copy.deepcopy(copies["cdk080"])}
    baseline = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    by_slug = {c["slug"]: c for c in catalog["categories"]}
    for category in catalog["categories"]:
        category["products"] = [p for p in category["products"] if p["sku"] != "CDK080"]
    pdp = [p for p in pdp if p["sku"] != "CDK080"]
    new_by_category = {}
    new_rows = []
    entries = []
    manifest_products = []
    for plan in plans:
        sku, key = plan["sku"], plan["key"]
        source_row, raw = records[sku]
        assert key == sku.lower()
        expected_category = "resin-charms" if raw["分类"].strip() in {"resin  charms", "resin accessories"} else "keychain" if raw["分类"].strip() == "Jewelry keychain" else "jewelry-accessories"
        assert plan["category"] == expected_category, (sku, expected_category)
        category = by_slug[plan["category"]]
        images = plan["imagesLocal"]
        assert len(images) == 3 and len(set(images)) == 3
        image_records = []
        for role, rel in enumerate(images, 1):
            assert rel.startswith(f"assets/images/pdp/{key}/{key}-{role}-"), (sku, rel)
            path = ROOT / rel
            with Image.open(path) as im:
                w, h = im.size
                assert w <= 1000 and w > 0 and h > 0
                assert not im.getexif().get(34853), f"GPS metadata in {rel}"
            image_records.append({"path": rel, "role": ["main", "scene", "detail"][role-1], "width": w, "height": h,
                                  "sha256": sha256(path), "bytes": path.stat().st_size,
                                  "origin": "supplied reference" if role == 1 else "AI-assisted styling illustration",
                                  **({"prompt": plan["imagePrompts"][str(role)]} if role > 1 else {})})
        with Image.open(ROOT / images[0]) as im:
            w, h = im.size
        title = plan["title"]
        assert 80 <= len(plan["description"]) <= 160 and len(plan["metaTitle"]) <= 65
        query = f'quote.html?product={quote(sku + " " + title)}&sku={sku}&image={quote(images[0], safe="/")}'
        row = {"category": category["name"], "categorySlug": category["slug"], "sourceSheet": "Sheet1", "sourceRow": source_row,
               "sortOrder": 0, "sku": sku, "title": title, "titleFull": title, "titleShort": title,
               "sourceTitle": raw["标题"], "sourceCategory": raw["分类"],
               "alibabaUrl": previous["catalog"]["alibabaUrl"] if sku == "CDK080" else "",
               "cleanAlibabaUrl": previous["catalog"]["cleanAlibabaUrl"] if sku == "CDK080" else "",
               "alibabaProductId": previous["catalog"]["alibabaProductId"] if sku == "CDK080" else "",
               "image": images[0], "imageAlt": sku + " " + title, "imageWidth": w, "imageHeight": h,
               "imageHash": hashlib.md5((ROOT / images[0]).read_bytes()).hexdigest(), "status": "ok", "anchorNote": "",
               "pdp": f"p-{key}.html", "inquiryUrl": query}
        specs = specs_from_source(raw)
        assert raw["状态"] == "库存有货"
        entry = {"catalogIndex": 0, "assetKey": key, "sku": sku, "category": category["name"], "categorySlug": category["slug"],
                 "url": row["cleanAlibabaUrl"], "status": "ok", "reason": "", "titleFull": raw["标题"],
                 "moq": "", "priceTiers": [], "stockStatus": "In stock; confirm the available quantity when requesting a quote",
                 "specs": specs, "images": [], "imagesLocal": images, "sourceWorkbook": args.workbook.name,
                 "sourceSheet": "Sheet1", "sourceRow": source_row, "sourceFields": raw,
                 "importedAt": datetime.now(timezone.utc).isoformat(), "metaTitle": plan["metaTitle"],
                 "metaDescription": plan["description"], "shortProductDescription": plan["description"]}
        copies[key] = {"sku": sku, "displayTitle": title, "metaTitle": plan["metaTitle"], "metaDescription": plan["description"], "isFamilyFriendly": True}
        details[key] = plan["description"]
        new_rows.append(row)
        entries.append(entry)
        new_by_category.setdefault(category["slug"], []).append(row)
        manifest_products.append({"sku": sku, "sourceRow": source_row, "sourceFields": raw, "displayTitle": title,
                                  "category": category["name"], "categorySlug": category["slug"], "pdp": row["pdp"],
                                  "operation": "update existing" if sku == "CDK080" else "new", "sourceImage": plan["source"],
                                  "sourceImageSha256": plan["sourceImageSha256"], "imageOutputs": image_records})
    for category in catalog["categories"]:
        category["products"] = new_by_category.get(category["slug"], []) + category["products"]
        category["productCount"] = len(category["products"])
        for order, row in enumerate(category["products"], 1):
            row["sortOrder"] = order
    flat = [p for c in catalog["categories"] for p in c["products"]]
    pdp.extend(entries)
    indices = {p["pdp"]: i for i, p in enumerate(flat, 1)}
    for entry in pdp:
        entry["catalogIndex"] = indices[f'p-{entry["assetKey"]}.html']
    catalog.update(totalProducts=len(flat), totalImages=len(flat), generatedAt=datetime.now(timezone.utc).isoformat())
    assert len(flat) == before_count + 15
    assert Counter(p["sku"] for p in flat)["CDK080"] == 1
    for path, value, indent in [(cat_path, catalog, 1), (pdp_path, pdp, 2), (copy_path, copies, 2), (detail_path, details, 2)]:
        save_json(path, value, indent)

    # Only generate this batch; preserve all unrelated PDP-specific customizations.
    generator = (ROOT / "scripts/gen_pdp.py").read_text().split("# ---- 2)")[0]
    target = 'for e in pdp:\n    sku, key'
    assert generator.count(target) == 1
    generator = generator.replace(target, 'for e in pdp:\n    if e["sku"] not in BATCH_SKUS: continue\n    sku, key')
    exec(compile(generator, str(ROOT / "scripts/gen_pdp.py"), "exec"), {"__file__": str(ROOT / "scripts/gen_pdp.py"), "BATCH_SKUS": batch_skus})
    for row, entry in zip(new_rows, entries):
        path = ROOT / row["pdp"]
        page = path.read_text()
        page = page.replace("Decorative craft material — non-edible. Batch test reports (EN 71, ASTM F963, CPC, REACH) available on request.",
                            "Confirm the exact assortment, minimum order quantity and dispatch date with your inquiry.")
        page, count = re.subn(r'<div class="answer-box" style="margin:14px 0">.*?</div>',
                              '<div class="answer-box" style="margin:14px 0"><b>Wholesale pricing by quotation</b> · Minimum order quantity confirmed by inquiry.</div>', page, count=1, flags=re.S)
        assert count == 1
        page = page.replace('detail view 2', 'styled scene illustration').replace('detail view 3', 'styled detail illustration')
        marker = '</div>\n<div>\n  <div class="answer-box"'
        assert marker in page
        note = '<p class="pdp-image-note" style="font-size:.85rem;color:#667085">Image 1: supplied product reference. Images 2–3: styled illustrations. Props are not included; confirm the exact assortment before ordering.</p>'
        page = page.replace(marker, note + marker, 1)
        page, count = re.subn(r'quote\.html\?product=[^"<>]+', html.escape(row["inquiryUrl"], quote=True), page, count=1)
        assert count == 1
        path.write_text("\n".join(line.rstrip() for line in page.splitlines()) + "\n", encoding="utf-8")

    changed_files = []
    for slug, rows in new_by_category.items():
        category = by_slug[slug]
        path = ROOT / (slug + ".html")
        page = path.read_text()
        if slug == "jewelry-accessories":
            page, removed = re.subn(r'<article class="product-card"[^>]*>(?:(?!</article>).)*<span class="pill soft">CDK080</span>(?:(?!</article>).)*</article>', "", page, flags=re.S)
            assert removed == 1
        first = re.search(r'<article class="product-card"', page)
        assert first
        page = page[:first.start()] + "".join(card(row) for row in rows) + page[first.start():]

        def schema_patch(match):
            value = json.loads(match[1])
            if value.get("@type") == "ItemList":
                value.update(numberOfItems=len(category["products"]), itemListElement=[catalog_list_item(p, n) for n, p in enumerate(category["products"], 1)])
            return '<script type="application/ld+json">' + json.dumps(value, ensure_ascii=False, separators=(",", ":")) + '</script>'

        page = re.sub(r'<script type="application/ld\+json">(.*?)</script>', schema_patch, page, flags=re.S)
        path.write_text(page, encoding="utf-8")
        changed_files.append(path.name)

    for page in ["keychain.html", "jewelry-accessories.html"]:
        update_category_copy(ROOT / page)

    # References to the existing SKU also use the updated title and main image.
    updated_row = next(p for p in new_rows if p["sku"] == "CDK080")
    updated_reference_pages = []
    for path in ROOT.glob("*.html"):
        if path.name in changed_files or path.name == "p-cdk080.html":
            continue
        page = path.read_text()

        def refresh_reference(match):
            text = match[0]
            if '<span class="pill soft">CDK080</span>' not in text:
                return text
            image = f'<img loading="lazy" src="{updated_row["image"]}" alt="{html.escape(updated_row["imageAlt"])}" width="{updated_row["imageWidth"]}" height="{updated_row["imageHeight"]}">'
            text = re.sub(r'<img\b[^>]*>', image, text, count=1)
            text = re.sub(r'<h3>.*?</h3>', f'<h3><a href="p-cdk080.html" style="color:inherit;text-decoration:none">{html.escape(updated_row["title"])}</a></h3>', text, count=1, flags=re.S)
            text = re.sub(r'data-title="[^"]*"', f'data-title="{html.escape(updated_row["title"])}"', text)
            text = re.sub(r'quote\.html\?product=[^"<>]+', html.escape(updated_row["inquiryUrl"], quote=True), text)
            return text

        refreshed = CARD.sub(refresh_reference, page)
        if refreshed != page:
            path.write_text(refreshed, encoding="utf-8")
            updated_reference_pages.append(path.name)

    sitemap = ROOT / "sitemap.xml"
    xml = sitemap.read_text()
    for row, entry in zip(new_rows, entries):
        loc = BASE + row["pdp"]
        node = '<url><loc>' + loc + '</loc><lastmod>' + DATE + '</lastmod><changefreq>monthly</changefreq><priority>0.7</priority>'
        node += "".join(f'<image:image><image:loc>{BASE + p}</image:loc><image:title>{html.escape(row["sku"] + " " + row["title"])}</image:title></image:image>' for p in entry["imagesLocal"])
        node += '</url>'
        escaped_loc = re.escape(loc)
        pattern = r'<url>\s*<loc>' + escaped_loc + r'</loc>.*?</url>'
        if re.search(pattern, xml, re.S):
            xml = re.sub(pattern, lambda m: node, xml, count=1, flags=re.S)
        else:
            xml = xml.replace('</urlset>', '  ' + node + '\n</urlset>')
    for page in changed_files:
        loc = re.escape(BASE + page)
        xml = re.sub(r'(<loc>' + loc + r'</loc>\s*<lastmod>)[^<]+', r'\g<1>' + DATE, xml)
    sitemap.write_text(xml, encoding="utf-8")
    llms_path = ROOT / "llms-full.txt"
    llms = llms_path.read_text()
    llms = re.sub(r'^.*\(https://www\.qulacrafts\.com/p-cdk080\.html\).*$\n?', '', llms, flags=re.M)
    llms = llms.replace(f'({before_count} live stock items)', f'({len(flat)} live stock items)')
    for slug, rows in new_by_category.items():
        heading = '## ' + by_slug[slug]["name"] + '\n'
        assert heading in llms
        lines = ''.join(f'- [{row["title"]}]({BASE + row["pdp"]}): SKU {row["sku"]} · ' + next(e for e in entries if e["sku"] == row["sku"])["specs"].get("Standard pack", "Packing by inquiry") + ' · MOQ and pricing by quotation\n' for row in rows)
        llms = llms.replace(heading, heading + lines, 1)
    llms_path.write_text(llms, encoding="utf-8")
    llms_short = ROOT / "llms.txt"
    text = llms_short.read_text()
    text = re.sub(r'## Products \(\d+ categories, \d+ live stock items\)', f'## Products ({len(catalog["categories"])} categories, {len(flat)} live stock items)', text)
    llms_short.write_text(text, encoding="utf-8")
    manifest = {"batchId": "qula-products-20261012", "target": "QULA", "baselineCommit": baseline,
                "sourceWorkbook": args.workbook.name, "sourceWorkbookSha256": sha256(args.workbook),
                "catalogCountBefore": before_count, "catalogCountAfter": len(flat), "newProductCount": 15, "updatedProductCount": 1,
                "imageCount": 48, "sourceCategoryMapping": {"resin charms / resin accessories": "Resin Charms", "Jewelry keychain": "Keychain", "charms / Jewelry earrings / Jewelry charms": "Jewelry Accessories"},
                "userCorrections": ["CDK25805 confirmed by user; source image named RW25805.png."],
                "categoryCountsBefore": before_categories, "categoryCountsAfter": {c["slug"]: len(c["products"]) for c in catalog["categories"]},
                "previousCDK080Records": previous, "updatedReferencePages": updated_reference_pages,
                "products": manifest_products, "validationStatus": "pending"}
    save_json(ROOT / "docs/product-batch-manifest-20261012.json", manifest)
    print(json.dumps({"new": 15, "updated": 1, "catalogBefore": before_count, "catalogAfter": len(flat), "images": 48, "updatedReferencePages": updated_reference_pages}))


if __name__ == "__main__":
    main()
