# QULA product batch v3 — 12 October 2026

The re-supplied 10.11(3).xlsx has 37 product records: 16 previously published records and 21 additions. The first 16 source records match the earlier batch manifest and are preserved. The catalog grows from 253 to 274 listings.

User-confirmed correction: use RW5463 for the photo named RW5643.png. Multi-code rows remain grouped listings with their exact supplied SKU strings. The existing single RX042 listing is preserved separately. RW728 keeps the acrylic/plastic material and acrylic category from the specification fields. GY016 remains explicitly glass and is routed to the existing Slime Charms supply category.

Each new listing has three images: the supplied product photo plus two labeled styled illustrations. Eighteen opaque reference photos are JPEGs at quality 85, 72 PPI and sRGB; three transparent reference photos remain PNGs. Image dimensions and aspect ratios are retained, with no enlargement of small originals. Generated images are scaled to at most 1000 px wide and have EXIF/GPS removed. The 63 images total 9,376,196 bytes.

Product details, category cards, search catalog, Product/Breadcrumb/ItemList schema, sitemap and AI catalog are synchronized. Prices, MOQ, unprovided dimensions, hole diameters, lead times and reports are not invented. Standard bag quantities are distinct from MOQ.

New inquiry links carry the actual catalog category, selected photo and complete SKU. The quote runtime accepts the explicit category only when it matches an existing select option, and otherwise retains the old fallback. A Jewelry Findings & Accessories option is added. This corrects RW728's old prefix-based Resin selection and supports YA446/YA447 and the new findings/fillers. Quote runtime cache versions are updated on both loading pages. Delivery addresses, attachments, basket synchronization and accepted-lead behavior are preserved.

Local validation:
- Inquiry/email/attachment/DOM safety/basket/lead/production-host guards pass.
- Protected-product checks, SEO for 313 indexable URLs and IndexNow checks pass.
- gates_full.py passes for 274 PDPs and 315 total HTML pages.
- All 253 existing catalog and PDP records are preserved except required order/index updates.
- Source fields match all 21 added workbook rows; galleries and structured images map to the same products.
- JPEG/PNG dimensions, transparency, sRGB, 72 PPI and EXIF/GPS stripping checked.
- Git whitespace checks pass.

Preview and production acceptance will be recorded below. No inquiry email is submitted by this batch. Mobile physical-device acceptance is not claimed.
