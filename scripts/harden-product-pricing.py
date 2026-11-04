#!/usr/bin/env python3
"""Apply QULA's inquiry-only pricing policy to every public product surface.

Historical listing tiers are not current quotations. Keep product facts, MOQ,
images and inquiry links intact while removing those tiers and public offers.
Run after a legacy import; the build guard also rejects any price regression.
"""

from __future__ import annotations

import argparse
import datetime
import json
import re
from pathlib import Path
from inquiry_schema import remove_inquiry_product_schema

SITE = Path(__file__).resolve().parents[1]
PRICE_BLOCK = re.compile(
    r'<div class="answer-box" style="margin:14px 0"><b>From \$[^<]+ / '
    r'(?P<unit>[^<]+)</b> · MOQ (?P<moq>[^—<]+) — tiered pricing by quantity; '
    r'the full tier table comes back with your quote within 12&#8211;24 hours\.</div>'
)
LLMS_PRICE = re.compile(
    r' · from \$[\d,.]+/(?:pieces|piece|pcs|pc|pairs|pair|bags|bag|boxes|box|sets|set|rolls|roll)\b',
    re.I,
)


def inquiry_source(entry: dict) -> dict:
    return {**entry, "priceTiers": [], "pricingMode": "quote_only"}


def inquiry_page(page: str) -> str:
    def quote(match: re.Match[str]) -> str:
        return (
            '<div class="answer-box" style="margin:14px 0"><b>Quoted by pack and quantity</b>'
            f' · MOQ {match["moq"].strip()} — full pricing comes back with your quote '
            'within 12&#8211;24 hours.</div>'
        )

    return remove_inquiry_product_schema(PRICE_BLOCK.sub(quote, page))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--date", type=datetime.date.fromisoformat, default=datetime.date.today())
    args = parser.parse_args()
    source = SITE / "assets/data/pdp-data.json"
    entries = json.loads(source.read_text(encoding="utf-8"))
    updated = [inquiry_source(entry) for entry in entries]
    source_changes = sum(old != new for old, new in zip(entries, updated))
    if source_changes:
        source.write_text(json.dumps(updated, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    changed = []
    for path in sorted(SITE.glob("p-*.html")):
        old = path.read_text(encoding="utf-8")
        new = inquiry_page(old)
        if new != old:
            path.write_text(new, encoding="utf-8")
            changed.append(path)

    llms = SITE / "llms-full.txt"
    old = llms.read_text(encoding="utf-8")
    new, llms_changes = LLMS_PRICE.subn("", old)
    if new != old:
        llms.write_text(new, encoding="utf-8")

    sitemap = SITE / "sitemap.xml"
    old = sitemap.read_text(encoding="utf-8")
    new = old
    for path in changed:
        pattern = r'(<loc>https://www\.qulacrafts\.com/' + re.escape(path.name) + r'</loc>\s*<lastmod>)[^<]+(</lastmod>)'
        new, count = re.subn(pattern, lambda match: match[1] + str(args.date) + match[2], new)
        if count != (0 if re.search(r'<meta[^>]+name="robots"[^>]+noindex', path.read_text(), re.I) else 1):
            raise ValueError(f"Unexpected sitemap coverage: {path.name}")
    if new != old:
        sitemap.write_text(new, encoding="utf-8")
    print(json.dumps({"source_records_updated": source_changes, "pages_updated": len(changed), "llms_prices_removed": llms_changes}))


if __name__ == "__main__":
    main()
