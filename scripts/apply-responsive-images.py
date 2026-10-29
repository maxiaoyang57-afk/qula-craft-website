"""Wire reviewed display derivatives while preserving source URLs and product data."""

import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = "20261029-responsive-images"
PAGES = (
    "index.html", "products.html", "polymer-clay-sprinkles.html",
    "resin-charms.html", "glitter-sequins-fillers.html", "slime-charms.html",
    "pvc-plastic-charms.html", "acrylic-beads.html", "beads-for-pens.html",
    "keychain.html", "jewelry-accessories.html",
)


def attribute(tag, name):
    match = re.search(r'\s+' + name + r'\s*=\s*([\"\x27])(.*?)\1', tag, re.I | re.S)
    return html.unescape(match.group(2)) if match else None


def set_attribute(tag, name, value):
    encoded = html.escape(value, quote=True)
    pattern = r'\s+' + name + r'\s*=\s*([\"\x27])(.*?)\1'
    if re.search(pattern, tag, re.I | re.S):
        return re.sub(pattern, lambda _: f' {name}="{encoded}"', tag, flags=re.I | re.S)
    return re.sub(r'\s*/?>$', lambda end: f' {name}="{encoded}"' + end.group(), tag)


def main():
    manifest = json.loads((ROOT / "docs/responsive-image-manifest-20261029.json").read_text(encoding="utf-8"))
    images = {record["source"]: record for record in manifest["images"]}
    counts = {}
    for name in PAGES:
        path = ROOT / name
        with path.open(encoding="utf-8", newline="") as source:
            text = source.read()
        count = 0

        def wire(match):
            nonlocal count
            tag = match.group()
            is_source = bool(re.match(r'<source\b', tag, re.I))
            url = attribute(tag, "srcset" if is_source else "src")
            if not url:
                return tag
            # Existing picture sources select a different crop, so optimize that
            # same source independently and retain the original media condition.
            source = url.split(",", 1)[0].strip().split(" ", 1)[0].split("?", 1)[0].lstrip("/")
            if source not in images:
                return tag
            record = images[source]
            candidates = ", ".join(f'{v["url"]} {v["width"]}w' for v in record["variants"])
            if "hero" in source:
                sizes = "100vw"
            elif name == "index.html" and "/category-covers-v2/" in source:
                sizes = "(max-width: 720px) calc((100vw - 56px) / 2), (max-width: 1100px) calc((100vw - 80px) / 2), 400px"
            else:
                sizes = "(max-width: 720px) calc(100vw - 48px), (max-width: 1100px) calc((100vw - 80px) / 2), 400px"
            tag = set_attribute(set_attribute(tag, "srcset", candidates), "sizes", sizes)
            if not is_source:
                # Reserve the real source aspect ratio before lazy loading.
                tag = set_attribute(set_attribute(tag, "width", str(record["sourceWidth"])),
                                    "height", str(record["sourceHeight"]))
            count += 1
            return tag

        updated = re.sub(r'<(?:img|source)\b[^>]*>', wire, text, flags=re.I)
        if updated != text:
            with path.open("w", encoding="utf-8", newline="") as output:
                output.write(updated)
        counts[name] = count

    icon = images["assets/images/whatsapp-3d.png"]
    candidates = ", ".join(f'url("../{v["url"].removeprefix("assets/")}") {i + 1}x' for i, v in enumerate(icon["variants"]))
    css_path = ROOT / "assets/css/style.css"
    with css_path.open(encoding="utf-8", newline="") as source:
        css = source.read()
    # Keep the original PNG declaration as a fallback for older engines.
    if "responsive-20261029/whatsapp-3d" not in css:
        declaration = 'background: url("../images/whatsapp-3d.png") no-repeat center/contain;'
        assert css.count(declaration) == 2
        css = css.replace(declaration, declaration + "\n  background-image: image-set(" + candidates + ");")
        with css_path.open("w", encoding="utf-8", newline="") as output:
            output.write(css)

    versioned = 0
    for path in ROOT.glob("*.html"):
        with path.open(encoding="utf-8", newline="") as source:
            text = source.read()
        updated = re.sub(r'(assets/css/style\.css\?v=)[A-Za-z0-9_-]+', lambda m: m.group(1) + VERSION, text)
        if updated != text:
            with path.open("w", encoding="utf-8", newline="") as output:
                output.write(updated)
            versioned += 1
    print(json.dumps({"responsiveElements": counts, "sharedStyleCacheUpdates": versioned}))


if __name__ == "__main__":
    main()
