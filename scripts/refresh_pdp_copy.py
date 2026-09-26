# -*- coding: utf-8 -*-
"""Refresh buyer-facing QULA copy without rebuilding the legacy page shell."""

from __future__ import annotations

import html
import json
import re
from pathlib import Path
from urllib.parse import quote

from pdp_public_copy import meta_description, meta_title, normalize_moq, public_title, sanitize_schema_value


SITE = Path(__file__).resolve().parents[1]
DATA = SITE / "assets/data"
PDP = json.loads((DATA / "pdp-data.json").read_text(encoding="utf-8"))
VERIFIED_DESCRIPTIONS = json.loads((DATA / "pdp-meta-descriptions.json").read_text(encoding="utf-8"))


def esc(value: str) -> str:
    return html.escape(value, quote=True)


copy_rows = {}
for entry in PDP:
    display = public_title(entry)
    description = meta_description(entry, display, VERIFIED_DESCRIPTIONS)
    title = meta_title(entry, display)
    assert display, f"{entry['sku']}: missing display title"
    assert 80 <= len(description) <= 160, f"{entry['sku']}: description length {len(description)}"
    copy_rows[entry["assetKey"]] = {
        "sku": entry["sku"],
        "displayTitle": display,
        "metaTitle": title,
        "metaDescription": description,
        "isFamilyFriendly": entry["sku"] != "MA118",
    }

