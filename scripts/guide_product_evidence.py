"""Curated, source-backed product photographs for existing buying guides."""
import html
import json
import re
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://www.qulacrafts.com/"
DATE = "2026-11-09"
PRODUCTS = {p["assetKey"]: p for p in json.loads((ROOT / "assets/data/pdp-data.json").read_text())}

# Descriptions identify only what is visible; dimensions and material are read
# from the catalog record, never estimated from a picture.
PHOTOS = {
    "ya425": ("Pastel heart beads in a dish beside a pen", "Heart acrylic beads", "Compare the listed 2.5 mm hole with your actual rod; the photograph does not establish pen fit."),
    "ya893": ("Colorful round beads with swirl patterns", "Swirl round acrylic beads", "Check hole diameter and the space each bead occupies on your selected pen blank."),
    "ya690": ("Translucent green leaf-shaped beads", "Leaf acrylic beads", "Confirm hole direction and how the leaf will face when threaded."),
    "ym109": ("Blue iridescent tube-style bingsu filler", "Iridescent bingsu reference", "This and the second YM109 listing share a main photograph. Specify the product link and approved sample."),
    "yt008": ("Transparent colorful rounded fishbowl-style pieces", "Fishbowl-style filler reference", "The source does not identify a specific material. Confirm it before comparing samples."),
    "yx053": ("Pink and white dragon-fruit patterned clay slices", "Dragon-fruit clay slices", "Compare a measured sample with the usable area of your jar lid or craft layout."),
    "yx124": ("Assorted colorful fruit slice decorations", "Larger fruit clay slices", "The size is a listed reference; confirm the selected design and assortment."),
    "rw967": ("White and yellow imitation fried-egg decorations", "Fried-egg resin decorations", "Request the reverse-side view and test adhesive contact before choosing a phone-case layout."),
    "rw474": ("Pastel candy-wrapper shaped decorations with Sweet lettering", "Candy resin decorations", "Confirm the selected color assortment and reverse side before ordering."),
    "rw26460": ("Miniature citrus and kiwi fruit decorations displayed on a hand", "Mini fruit resin decorations", "The hand is a scale reference in the source photograph; use the listed measurements for planning."),
}
GUIDES = {
    "guide-beadable-pen-beads.html": ("ya425", ["ya425", "ya893", "ya690"], "Compare the actual beads before choosing a pen layout", "These catalog photographs show the listed components. Pen blanks and styling props are included only when named in the quotation."),
    "guide-bingsu-beads-slime-fillers.html": ("ym109", ["ym109", "yt008"], "Compare the loose filler references", "Order by product link as well as SKU. The two YM109 references share their first photograph; this is not evidence that their selected batches are identical."),
    "guide-decoden-supplies.html": ("rw474", ["rw967", "rw474", "rw26460"], "Choose a size range from actual resin components", "Front photographs show the design. Confirm a flat reverse side and test your chosen adhesive, base and layout before assembling a collection."),
    "guide-clay-slices-vs-resin-charms-slime.html": ("yx053", ["yx053", "yx124", "rw26460"], "Compare a small slice, a larger slice and a resin focal", "All three are decorative, non-edible components. Appearance and listed size do not establish formula compatibility or a fixed dose."),
}

def esc(s):
    return html.escape(str(s), quote=True)

def facts(key):
    p = PRODUCTS[key]
    specs = p.get("specs", {})
    rows = []
    material = specs.get("Material", "")
    if material and material.lower() not in ("other", "unknown", "none"):
        rows.append(("Listed material", material.upper() if material.lower() == "pet" else material))
    else:
        rows.append(("Material", "Confirm for the selected reference"))
    size = specs.get("Size")
    if size:
        rows.append(("Listed size", size))
    pack = specs.get("Standard pack") or specs.get("Pack reference")
    if not pack and key == "ym109":
        pack = "500 g/bag (source listing reference)"
    if pack:
        rows.append(("Pack reference", pack))
    return rows

