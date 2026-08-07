# -*- coding: utf-8 -*-
"""Replace selected Qula Craft PDP galleries from an explicit three-image job file.

The job file keeps the only judgement-heavy step—image order—visible and reviewable.
Everything after that is deterministic: backup, WebP conversion, data/schema/gallery
sync, mobile-width fix, and CSV manifest generation.
"""

import argparse
import csv
import json
import re
import shutil
from pathlib import Path

from PIL import Image, ImageOps


BASE_URL = "https://www.qulacrafts.com/"
MOBILE_FIX = """
  <style>
    @media (max-width:640px){
      .detail-grid{grid-template-columns:minmax(0,1fr)}
      .detail-grid>*{min-width:0}
      .detail-grid .spec-table{width:100%;min-width:0;table-layout:fixed}
      .detail-grid .spec-table th{width:34%}
      .detail-grid .spec-table th,.detail-grid .spec-table td{overflow-wrap:anywhere}
    }
  </style>"""
SCHEMA_RE = re.compile(
    r'(<script type="application/ld\+json">)(.*?)(</script>)', re.S
)
GALLERY_RE = re.compile(
    r'<div class="gallery-main">.*?</div>\s*'
    r'(?:<div class="gallery-row">.*?</div>)?',
    re.S,
)
UX_LINK_RE = re.compile(
    r'(<link[^>]+href="assets/css/ux\.css[^"]*"[^>]*>)', re.I
)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Batch-replace selected PDP galleries with ordered three-image sets."
    )
    parser.add_argument("--site", type=Path, required=True)
    parser.add_argument("--job", type=Path, required=True)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate SKU, files, target pages and image count without writing.",
    )
    return parser.parse_args()


def load_job(path):
    job = json.loads(path.read_text(encoding="utf-8"))
    required = ("source_root", "output_root", "backup_root", "items")
    missing = [name for name in required if name not in job]
    if missing:
        raise ValueError(f"Job missing keys: {', '.join(missing)}")
    if not job["items"]:
        raise ValueError("Job contains no items")
    return job


def validate_item(item, entries, source_root, site):
    sku = str(item.get("sku", "")).strip()
    files = item.get("files") or []
    if not sku:
        raise ValueError("Each item needs a SKU")
    if len(files) != 3:
        raise ValueError(f"{sku}: exactly three ordered files are required")
    entry = next((row for row in entries if row.get("sku") == sku), None)
    if not entry:
        raise ValueError(f"{sku}: not found in pdp-data.json")
    sources = [source_root / name for name in files]
    absent = [str(path) for path in sources if not path.is_file()]
    if absent:
        raise FileNotFoundError(f"{sku}: source files missing: {absent}")
    page = site / f"p-{entry['assetKey']}.html"
    if not page.is_file():
        raise FileNotFoundError(f"{sku}: PDP page missing: {page}")
    alts = item.get("alts") or [f"{sku} product image {i}" for i in range(1, 4)]
    if len(alts) != 3:
        raise ValueError(f"{sku}: alts must contain three entries")
    return entry, sources, page, [str(alt).strip() for alt in alts]


def convert_to_square_webp(source, destination):
    destination.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(source) as raw:
        image = ImageOps.exif_transpose(raw).convert("RGBA")
        scale = min(1200 / image.width, 1200 / image.height)
        target_size = (
            max(1, round(image.width * scale)),
            max(1, round(image.height * scale)),
        )
        image = image.resize(target_size, Image.Resampling.LANCZOS)
        canvas = Image.new("RGBA", (1200, 1200), "white")
        left = (1200 - image.width) // 2
        top = (1200 - image.height) // 2
        canvas.alpha_composite(image, (left, top))
        canvas.convert("RGB").save(
            destination, "WEBP", quality=86, method=6, optimize=True
        )


def update_product_schema(html, image_urls):
    changed = False

    def replace(match):
        nonlocal changed
        try:
            payload = json.loads(match.group(2))
        except json.JSONDecodeError:
            return match.group(0)
        if payload.get("@type") != "Product":
            return match.group(0)
        payload["image"] = image_urls
        changed = True
        return (
            match.group(1)
            + json.dumps(payload, ensure_ascii=False, separators=(", ", ": "))
            + match.group(3)
        )

    updated = SCHEMA_RE.sub(replace, html)
    if not changed:
        raise ValueError("Product schema block not found")
    return updated