(DATA / "pdp-copy.json").write_text(
    json.dumps(copy_rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)


def replace_meta(content: str, *, name: str | None = None, prop: str | None = None, value: str) -> str:
    attr = "name" if name else "property"
    target = name or prop
    pattern = rf'(<meta\s+[^>]*{attr}="{re.escape(target)}"[^>]*content=")[^"]*(")'
    return re.sub(pattern, lambda match: match.group(1) + esc(value) + match.group(2), content, count=1, flags=re.I)


def update_product_jsonld(content: str, row: dict) -> str:
    pattern = re.compile(r'(<script type="application/ld\+json">)(.*?)(</script>)', re.S)

    def update(match):
        try:
            data = json.loads(html.unescape(match.group(2)))
        except json.JSONDecodeError:
            return match.group(0)
        if data.get("@type") != "Product":
            return match.group(0)
        data["name"] = row["displayTitle"]
        data["description"] = row["metaDescription"]
        data["isFamilyFriendly"] = row["isFamilyFriendly"]
        for key in ("material", "color", "pattern", "size"):
            if key in data:
                data[key] = sanitize_schema_value(data[key])
        for prop in data.get("additionalProperty", []):
            if "value" in prop:
                prop["value"] = sanitize_schema_value(prop["value"])
        manufacturer = data.get("manufacturer")
        if isinstance(manufacturer, dict) and manufacturer.get("legalName") == "Yiwu Sola Craft Co., Ltd":
            manufacturer["legalName"] = "Yiwu Sola Craft Co., Ltd."
        offers = data.get("offers")
        if isinstance(offers, dict):
            seller = offers.get("seller")
            if isinstance(seller, dict) and seller.get("legalName") == "Yiwu Sola Craft Co., Ltd":
                seller["legalName"] = "Yiwu Sola Craft Co., Ltd."
        return match.group(1) + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + match.group(3)

    return pattern.sub(update, content)


for entry in PDP:
    sku = entry["sku"]
    row = copy_rows[entry["assetKey"]]
    page = SITE / f"p-{entry['assetKey']}.html"
    content = page.read_text(encoding="utf-8")
    content = re.sub(r"<title>.*?</title>", f"<title>{esc(row['metaTitle'])}</title>", content, count=1, flags=re.S)
    content = replace_meta(content, name="description", value=row["metaDescription"])
    content = replace_meta(content, prop="og:title", value=row["metaTitle"])
    content = replace_meta(content, prop="og:description", value=row["metaDescription"])
    content = replace_meta(content, name="twitter:title", value=row["metaTitle"])
    content = replace_meta(content, name="twitter:description", value=row["metaDescription"])
    keywords = f"{sku}, {row['displayTitle']}, {entry['category']} wholesale, bulk craft supplies"
    content = replace_meta(content, name="keywords", value=keywords)
    content = re.sub(r"(<h1[^>]*>).*?(</h1>)", lambda m: m.group(1) + esc(row["displayTitle"]) + m.group(2), content, count=1, flags=re.S)
    content = re.sub(
        r'(<div class="gallery-main"><img\b[^>]*\balt=")[^"]*(")',
        lambda m: m.group(1) + esc(f"{sku} {row['displayTitle']}") + m.group(2),
        content,
        count=1,
        flags=re.S,
    )
    encoded_product = quote(row["displayTitle"], safe="")
    content = re.sub(
        rf'(href="quote\.html\?product=)[^"&]*(&amp;sku={re.escape(sku)}|&sku={re.escape(sku)})',
        lambda m: m.group(1) + encoded_product + m.group(2),
        content,
        count=1,
    )
    content = re.sub(
        rf'(<a class="basket-add" data-sku="{re.escape(sku)}" data-title=")[^"]*(")',
        lambda m: m.group(1) + esc(row["displayTitle"]) + m.group(2),
        content,
        count=1,
    )
    for raw_value in (entry.get("specs") or {}).values():
        cleaned_value = sanitize_schema_value(str(raw_value))
        if cleaned_value != str(raw_value):
            content = content.replace(esc(str(raw_value)), esc(cleaned_value))
    raw_moq = str(entry.get("moq", ""))
    clean_moq = normalize_moq(raw_moq)
    if raw_moq and raw_moq != clean_moq:
        content = content.replace(esc(raw_moq), esc(clean_moq))
    content = update_product_jsonld(content, row)
    page.write_text(content, encoding="utf-8")


# Keep catalog/search/related-card titles consistent with each PDP while preserving
# the raw source title in pdp-data.json.
catalog_path = DATA / "product-catalog.json"
catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
for category in catalog["categories"]:
    for product in category["products"]:
        asset_key = Path(product.get("pdp", "")).stem.removeprefix("p-")
        row = copy_rows.get(asset_key)
        if row:
            product["title"] = row["displayTitle"]
            product["titleFull"] = row["displayTitle"]
            product["titleShort"] = row["displayTitle"]
            product["imageAlt"] = f"{product['sku']} {row['displayTitle']}"
catalog_path.write_text(json.dumps(catalog, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


# Replace exact source titles wherever catalog cards or related items are rendered.
text_targets = list(SITE.glob("*.html")) + [SITE / "assets/js/main.js"]
for path in text_targets:
    content = path.read_text(encoding="utf-8")
    original = content
    for entry in PDP:
        source = entry.get("titleFull", "")
        display = copy_rows[entry["assetKey"]]["displayTitle"]
        if source and source != display:
            content = content.replace(source, display).replace(esc(source), esc(display))
            content = content.replace(quote(source), quote(display))
    if content != original:
        path.write_text(content, encoding="utf-8")


copy_by_sku = {}
for row in copy_rows.values():
    copy_by_sku.setdefault(row["sku"], []).append(row)


def refresh_product_cards(content: str) -> str:
    pattern = re.compile(r'<article class="product-card"[\s\S]*?</article>')

    def update(match):
        card = match.group(0)
        sku_match = re.search(r'<span class="pill soft">([^<]+)</span>', card)
        if not sku_match:
            return card
        sku = html.unescape(sku_match.group(1)).strip()
        rows = copy_by_sku.get(sku, [])
        if not rows:
            return card
        # Only YM109 has two source pages. Card links disambiguate those records.
        row = rows[0]
        link_match = re.search(r'href="p-([^".]+)\.html"', card)
        if link_match and link_match.group(1) in copy_rows:
            row = copy_rows[link_match.group(1)]
        display = row["displayTitle"]
        card = re.sub(r'(\bdata-title=")[^"]*(")', lambda m: m.group(1) + esc(display) + m.group(2), card, count=1)
        card = re.sub(r'(<img\b[^>]*\balt=")[^"]*(")', lambda m: m.group(1) + esc(f"{sku} {display}") + m.group(2), card, count=1)
        card = re.sub(r'(<h3><a\b[^>]*>).*?(</a></h3>)', lambda m: m.group(1) + esc(display) + m.group(2), card, count=1, flags=re.S)
        encoded = quote(f"{sku} {display}", safe="")
        card = re.sub(r'(href="quote\.html\?product=)[^"&]*', lambda m: m.group(1) + encoded, card, count=1)
        card = re.sub(
            rf'(<a class="basket-add" data-sku="{re.escape(sku)}" data-title=")[^"]*(")',
            lambda m: m.group(1) + esc(display) + m.group(2),
            card,
            count=1,
        )
        return card

    return pattern.sub(update, content)


def refresh_itemlist_jsonld(content: str) -> str:
    pattern = re.compile(r'(<script type="application/ld\+json">)(.*?)(</script>)', re.S)

    def walk(value):
        if isinstance(value, list):
            for item in value:
                walk(item)
            return
        if not isinstance(value, dict):
            return
        if value.get("@type") == "ListItem":
            url = str(value.get("url", ""))
            match = re.search(r"/p-([^/]+)\.html$", url)
            if match and match.group(1) in copy_rows:
                value["name"] = copy_rows[match.group(1)]["displayTitle"]
        for item in value.values():
            walk(item)

    def update(match):
        try:
            data = json.loads(html.unescape(match.group(2)))
        except json.JSONDecodeError:
            return match.group(0)
        walk(data)
        return match.group(1) + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + match.group(3)

    return pattern.sub(update, content)


# Remove internal placeholders, awkward CTAs and unverified real-time stock wording.
page_replacements = {
    "factory.html": {
        "Suggested proof to replace later": "Workshop & Packing Evidence",
    },
    "customization.html": {
        "Support custom shapes, colors, mixes, logo labeling and packaging":
            "We support custom shapes, colors, mixes, logo labeling and packaging",
    },
    "about.html": {
        "Qula Craft is a B2B supplier concept for custom craft supplies":
            "Qula Craft is a B2B manufacturer and supplier of custom craft supplies",
        "Certified for Kids Channels": "Test Documentation for Kids’ Channels",
    },
    "index.html": {
        "Ask for solution →": "Request sourcing advice →",
    },
    "guide-clay-slices-vs-resin-charms-slime.html": {
        "Most successful slime shops run roughly a 70/30 budget split between the two.":
            "A practical starting point is to allocate more of the decoration budget to clay slices and use resin charms as focal pieces.",
        "Our production includes a colorfast check before shipping; see the quality & safety page for the full QC chain.":
            "Ask for a colorfastness check against the approved sample and intended slime formula before shipping.",
        "Quality slices don’t. Test any new supplier batch:":
            "Well-made slices should resist color bleed, but every new supplier batch should still be tested:",
        "We colorfast-test mixes before shipping.":
            "Confirm colorfastness against the approved sample and intended slime formula before shipping.",
    },
    "resin-charms.html": {
        "Standard craft adhesives — E6000-type glue and UV resin both bond well to the flat base. The surface is degreased before packing, so no extra prep is needed.":
            "Adhesive performance depends on the charm finish and end product. Test the selected adhesive on a sample, and keep the bonding surface clean and dry before assembly.",
        "We use UV-stabilized resin for clear pieces; colored and opaque charms are unaffected in normal retail conditions. Avoid months of direct sunlight in displays, as with any resin product.":
            "Resin appearance depends on formulation and storage. Confirm UV-resistance requirements for clear pieces, and avoid prolonged direct sunlight during storage or display.",
    },
}

stock_sentence = "Every item below is in production today — real SKU, real photo. Quote any SKU directly by button or WhatsApp."
stock_replacement = "Browse current catalog items with verified SKUs and product photos. Confirm availability, MOQ and lead time in your quotation."
related_sentence = "Every item below is a live stock listing — quote any SKU directly or"
related_replacement = "Browse related catalog items below — quote any SKU directly or"

for path in SITE.glob("*.html"):
    content = path.read_text(encoding="utf-8")
    content = refresh_product_cards(content)
    content = content.replace(stock_sentence, stock_replacement)
    content = content.replace(related_sentence, related_replacement)
    for old, new in page_replacements.get(path.name, {}).items():
        content = content.replace(old, new)
    content = refresh_itemlist_jsonld(content)
    path.write_text(content, encoding="utf-8")


# A source title can be a substring of another product title. Re-assert each
# PDP's own buyer-facing fields after the site-wide exact-title cleanup so a
# cross-product replacement cannot overwrite the page's H1 or CTA payload.
for entry in PDP:
    sku = entry["sku"]
    row = copy_rows[entry["assetKey"]]
    page = SITE / f"p-{entry['assetKey']}.html"
    content = page.read_text(encoding="utf-8")
    content = re.sub(
        r"(<h1[^>]*>).*?(</h1>)",
        lambda match: match.group(1) + esc(row["displayTitle"]) + match.group(2),
        content,
        count=1,
        flags=re.S,
    )
    content = re.sub(
        r'(<div class="gallery-main"><img\b[^>]*\balt=")[^"]*(")',
        lambda match: match.group(1) + esc(f"{sku} {row['displayTitle']}") + match.group(2),
        content,
        count=1,
        flags=re.S,
    )
    encoded_product = quote(row["displayTitle"], safe="")
    content = re.sub(
        rf'(href="quote\.html\?product=)[^"&]*(&amp;sku={re.escape(sku)}|&sku={re.escape(sku)})',
        lambda match: match.group(1) + encoded_product + match.group(2),
        content,
        count=1,
    )
    content = re.sub(
        rf'(<a class="basket-add" data-sku="{re.escape(sku)}" data-title=")[^"]*(")',
        lambda match: match.group(1) + esc(row["displayTitle"]) + match.group(2),
        content,
        count=1,
    )
    content = update_product_jsonld(content, row)
    page.write_text(content, encoding="utf-8")


# Refresh sitemap dates and image titles for every changed public page.
sitemap_path = SITE / "sitemap.xml"
sitemap = sitemap_path.read_text(encoding="utf-8")
changed_core_pages = {
    "", "about.html", "customization.html", "factory.html", "index.html",
    "guide-clay-slices-vs-resin-charms-slime.html", "products.html",
    "slime-charms.html", "polymer-clay-sprinkles.html", "resin-charms.html",
    "glitter-sequins-fillers.html", "pvc-plastic-charms.html", "acrylic-beads.html",
    "beads-for-pens.html", "keychain.html", "jewelry-accessories.html",
}

def refresh_sitemap_block(match):
    block = match.group(0)
    loc_match = re.search(r"<loc>https://www\.qulacrafts\.com/([^<]*)</loc>", block)
    if not loc_match:
        return block
    page_name = loc_match.group(1)
    asset_match = re.fullmatch(r"p-(.+)\.html", page_name)
    row = copy_rows.get(asset_match.group(1)) if asset_match else None
    if row or page_name in changed_core_pages:
        block = re.sub(r"<lastmod>[^<]+</lastmod>", "<lastmod>2026-09-26</lastmod>", block, count=1)
    if row:
        image_title = esc(f"{row['sku']} — {row['displayTitle']}")
        block = re.sub(r"<image:title>.*?</image:title>", f"<image:title>{image_title}</image:title>", block)
    return block

sitemap = re.sub(r"<url>.*?</url>", refresh_sitemap_block, sitemap, flags=re.S)
sitemap_path.write_text(sitemap, encoding="utf-8")

print(f"Refreshed public copy for {len(PDP)} PDPs")