def cards(keys):
    chunks = []
    for key in keys:
        p = PRODUCTS[key]
        alt, title, note = PHOTOS[key]
        src = p["imagesLocal"][0]
        w, h = Image.open(ROOT / src).size
        chunks.append(f'<article style="min-width:0;border:1px solid #eadde3;border-radius:16px;padding:16px;background:#fff"><a href="p-{key}.html"><img loading="lazy" src="{esc(src)}" alt="{esc(p["sku"] + ": " + alt)}" width="{w}" height="{h}" style="display:block;width:100%;height:220px;object-fit:contain;background:#fff;border-radius:10px"></a><h3><a href="p-{key}.html">{esc(p["sku"])} · {esc(title)}</a></h3><dl>' + "".join(f'<dt><b>{esc(k)}</b></dt><dd style="margin:0 0 8px">{esc(v)}</dd>' for k,v in facts(key)) + f'</dl><p>{esc(note)}</p><a class="text-link" href="p-{key}.html">View product and request a quote →</a></article>')
    return '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,230px),1fr));gap:18px">' + "".join(chunks) + '</div>'

def apply(page):
    """Patch only the curated guide images and evidence section; keep its shell."""
    hero, keys, heading, intro = GUIDES[page]
    path = ROOT / page
    s = path.read_text()
    p = PRODUCTS[hero]
    src = p["imagesLocal"][0]
    w,h = Image.open(ROOT / src).size
    photo = f'<figure style="margin:26px 0"><a href="p-{hero}.html"><img loading="eager" fetchpriority="high" src="{esc(src)}" alt="{esc(p["sku"] + ": " + PHOTOS[hero][0])}" width="{w}" height="{h}" style="width:100%;height:auto;object-fit:contain;background:#fff;border-radius:18px;max-width:520px;display:block;margin:0 auto"></a><figcaption class="small-note" style="text-align:center;margin-top:8px">{esc(p["sku"])} catalog photograph. <a href="p-{hero}.html">See the supplied component and listed specifications</a>.</figcaption></figure>'
    evidence = f'<section data-guide-product-evidence="20261109"><h2>{heading}</h2><p>{intro}</p>{cards(keys)}<p class="small-note">Pack references describe the listed unit, not a minimum order or a counted yield. Confirm current MOQ, samples, assortment and dispatch date in your quotation.</p></section>'
    s = re.sub(r'<section data-guide-product-evidence="20261109">.*?</section>', '', s, flags=re.S)
    main = s.index('<main')
    before, body = s[:main], s[main:]
    body, n = re.subn(r'<figure\b[^>]*>.*?</figure>', lambda _: photo + evidence, body, count=1, flags=re.S)
    assert n == 1, page
    before = re.sub(r'(<meta (?:property|name)="(?:og:image|twitter:image)" content=")[^"]+', lambda m:m[1]+BASE+src, before)
    def schema(m):
        data = json.loads(m[1])
        if data.get('@type') == 'Article':
            data['image'] = BASE + src
            data['dateModified'] = DATE
        return '<script type="application/ld+json">' + json.dumps(data,ensure_ascii=False) + '</script>'
    before = re.sub(r'<script type="application/ld\+json">(.*?)</script>', schema, before, flags=re.S)
    body = re.sub(r'Updated (?:[A-Za-z]+ \d{1,2}, \d{4}|\d{1,2} [A-Za-z]+ \d{4})', 'Updated November 9, 2026', body, count=1)
    path.write_text(before + body)

