"""Apply batch-specific SEO descriptions after the shared PDP generator."""
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OLD = "Wholesale Christmas Resin Cabochons for Hair Clips,. Wholesale Resin Charms. MOQ To be discussed. From Yiwu; batch reports on request."
DESCRIPTIONS = {
    "RW26774": "Wholesale Christmas resin cabochons for hair clips, keychains, scrapbooking and seasonal decoration. Reference RW26774 for bulk inquiries.",
    "RW26775": "Wholesale Christmas resin cabochons for hair clips, keychains, scrapbooks and gift packaging. Reference RW26775 for bulk inquiries.",
    "RW26776": "Wholesale Christmas resin cabochons for hair clips, keychains, scrapbooks and phone decoration. Reference RW26776 for bulk inquiries.",
    "RW26777": "Wholesale Christmas resin cabochons for hair clips, keychains, scrapbooks and phone cases. Reference RW26777 for bulk inquiries.",
}

for sku, description in DESCRIPTIONS.items():
    path = ROOT / f"p-{sku.lower()}.html"
    content = path.read_text(encoding="utf-8")
    count = content.count(OLD)
    if count != 3:
        raise RuntimeError(f"{sku}: expected three generated descriptions, found {count}")
    path.write_text(content.replace(OLD, description), encoding="utf-8")
    print(f"{sku}: replaced {count} descriptions")
