"""Render each product's introduction and buying advice once.

Keep source records and editorial details intact. Compact, existing metadata is
used as the introduction when the old summary repeats the buying advice.
"""
import html

from pdp_public_copy import CONTENT_REVIEWS, PRODUCT_DETAILS


def normalized(text):
    return " ".join(str(text or "").split())


def product_summary(entry, copy):
    key = entry["assetKey"]
    review = CONTENT_REVIEWS.get(key, {})
    if review.get("summary"):
        return review["summary"]
    summary = PRODUCT_DETAILS.get(key, "")
    for name in ("projectUse", "selectionAdvice"):
        paragraph = normalized(copy.get(name))
        if len(paragraph.split()) >= 35 and paragraph in normalized(summary):
            return copy["metaDescription"]
    return summary


def buying_copy(entry, copy):
    result = {name: copy.get(name, "") for name in ("projectUse", "selectionAdvice", "variantSizeNotes")}
    review = CONTENT_REVIEWS.get(entry["assetKey"], {})
    result.update({name: review[name] for name in result if name in review})
    names = tuple(result)
    for index, name in enumerate(names):
        for other in names[index + 1:]:
            first, second = normalized(result[name]), normalized(result[other])
            if not first or not second:
                continue
            if second in first:
                result[other] = ""
            elif first in second:
                result[name] = ""
                break
    return result


def render_buying_guide(entry, copy):
    text = buying_copy(entry, copy)
    if not any(text.values()):
        return ""
    esc = html.escape
    columns = []
    if text["projectUse"]:
        columns.append('<div><h3>Project ideas</h3><p>' + esc(text["projectUse"]) + '</p></div>')
    if text["selectionAdvice"] or text["variantSizeNotes"]:
        paragraphs = ''.join('<p>' + esc(text[name]) + '</p>' for name in ("selectionAdvice", "variantSizeNotes") if text[name])
        columns.append('<div><h3>Before you choose</h3>' + paragraphs + '</div>')
    content = ''.join(columns)
    if len(columns) > 1:
        content = '<div class="detail-grid">' + content + '</div>'
    return ('<section class="section" data-product-buying-guide="' + esc(entry["sku"], quote=True) + '">'
            '<div class="container"><div class="section-head"><span class="eyebrow">Choose Your Reference</span>'
            '<h2>Plan your project with ' + esc(entry["sku"]) + '</h2></div>' + content + '</div></section>')
