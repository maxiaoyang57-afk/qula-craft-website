"""Render curated selection notes without changing imported product facts.

The full PDP generator and the narrow existing-page update share this renderer.
Run this module to refresh only the six reviewed sections in published HTML.
"""
from __future__ import annotations

import html
import json
import re
from pathlib import Path
from urllib.parse import parse_qs, quote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
GUIDES = json.loads((ROOT / "assets/data/product-selection-guides.json").read_text(encoding="utf-8"))
CATEGORIES = {"yx043": "Polymer Clay Sprinkles", "yx3194": "Polymer Clay Sprinkles", "yx3301": "Polymer Clay Sprinkles", "ya425": "Acrylic Beads", "ya382": "Acrylic Beads", "czb26353": "Beads for Pens"}


def selection_quote_url(key: str, quote_url: str) -> str:
    """Add the missing category to reviewed legacy links, preserving other fields."""
    if key not in GUIDES:
        return quote_url
    destination = html.unescape(quote_url)
    if not destination.startswith("quote.html?"):
        raise ValueError(f"Unexpected inquiry destination for {key}")
    if "category" not in parse_qs(urlsplit(destination).query):
        destination += "&category=" + quote(CATEGORIES[key])
    return html.escape(destination)


def selection_jump(key: str) -> str:
    if key not in GUIDES:
        return ""
    return '<p class="small-note" data-selection-jump="' + key + '"><a href="#project-selection">Review project and sample checks before ordering →</a></p>'


def render_selection_guide(key: str, quote_url: str) -> str:
    if key not in GUIDES:
        return ""
    guide = GUIDES[key]
    esc = html.escape
    # Preserve the existing product's inquiry destination and all context fields.
    destination = html.unescape(selection_quote_url(key, quote_url))
    if not destination.startswith("quote.html?"):
        raise ValueError(f"Unexpected inquiry destination for {key}")
    checks = "".join("<li>" + esc(check) + "</li>" for check in guide["checks"])
    return (
        f'<!-- product-selection:start:{key} -->\n'
        f'<section class="section" id="project-selection" style="scroll-margin-top:110px" data-product-selection="{esc(guide["sku"])}"><div class="container">'
        f'<div class="section-head"><span class="eyebrow">Project &amp; Sample Planning</span><h2>{esc(guide["heading"])}</h2></div>'
        f'<div class="detail-grid"><div><h3>Choose your reference</h3><p>{esc(guide["project"])}</p>'
        f'<p><a href="{esc(guide["guide"]["url"])}">{esc(guide["guide"]["label"])} →</a></p>'
        f'<p><a href="{esc(guide["related"]["url"])}">{esc(guide["related"]["label"])} →</a></p></div>'
        f'<div><h3>What to include in your inquiry</h3><ul>{checks}</ul>'
        '<p>Include your required quantity, destination country and any design or packing changes so we can review the request together.</p>'
        '</div></div><p>'
        f'<a class="btn btn-primary" data-selection-inquiry="{esc(guide["sku"])}" href="{esc(destination)}">Discuss {esc(guide["sku"])} for my project <span>→</span></a>'
        '</p></div></section>\n'
        f'<!-- product-selection:end:{key} -->'
    )


def update_existing_pages() -> None:
    for key, guide in GUIDES.items():
        path = ROOT / f"p-{key}.html"
        before = path.read_text(encoding="utf-8")
        match = re.search(r'<a class="btn btn-primary" href="([^"]+)">Request Quote for ' + re.escape(guide["sku"]) + r'\b', before)
        if not match:
            raise ValueError(f"Missing original product inquiry for {key}")
        destination = selection_quote_url(key, match.group(1))
        before = before[:match.start(1)] + destination + before[match.end(1):]
        after = re.sub(r'<!-- product-selection:start:' + key + r' -->.*?<!-- product-selection:end:' + key + r' -->\n?', "", before, flags=re.S)
        after = re.sub(r'<p class="small-note" data-selection-jump="' + key + r'">.*?</p>\n?', "", after)
        cta = '  <div class="pdp-cta"'
        if after.count(cta) != 1:
            raise ValueError(f"Ambiguous primary CTA for {key}")
        after = after.replace(cta, selection_jump(key) + "\n" + cta, 1)
        related = '<section class="section section-soft">'
        if after.count(related) != 1:
            raise ValueError(f"Ambiguous related-products section for {key}")
        after = after.replace(related, render_selection_guide(key, destination) + "\n" + related, 1)
        path.write_text(after, encoding="utf-8")
        print(f"Updated selection guide: {guide['sku']}")


if __name__ == "__main__":
    update_existing_pages()
