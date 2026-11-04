"""QULA's inquiry-only catalog does not publish Product offers or rich results.

Keep the visible product facts and BreadcrumbList; never invent an offer/review.
"""
import json
import re

JSONLD = re.compile(r'<script type="application/ld\+json">(.*?)</script>\n?', re.S)
INQUIRY_COPY = re.compile(r'<b>(?:Quoted by pack and quantity|Wholesale pricing by quotation|Packaging &amp; MOQ)</b>')


def pdp_schemas(product, breadcrumb):
    # Old imported offers or review fields do not override the site's policy.
    return [breadcrumb]


def remove_inquiry_product_schema(page):
    def replace(match):
        data = json.loads(match.group(1))
        if data.get("@type") == "Product":
            if not INQUIRY_COPY.search(page):
                raise ValueError("Unqualified Product without the expected inquiry-only copy")
            return ""
        return match.group(0)
    return JSONLD.sub(replace, page)


if __name__ == "__main__":
    import argparse
    import datetime
    from pathlib import Path

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="Apply the reviewed cleanup; default is read-only")
    parser.add_argument("--date", type=datetime.date.fromisoformat, help="Actual modification date, required with --write")
    args = parser.parse_args()
    if args.write and not args.date:
        parser.error("--write requires --date YYYY-MM-DD")
    root = Path(__file__).resolve().parents[1]
    changes = {}
    for path in sorted(root.glob("p-*.html")):
        old = path.read_text(encoding="utf-8")
        new = remove_inquiry_product_schema(old)
        if old != new:
            changes[path] = new
    sitemap_path = root / "sitemap.xml"
    sitemap = sitemap_path.read_text(encoding="utf-8")
    for path, page in changes.items():
        pattern = r'(<loc>https://www\.qulacrafts\.com/' + re.escape(path.name) + r'</loc>\s*<lastmod>)[^<]+(</lastmod>)'
        sitemap, count = re.subn(pattern, lambda m: m[1] + str(args.date) + m[2], sitemap)
        if count != (0 if 'content="noindex,follow"' in page else 1):
            raise ValueError(f"Unexpected sitemap coverage: {path.name}")
    if args.write:
        for path, page in changes.items():
            path.write_text(page, encoding="utf-8")
        if changes:
            sitemap_path.write_text(sitemap, encoding="utf-8")
    print(json.dumps({"mode": "write" if args.write else "check", "changed_pages": len(changes)}))