CONTENT = {
    "guide-bingsu-beads-slime-fillers.html": {
        "file": "bingsu-buyer-body.html",
        "answer": "Choose a slime filler by its selected product reference and a measured trial in your own formula. The two YM109 listings identify PET and a 500 g reference pack, but share a main photograph. Confirm the exact reference, pack, sample and MOQ; test appearance and texture before scaling.",
        "faq": [("What are the YM109 bingsu references made of?", "Both source listings identify PET. This does not establish coating, color stability or compatibility with every slime formula. Confirm the selected reference and test an actual sample."), ("How many jars does a 500 g pack supply?", "Divide the available weight by your measured dose per jar, then allow for your actual packing process. A pack weight is not a recommended dose or a guaranteed yield."), ("Do the two YM109 references show different products?", "They share their first photograph and the same SKU. Use the exact product link and an approved sample to identify your selection; the photograph alone does not establish equivalence."), ("Is the YT008 filler acrylic?", "The source does not identify a specific material. Request confirmation for the selected reference before ordering.")],
        "quote": "quote.html?product=Bingsu%20Beads%20and%20Slime%20Fillers",
    },
    "guide-decoden-supplies.html": {
        "file": "decoden-buyer-body.html",
        "answer": "Build a decoden shortlist around the usable case area, actual component dimensions and reverse-side shape. Compare catalog photographs by SKU, request backing details and test the selected decoration with your case and adhesive. Use an approved layout to calculate quantities, then confirm pack counts, MOQ and samples in the quotation.",
        "faq": [("Does a charm photograph establish a flat backing?", "No. Request a reverse-side photograph and the relevant thickness or dimensions for each selected SKU."), ("How many decorations does one phone case need?", "Count each SKU in your actual trial layout. The usable case area, camera clearance and selected component sizes determine the quantity."), ("Does a 100-piece bag mean the MOQ is 100 pieces?", "A reference pack count and minimum order are different facts. Confirm the MOQ and available assortment for each selected SKU in the quotation."), ("Can I choose an adhesive from the decoration photo?", "The photo does not establish adhesive compatibility. Follow the adhesive supplier's instructions and trial the selected decoration, case surface and any base material together.")],
        "quote": "quote.html?product=Decoden%20Resin%20Charms",
    },
    "guide-clay-slices-vs-resin-charms-slime.html": {
        "file": "clay-resin-buyer-body.html",
        "answer": "Compare clay slices and resin decorations by the exact SKU, listed dimensions, pack unit and intended role in your design. Small slices can repeat a motif; a larger piece can act as a focal. Both require a sample check in your actual slime formula. Pack weight does not establish piece count or a fixed dose.",
        "faq": [("Are fake sprinkles edible?", "No. The references in this guide are decorative, non-edible craft components. Assess the requirements of the intended finished product and market."), ("How much decoration should I add per jar?", "Determine the amount through a measured trial with your actual base, jar and selected components. This guide does not prescribe a universal dose."), ("Does a 500 g clay pack contain a fixed number of slices?", "Weight alone does not establish piece count. Count and weigh a representative approved sample if your kit needs a counted quantity."), ("Can a short soak prove color stability?", "An early check does not establish long-term performance. Test the selected sample in the actual formula and intended storage conditions over the period relevant to your product.")],
        "quote": "quote.html?product=Polymer%20Clay%20Slices%20and%20Resin%20Decorations",
        "description": "Compare clay slices and resin decorations for slime using actual SKU photographs, listed sizes, pack units and a measured sample checklist.",
    },
}

def apply_content(page, cfg):
    path = ROOT / page
    s = path.read_text()
    main = re.search(r'<main\b[^>]*>(.*?)</main>', s, re.S)
    old = main[1]
    hero = re.search(r'<section\b.*?</section>', old, re.S)[0]
    figure = re.search(r'<figure\b.*?</figure>', old, re.S)[0]
    # Keep the existing related-guide navigation, not superseded buyer prose.
    related = old.rfind('<section', 0, old.find('Keep Reading'))
    tail = old[related:] if related >= 0 else ''
    faq = '<section class="section section-soft"><div class="container guide-body"><h2>Questions before you order</h2><div class="faq-list">' + ''.join(f'<details><summary>{esc(q)}</summary><p>{esc(a)}</p></details>' for q,a in cfg['faq']) + '</div></div></section>'
    core = (ROOT / 'scripts/data' / cfg['file']).read_text()
    body = hero + '<section class="section" style="padding-top:26px"><div class="container guide-body"><div class="answer-box"><b>Short answer:</b> ' + esc(cfg['answer']) + '</div>' + figure + core + f'<p><a class="btn btn-primary" href="{esc(cfg["quote"])}">Request a quotation for your selected components →</a></p></div></section>' + faq + tail
    s = s[:main.start(1)] + body + s[main.end(1):]
    def schema(m):
        data = json.loads(m[1])
        if data.get('@type') == 'FAQPage':
            data['mainEntity'] = [{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in cfg['faq']]
        if data.get('@type') == 'Article' and cfg.get('description'):
            data['description'] = cfg['description']
        return '<script type="application/ld+json">' + json.dumps(data,ensure_ascii=False) + '</script>'
    s = re.sub(r'<script type="application/ld\+json">(.*?)</script>', schema, s, flags=re.S)
    if cfg.get('description'):
        s = re.sub(r'(<meta (?:name="description"|property="og:description"|name="twitter:description") content=")[^"]*', lambda m:m[1]+esc(cfg['description']), s)
    path.write_text(s)

def apply_all():
    for page,cfg in CONTENT.items():
        apply_content(page,cfg)
    for page in GUIDES:
        apply(page)

if __name__ == '__main__':
    apply_all()
    print('Updated four guide photo sections with catalog facts and source photographs.')
