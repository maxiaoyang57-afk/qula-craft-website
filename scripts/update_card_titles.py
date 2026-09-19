#!/usr/bin/env python3
"""Synchronize product-card titles from the canonical product catalog.

Only card-facing fields are changed: visible card headings, card data-title
attributes, and ItemList names. PDP H1/meta/Product schema content is left
untouched. Use --check in CI or before publishing to verify synchronization.
"""

from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path
from urllib.parse import urlparse


SITE = Path(__file__).resolve().parents[1]
CATALOG_PATH = SITE / "assets/data/product-catalog.json"
CARD_RE = re.compile(r'<article\s+class="product-card"[^>]*>.*?</article>', re.S)
H3_RE = re.compile(r'(<h3\b[^>]*>)(.*?)(</h3>)', re.S | re.I)
ANCHOR_RE = re.compile(r'(<a\b[^>]*>)(.*?)(</a>)', re.S | re.I)
DATA_TITLE_RE = re.compile(r'(\bdata-title=")[^"]*(")', re.I)
PDP_HREF_RE = re.compile(r'href="(p-[^"]+\.html)"', re.I)
JSON_LD_RE = re.compile(
    r'(<script\s+type="application/ld\+json">)(.*?)(</script>)', re.S | re.I
)


def clean_text(value: str) -> str:
    return " ".join(html.unescape(re.sub(r"<[^>]+>", "", value)).split())


def load_titles() -> dict[str, str]:
    catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    titles: dict[str, str] = {}
    for category in catalog["categories"]:
        for product in category["products"]:
            pdp = str(product.get("pdp", "")).lower()
            title = str(product.get("titleShort") or product.get("title") or "").strip()
            if not pdp or not title:
                raise ValueError(f"Missing PDP/card title for SKU {product.get('sku')}")
            if pdp in titles:
                raise ValueError(f"Duplicate PDP slug in catalog: {pdp}")
            titles[pdp] = title
    return titles


def patch_card(block: str, title: str) -> str:
    escaped = html.escape(title, quote=True)
    block = DATA_TITLE_RE.sub(lambda match: match.group(1) + escaped + match.group(2), block)

    def patch_h3(match: re.Match[str]) -> str:
        inner = match.group(2)
        if ANCHOR_RE.search(inner):
            inner = ANCHOR_RE.sub(
                lambda anchor: anchor.group(1) + escaped + anchor.group(3), inner, count=1
            )
        else:
            inner = escaped
        return match.group(1) + inner + match.group(3)

    patched, count = H3_RE.subn(patch_h3, block, count=1)
    if count != 1:
        raise ValueError("Product card is missing an H3 title")
    return patched


def patch_item_list(raw: str, titles: dict[str, str]) -> tuple[str, int]:
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return raw, 0
    if not isinstance(data, dict) or data.get("@type") != "ItemList":
        return raw, 0

    changed = 0
    for item in data.get("itemListElement", []):
        if not isinstance(item, dict):
            continue
        pdp = Path(urlparse(str(item.get("url", ""))).path).name.lower()
        title = titles.get(pdp)
        if title and item.get("name") != title:
            item["name"] = title
            changed += 1
    if not changed:
        return raw, 0
    return json.dumps(data, ensure_ascii=False, separators=(",", ":")), changed


def process_file(path: Path, titles: dict[str, str], write: bool) -> tuple[int, int, set[str]]:
    source = path.read_text(encoding="utf-8")
    card_count = 0
    item_count = 0
    seen: set[str] = set()

    def card_callback(match: re.Match[str]) -> str:
        nonlocal card_count
        block = match.group(0)
        href_match = PDP_HREF_RE.search(block)
        if not href_match:
            return block
        pdp = href_match.group(1).lower()
        title = titles.get(pdp)
        if not title:
            return block
        card_count += 1
        seen.add(pdp)
        return patch_card(block, title)

    output = CARD_RE.sub(card_callback, source)

    def json_ld_callback(match: re.Match[str]) -> str:
        nonlocal item_count
        patched, changed = patch_item_list(match.group(2), titles)
        item_count += changed
        return match.group(1) + patched + match.group(3)

    output = JSON_LD_RE.sub(json_ld_callback, output)
    if write and output != source:
        path.write_text(output, encoding="utf-8")
    return card_count, item_count, seen


def verify_file(path: Path, titles: dict[str, str]) -> tuple[int, set[str], list[str]]:
    source = path.read_text(encoding="utf-8")
    count = 0
    seen: set[str] = set()
    errors: list[str] = []

    for match in CARD_RE.finditer(source):
        block = match.group(0)
        href_match = PDP_HREF_RE.search(block)
        if not href_match:
            continue
        pdp = href_match.group(1).lower()
        title = titles.get(pdp)
        if not title:
            continue
        count += 1
        seen.add(pdp)
        h3_match = H3_RE.search(block)
        actual = clean_text(h3_match.group(2)) if h3_match else ""
        if actual != title:
            errors.append(f"{path.name}: {pdp} H3 is {actual!r}, expected {title!r}")
        for value in re.findall(r'\bdata-title="([^"]*)"', block, re.I):
            if html.unescape(value) != title:
                errors.append(
                    f"{path.name}: {pdp} data-title is {html.unescape(value)!r}, expected {title!r}"
                )

    for match in JSON_LD_RE.finditer(source):
        try:
            data = json.loads(match.group(2))
        except json.JSONDecodeError:
            continue
        if not isinstance(data, dict) or data.get("@type") != "ItemList":
            continue
        for item in data.get("itemListElement", []):
            if not isinstance(item, dict):
                continue
            pdp = Path(urlparse(str(item.get("url", ""))).path).name.lower()
            title = titles.get(pdp)
            if title and item.get("name") != title:
                errors.append(
                    f"{path.name}: {pdp} ItemList name is {item.get('name')!r}, expected {title!r}"
                )
    return count, seen, errors


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="verify only; do not write files")
    args = parser.parse_args()
    titles = load_titles()
    html_files = sorted(SITE.glob("*.html"))

    if not args.check:
        cards = items = 0
        seen: set[str] = set()
        for path in html_files:
            card_count, item_count, file_seen = process_file(path, titles, write=True)
            cards += card_count
            items += item_count
            seen.update(file_seen)
        print(f"Updated {cards} card occurrences and {items} ItemList names across {len(html_files)} HTML files")
        print(f"Products represented in cards: {len(seen)}/{len(titles)}")

    cards = 0
    seen: set[str] = set()
    errors: list[str] = []
    for path in html_files:
        card_count, file_seen, file_errors = verify_file(path, titles)
        cards += card_count
        seen.update(file_seen)
        errors.extend(file_errors)
    missing = sorted(set(titles) - seen)
    if missing:
        errors.append(f"Catalog products without a card occurrence: {', '.join(missing)}")
    if errors:
        raise SystemExit("\n".join(errors[:30]))
    print(f"Verified {cards} card occurrences for {len(seen)}/{len(titles)} products")


if __name__ == "__main__":
    main()
