#!/usr/bin/env python3
"""Suppress product prices when the displayed unit conflicts with the MOQ unit.

The source catalog occasionally exposes a per-piece price beside a bag MOQ (or
the reverse).  There is no verified conversion between those units, so the
only truthful public representation is a quantity-based quote.
"""

from __future__ import annotations

import json
import re
from pathlib import Path


SITE = Path(__file__).resolve().parents[1]
PRICE_BLOCK = re.compile(
    r'<div class="answer-box" style="margin:14px 0"><b>From \$[^<]+ / '
    r'(?P<unit>[^<]+)</b> · MOQ (?P<moq>[^—<]+) — tiered pricing by quantity; '
    r'the full tier table comes back with your quote within 12&#8211;24 hours\.</div>'
)
PRICE_CLAUSE = re.compile(
    r'\. from \$[\d,.]+/(?:pieces|piece|pcs|pc|pairs|pair|bags|bag|boxes|box|sets|set|rolls|roll)\b',
    re.I,
)
LLMS_PRICE = re.compile(
    r' · from \$[\d,.]+/(?:pieces|piece|pcs|pc|pairs|pair|bags|bag|boxes|box|sets|set|rolls|roll)\b',
    re.I,
)
QUOTED_BLOCK = re.compile(
    r'<b>Quoted by pack and quantity</b> · MOQ (?P<moq>[^—<]+) — '
)
MOQ_SENTENCE = re.compile(r'MOQ [^.]+\. From Yiwu')


def family(text: str) -> str | None:
    text = text.lower()
    if re.search(r"\b(?:bag|bags|box|boxes|set|sets|roll|rolls)\b", text):
        return "pack"
    if re.search(r"\b(?:pc|pcs|piece|pieces|pair|pairs)\b", text):
        return "piece"
    return None


def clean_price_clause(text: str) -> str:
    return PRICE_CLAUSE.sub("", text)


def repair_moq_sentence(text: str, moq: str) -> str:
    """Keep metadata MOQ wording aligned with the verified visible MOQ."""
    return MOQ_SENTENCE.sub(f"MOQ {moq}. From Yiwu", text)


def patch_json_ld(match: re.Match[str]) -> str:
    raw = match.group(1)
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return match.group(0)
    if data.get("@type") != "Product":
        return match.group(0)
    data.pop("offers", None)
    if isinstance(data.get("description"), str):
        data["description"] = clean_price_clause(data["description"])
    compact = json.dumps(data, ensure_ascii=False, separators=(", ", ": "))
    return f'<script type="application/ld+json">{compact}</script>'


def main() -> None:
    hardened: list[str] = []
    changed: list[str] = []
    for path in sorted(SITE.glob("p-*.html")):
        html = path.read_text(encoding="utf-8")
        original = html
        match = PRICE_BLOCK.search(html)
        if match:
            unit_family = family(match.group("unit"))
            moq = match.group("moq").strip()
            moq_unit_family = family(moq)
            if unit_family and moq_unit_family and unit_family != moq_unit_family:
                replacement = (
                    '<div class="answer-box" style="margin:14px 0"><b>Quoted by pack and quantity</b>'
                    f' · MOQ {moq} — the sales unit and full tier pricing are confirmed in your quote '
                    'within 12&#8211;24 hours.</div>'
                )
                html = PRICE_BLOCK.sub(replacement, html, count=1)
                html = clean_price_clause(html)
                html = re.sub(
                    r'<script type="application/ld\+json">(.*?)</script>',
                    patch_json_ld,
                    html,
                    flags=re.S,
                )
                hardened.append(path.name)

        quoted = QUOTED_BLOCK.search(html)
        if quoted:
            html = repair_moq_sentence(html, quoted.group("moq").strip())

        if html != original:
            path.write_text(html, encoding="utf-8")
            changed.append(path.name)

    if changed or "quantitys" in (SITE / "llms-full.txt").read_text(encoding="utf-8"):
        llms_path = SITE / "llms-full.txt"
        llms = llms_path.read_text(encoding="utf-8")
        for filename in hardened:
            slug = filename.removesuffix(".html")
            llms = re.sub(
                rf'(^- \[[^\n]+\]\(https://www\.qulacrafts\.com/{re.escape(slug)}\.html\):[^\n]+?)'
                r' · from \$[\d,.]+/(?:bag|pc|pcs|piece|pieces|pair|set|box|roll)',
                r'\1 · price confirmed by sales unit and quantity',
                llms,
                flags=re.I | re.M,
            )
        llms = re.sub(
            r'price confirmed by sales unit and quantitys\b',
            'price confirmed by sales unit and quantity',
            llms,
        )
        llms_path.write_text(llms, encoding="utf-8")

    print(f"Suppressed conflicting price/MOQ units on {len(hardened)} product pages.")
    print(f"Updated or repaired {len(changed)} product pages.")
    for filename in hardened:
        print(f"  {filename}")


if __name__ == "__main__":
    main()
