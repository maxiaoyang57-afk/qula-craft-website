"""User-approved SC048 content, shared by its page and the PDP generator."""
import json
import re
from html import escape
from pathlib import Path
from urllib.parse import urlencode, quote


DESCRIPTION = (
    "SC048 8 × 8 cm microfiber jewelry cleaning cloth in 12 colors. "
    "Custom orders and logo customization available. Request a quote for your brand."
)
QUOTE_URL = "quote.html?" + urlencode({
    "product": "SC048 Jewelry Cleaning Cloth - Custom Logo Request",
    "sku": "SC048",
    "image": "assets/images/pdp/sc048/01.webp",
}, quote_via=quote)

INTRO = '''<section class="sc048-description" aria-labelledby="sc048-description-title">
    <h2 id="sc048-description-title">Product Description</h2>
    <p>Soft microfiber cloth with a suede-like finish. An 8 × 8 cm format in 12 colors, ideal for jewelry care kits, stores and branded gift sets.</p>
    <ul class="sc048-service-badges" aria-label="Customization services">
      <li>Custom Orders Welcome</li>
      <li>Custom Logo Available</li>
    </ul>
  </section>
  '''

CUSTOM_ROWS = '''<tr class="sc048-custom-row"><th scope="row">Customization</th><td>Custom orders accepted</td></tr>
  <tr class="sc048-custom-row"><th scope="row">Custom Logo</th><td>Available upon request</td></tr>'''

CUSTOM_SECTION = '''<section class="sc048-customization" id="sc048-customization" aria-labelledby="sc048-customization-title">
  <div class="container sc048-custom-grid">
    <figure class="sc048-logo-example">
      <img loading="lazy" decoding="async" src="assets/images/pdp/sc048/custom-logo-example.webp" width="1200" height="900" alt="Illustrative pink and sage jewelry cloths with YOUR LOGO placement on the pink cloth, beside a jewelry pouch and ring">
      <figcaption>Illustrative logo placement. Pouch and jewelry shown as styling props.</figcaption>
    </figure>
    <div class="sc048-custom-copy">
      <span class="eyebrow">Customization</span>
      <h2 id="sc048-customization-title">Your Brand. Your Logo.</h2>
      <p>We accept custom orders and offer logo customization for your jewelry cleaning cloths.</p>
      <ol class="sc048-custom-steps">
        <li><span aria-hidden="true">01</span>Send your logo file</li>
        <li><span aria-hidden="true">02</span>Tell us your quantity and requirements</li>
        <li><span aria-hidden="true">03</span>Receive your custom quotation</li>
      </ol>
      <a class="btn btn-primary sc048-custom-quote" href="__QUOTE_URL__">Request Custom Logo Quote <span aria-hidden="true">→</span></a>
      <p class="sc048-quotation-note">Available options, minimum quantities, pricing and production time are confirmed for each project.</p>
    </div>
  </div>
</section>
'''.replace("__QUOTE_URL__", escape(QUOTE_URL, quote=True))


def _replace_once(page, old, new):
    if page.count(old) != 1:
        raise ValueError(f"SC048 markup changed; expected one anchor: {old[:70]}")
    return page.replace(old, new, 1)


def apply_sc048_customization(page):
    """Apply only to SC048; do not regenerate unrelated product pages."""
    if 'href="https://www.qulacrafts.com/p-sc048.html"' not in page:
        raise ValueError("SC048 customization received a different product page")
    if 'id="sc048-customization"' in page:
        return page
    page = _replace_once(page, "</head>",
        '<link rel="stylesheet" href="assets/css/sc048-customization.css?v=20260910a">\n</head>')
    page, count = re.subn(r'<body(?: class="([^"]*)")?>',
        lambda m: '<body class="' + ((m.group(1) or "") + ' sc048-page').strip() + '">',
        page, count=1)
    if count != 1:
        raise ValueError("SC048 body element not found")
    page = _replace_once(page, '<section class="section" style="padding-top:26px">',
        '<section class="section sc048-product" style="padding-top:26px">')
    page = _replace_once(page, '<div class="answer-box"', INTRO + '<div class="answer-box"')
    page = _replace_once(page,
        '<tr><td><b>Stock status</b></td><td>Live production item</td></tr></table>',
        '<tr><td><b>Stock status</b></td><td>Live production item</td></tr>\n  ' + CUSTOM_ROWS + '</table>')
    page = _replace_once(page,
        '<p style="font-size:.85rem;color:#77808c;margin:10px 0 16px">Decorative craft material — non-edible. Batch test reports (EN 71, ASTM F963, CPC, REACH) available on request.</p>',
        '<p class="sc048-quotation-note">The listed MOQ applies to the standard item. Custom MOQ, pricing and lead time are confirmed by quotation.</p>')
    page = _replace_once(page, '<section class="section section-soft">',
        CUSTOM_SECTION + '<section class="section section-soft">')
    for selector in ('name="description"', 'property="og:description"'):
        page, count = re.subn(r'(<meta ' + selector + r' content=")[^"]*(">)',
            lambda m: m.group(1) + escape(DESCRIPTION, quote=True) + m.group(2), page, count=1)
        if count != 1:
            raise ValueError(f"SC048 metadata missing: {selector}")

    def update_product(match):
        data = json.loads(match.group(1))
        if data.get("@type") != "Product":
            return match.group(0)
        if data.get("sku") != "SC048":
            raise ValueError("SC048 Product schema has another SKU")
        data["description"] = DESCRIPTION
        data.setdefault("additionalProperty", []).extend([
            {"@type": "PropertyValue", "name": "Customization", "value": "Custom orders accepted"},
            {"@type": "PropertyValue", "name": "Custom Logo", "value": "Available upon request"},
        ])
        return '<script type="application/ld+json">' + json.dumps(data, ensure_ascii=False) + '</script>'

    return re.sub(r'<script type="application/ld\+json">(.*?)</script>', update_product, page, flags=re.S)


if __name__ == "__main__":
    path = Path(__file__).resolve().parents[1] / "p-sc048.html"
    path.write_text(apply_sc048_customization(path.read_text(encoding="utf-8")), encoding="utf-8")
