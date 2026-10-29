"""Build faithful display derivatives; never overwrite source images or product data.

Requires Pillow with WebP support. Run from any directory. The manifest maps each
unchanged source URL to width-descriptor candidates for HTML srcset integration.
"""

from __future__ import annotations

import hashlib
import json
from html.parser import HTMLParser
from pathlib import Path

from PIL import Image, ImageOps


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "assets/images/responsive-20261029"
PAGES = (
    "index.html", "products.html", "polymer-clay-sprinkles.html",
    "resin-charms.html", "glitter-sequins-fillers.html", "slime-charms.html",
    "pvc-plastic-charms.html", "acrylic-beads.html", "beads-for-pens.html",
    "keychain.html", "jewelry-accessories.html",
)


class ImageSources(HTMLParser):
    def __init__(self):
        super().__init__()
        self.sources = []

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        sources = [values.get("src", "")] if tag == "img" else (
            [candidate.strip().split()[0] for candidate in values.get("srcset", "").split(",")
             if candidate.strip()] if tag == "source" else [])
        for source in sources:
            source = source.split("?", 1)[0].lstrip("/")
            if (source.startswith("assets/images/")
                    and not source.startswith("assets/images/responsive-20261029/")):
                self.sources.append(source)


def main():
    usage = {}
    for page in PAGES:
        parser = ImageSources()
        parser.feed((ROOT / page).read_text(encoding="utf-8"))
        for source in parser.sources:
            usage.setdefault(source, []).append(page)

    # The homepage's presentation imagery and the largest category images give
    # the immediate mobile benefit, without rebuilding thousands of PDP assets.
    selected = {
        source: pages for source, pages in usage.items()
        if "index.html" in pages or (ROOT / source).stat().st_size >= 200_000
    }
    selected["assets/images/whatsapp-3d.png"] = ["shared CSS"]
    # Keep the original mobile crop discoverable after its <source> receives a
    # responsive srcset. Generated derivative URLs are never treated as masters.
    selected["assets/images/flatlay-craft-range-hero-mobile.webp"] = ["index.html"]
    OUTPUT.mkdir(parents=True, exist_ok=True)
    records = []
    for source, pages in sorted(selected.items()):
        source_path = ROOT / source
        raw = source_path.read_bytes()
        sha = hashlib.sha256(raw).hexdigest()
        with Image.open(source_path) as original:
            image = ImageOps.exif_transpose(original)
            width, height = image.size
            is_icon = source.endswith("whatsapp-3d.png")
            is_product = "/pdp/" in source or "/catalog/" in source
            desired = (128, 256) if is_icon else (360, 640) if is_product else (360, 640, 960)
            if source.endswith("flatlay-craft-range-hero.webp"):
                desired += (1280,)
            widths = sorted({min(width, candidate) for candidate in desired})
            stem = source_path.stem[:82] + "-" + hashlib.sha256(source.encode()).hexdigest()[:8]
            variants = []
            retain_original_candidate = False
            for target_width in widths:
                target_height = max(1, round(height * target_width / width))
                resized = image.resize((target_width, target_height), Image.Resampling.LANCZOS)
                output = OUTPUT / f"{stem}-{target_width}w.webp"
                resized.save(output, "WEBP", quality=88, method=6,
                             lossless=is_icon, exact=True, alpha_quality=100,
                             icc_profile=original.info.get("icc_profile", b""))
                with Image.open(output) as check:
                    check.load()
                    assert check.size == (target_width, target_height)
                if output.stat().st_size >= len(raw):
                    assert output.resolve().parent == OUTPUT.resolve()
                    output.unlink()
                    retain_original_candidate = True
                    continue
                variants.append({"url": output.relative_to(ROOT).as_posix(),
                                 "width": target_width, "height": target_height,
                                 "bytes": output.stat().st_size})
            if retain_original_candidate:
                variants.append({"url": source, "width": width, "height": height,
                                 "bytes": len(raw)})
            variants.sort(key=lambda item: item["width"])
            records.append({"source": source, "sourceBytes": len(raw),
                            "sourceSha256": sha, "sourceWidth": width,
                            "sourceHeight": height, "pages": sorted(set(pages)),
                            "variants": variants})
    manifest = {"version": "20261029", "method": "Lanczos resize, WebP quality 88; icon lossless",
                "originalFilesPreserved": True, "images": records}
    (ROOT / "docs/responsive-image-manifest-20261029.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"sources": len(records),
                      "sourceBytes": sum(record["sourceBytes"] for record in records),
                      "variants": sum(len(record["variants"]) for record in records),
                      "derivativeBytes": sum(v["bytes"] for record in records for v in record["variants"]),
                      "640OrNearestBytes": sum(min(record["variants"], key=lambda v: abs(v["width"]-640))["bytes"]
                                               for record in records)}))


if __name__ == "__main__":
    main()