def update_page(html, sku, rel_images, alts):
    gallery = (
        f'<div class="gallery-main"><img fetchpriority="high" '
        f'src="{rel_images[0]}" alt="{alts[0]}" width="1200" height="1200"></div>'
        '<div class="gallery-row">'
        + "".join(
            f'<img loading="lazy" src="{rel}" alt="{alt}" '
            'width="1200" height="1200">'
            for rel, alt in zip(rel_images, alts)
        )
        + "</div>"
    )
    updated, count = GALLERY_RE.subn(gallery, html, count=1)
    if count != 1:
        raise ValueError(f"{sku}: gallery block not found")
    updated = update_product_schema(
        updated, [BASE_URL + rel for rel in rel_images]
    )
    if "table-layout:fixed" not in updated:
        updated, count = UX_LINK_RE.subn(r"\1" + MOBILE_FIX, updated, count=1)
        if count != 1:
            raise ValueError(f"{sku}: ux.css link not found for mobile fix")
    return updated


def run(site, job_path, dry_run=False):
    site = site.resolve()
    job = load_job(job_path.resolve())
    source_root = Path(job["source_root"]).resolve()
    output_root = Path(job["output_root"]).resolve()
    backup_root = Path(job["backup_root"]).resolve()
    data_path = site / "assets/data/pdp-data.json"
    entries = json.loads(data_path.read_text(encoding="utf-8"))

    planned = [
        (item, *validate_item(item, entries, source_root, site))
        for item in job["items"]
    ]
    if dry_run:
        return [
            {
                "sku": item["sku"],
                "assetKey": entry["assetKey"],
                "files": [str(path) for path in sources],
                "page": str(page),
            }
            for item, entry, sources, page, _alts in planned
        ]

    output_root.mkdir(parents=True, exist_ok=True)
    backup_root.mkdir(parents=True, exist_ok=True)
    manifest_rows = []

    for item, entry, sources, page, alts in planned:
        sku = item["sku"]
        key = entry["assetKey"]
        site_image_dir = site / f"assets/images/pdp/{key}"
        sku_backup = backup_root / sku
        sku_output = output_root / sku
        if sku_backup.exists() or sku_output.exists():
            raise FileExistsError(
                f"{sku}: output or backup folder already exists; use a fresh dated job path"
            )
        sku_backup.mkdir(parents=True)
        sku_output.mkdir(parents=True)
        for old_image in site_image_dir.glob("*.webp"):
            shutil.copy2(old_image, sku_backup / old_image.name)

        rel_images = []
        for index, source in enumerate(sources, 1):
            site_target = site_image_dir / f"{index:02}.webp"
            delivery_target = sku_output / f"{sku}-{index:02}.webp"
            convert_to_square_webp(source, delivery_target)
            shutil.copy2(delivery_target, site_target)
            rel = f"assets/images/pdp/{key}/{index:02}.webp"
            rel_images.append(rel)
            with Image.open(delivery_target) as image:
                manifest_rows.append(
                    {
                        "SKU": sku,
                        "Position": index,
                        "SourceFile": str(source),
                        "OutputFile": str(delivery_target),
                        "OutputWidth": image.width,
                        "OutputHeight": image.height,
                        "OutputBytes": delivery_target.stat().st_size,
                        "Alt": alts[index - 1],
                    }
                )

        entry["imagesLocal"] = rel_images
        page.write_text(
            update_page(page.read_text(encoding="utf-8"), sku, rel_images, alts),
            encoding="utf-8",
        )

    data_path.write_text(
        json.dumps(entries, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    manifest_path = output_root / "image-manifest.csv"
    with manifest_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=manifest_rows[0].keys())
        writer.writeheader()
        writer.writerows(manifest_rows)
    return manifest_rows


def main():
    args = parse_args()
    result = run(args.site, args.job, args.dry_run)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
