# -*- coding: utf-8 -*-
"""Buyer-facing PDP copy helpers.

The Alibaba capture in ``pdp-data.json`` remains the source record.  This
module only normalizes wording that is safe to publish: spelling, units and
marketplace-style filler.  It deliberately does not infer product facts.
"""

from __future__ import annotations

import re


PUBLIC_TITLE_OVERRIDES = {
    "RX399": "Mini Dinosaur Figures",
    "MSB401": "Butterfly Pendant Charms",
    "SC048": "Custom Jewelry Polishing Cloths",
    "MA118": "Adult-Themed Body Confetti Sequins",
}

PUBLIC_META_TITLE_OVERRIDES_BY_ASSET = {
    "rw5306": "Mini Wooden Honey Sticks Wholesale | RW5306",
    "ym228": "Artificial Snow for Slime Wholesale | YM228",
    "ym216": "Gummy Worm Resin Cabochons Wholesale | YM216",
    "czb26337": "Pig Resin Flatback Charms Wholesale | CZB26337",
    "msb394": "Rhinestone Alphabet Slide Beads Wholesale | MSB394",
    "ym109": "Iridescent Bingsu Beads Wholesale | YM109",
    "ym109-2": "Bingsu Beads for Slime Wholesale | YM109",
}

PUBLIC_DESCRIPTION_OVERRIDES_BY_ASSET = {
    "rx399": "Wholesale mixed-color mini dinosaur figures for craft, display and themed assortments. Reference SKU RX399 for MOQ, packing and quotation.",
    "yx4075": "Wholesale St. Patrick's Day polymer clay slices with clover, rainbow and green hat designs for slime and crafts. SKU YX4075; MOQ 1 bag.",
    "msb401": "Wholesale butterfly pendant charms with colorful inlays and gold-tone loops. MOQ 100 pieces; quote SKU MSB401 for current packing.",
    "ym109": "Wholesale iridescent bingsu beads for crunchy slime. Reference SKU YM109 to confirm MOQ, pack size, available colors and quotation.",
    "ym109-2": "Wholesale bingsu bead additives for fluffy and crunchy slime. Reference SKU YM109 for current MOQ, packing and quotation.",
}

PUBLIC_TEXT_REPLACEMENTS = (
    (r"\bLight Wight\b", "Lightweight"),
    (r"\bWight\b", "Weight"),
    (r"\bBreads\b", "Beads"),
    (r"\bPlearl\b", "Pearl"),
    (r"\bGllitter\b", "Glitter"),
    (r"\bDecorfor\b", "Decor for"),
    (r"\bPhoneCase\b", "Phone Case"),
    (r"\bNails Art\b", "Nail Art"),
    (r"\bDoll House\b", "Dollhouse"),
    (r"\b1bag\b", "1 bag"),
    (r"\bSt\.? Patrick Day\b", "St. Patrick's Day"),
    (r"\bPolymer Hot Clay\b", "Polymer Clay"),
    (r"\bHot Clay\b", "Polymer Clay"),
    (r"\bO Ring\b", "O-Ring"),
    (r"\bDiy\b", "DIY"),
    (r"\b3d\b", "3D"),
    (r"\bfor choose\b", "to choose from"),
    (r"\bSame as photo\b", "As shown"),
    (r"\bAs Picture\b", "As shown"),
    (r"\bOr Customized\b", "or custom colors"),
)

LEADING_MARKETPLACE_PHRASES = (
    "Hot Selling",
    "Hot Sale",
    "Popular Sale",
    "Popular New Product",
    "Now Product",
    "New Creative",
    "New Lovely",
    "New Fashion",
    "New Novelty",
    "High Quality",
)


def clean_public_text(value: str) -> str:
    text = str(value or "")
    for pattern, replacement in PUBLIC_TEXT_REPLACEMENTS:
        text = re.sub(pattern, replacement, text, flags=re.I)
    text = text.replace("*", " × ")
    text = re.sub(r"\b(\d+)\s*Pcs\b", r"\1 pcs", text, flags=re.I)
    text = re.sub(r"\b(\d+(?:\.\d+)?)\s*(KG|MM|CM|G)\b", lambda m: f"{m.group(1)} {m.group(2).lower()}", text, flags=re.I)
    text = re.sub(r"\s*/\s*(Bag|Lot|Pack|Packet)\b", lambda m: f"/{m.group(1).lower()}", text, flags=re.I)
    text = re.sub(r"\s+", " ", text).strip(" -.,")
    return text


def public_title(entry: dict) -> str:
    sku = entry["sku"]
    if sku in PUBLIC_TITLE_OVERRIDES:
        return PUBLIC_TITLE_OVERRIDES[sku]
    title = clean_public_text(entry.get("titleFull", ""))
    for phrase in LEADING_MARKETPLACE_PHRASES:
        title = re.sub(rf"^(?:Wholesale\s+|Bulk\s+)?{re.escape(phrase)}\s+", "", title, flags=re.I)
    title = re.sub(r"^(?:Popular\s+)?(?:New\s+)?Product\s+", "", title, flags=re.I)
    title = re.sub(r"\bCheap\b\s*", "", title, flags=re.I)
    title = re.sub(r"\s+", " ", title).strip(" -.,")
    return title


def meta_title(entry: dict, display_title: str) -> str:
    if entry["assetKey"] in PUBLIC_META_TITLE_OVERRIDES_BY_ASSET:
        return PUBLIC_META_TITLE_OVERRIDES_BY_ASSET[entry["assetKey"]]
    verified = clean_public_text(entry.get("metaTitle", ""))
    if verified:
        return verified
    candidate = f"{display_title} Wholesale | {entry['sku']}"
    if len(candidate) <= 65:
        return candidate
    return f"{entry['category']} Wholesale | {entry['sku']} | Qula Craft"


def normalize_moq(value: str) -> str:
    moq = clean_public_text(value)
    return re.sub(r"\b1Bag\b", "1 bag", moq, flags=re.I)


def meta_description(entry: dict, display_title: str, verified_overrides: dict) -> str:
    sku = entry["sku"]
    if entry["assetKey"] in PUBLIC_DESCRIPTION_OVERRIDES_BY_ASSET:
        return PUBLIC_DESCRIPTION_OVERRIDES_BY_ASSET[entry["assetKey"]]
    if sku in verified_overrides:
        return verified_overrides[sku]
    moq = normalize_moq(entry.get("moq", ""))
    detail = f" MOQ: {moq}." if moq else ""
    candidate = (
        f"{display_title}.{detail} Reference SKU {sku} for packing and current wholesale quotation."
    )
    if 80 <= len(candidate) <= 160:
        return candidate
    concise = f"{display_title}. SKU {sku}; request current MOQ, packing and quotation."
    if 80 <= len(concise) <= 160:
        return concise
    return (
        f"Wholesale {entry['category']} from Qula Craft. Reference SKU {sku} to confirm "
        f"product details, MOQ, packing and current quotation."
    )


def sanitize_schema_value(value):
    if isinstance(value, str):
        cleaned = clean_public_text(value)
        if cleaned.upper() == "COLORFUL":
            return "Assorted colors"
        return cleaned
    if isinstance(value, list):
        return [sanitize_schema_value(item) for item in value]
    if isinstance(value, dict):
        return {key: sanitize_schema_value(item) for key, item in value.items()}
    return value
