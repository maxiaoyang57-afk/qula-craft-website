# Category purchasing-copy review — 2026-10-12

## Result

Sixteen FAQ answers across Acrylic Beads, Polymer Clay Slices, Resin Charms and Slime Charms now use the selected SKU, approved sample and quotation as the basis for purchasing decisions. Visible answers and FAQ structured data are updated together.

| Page | Revision |
| --- | --- |
| Acrylic Beads | Confirm hole diameter/direction and no-hole fillers per SKU; replace generic 500g packing, guaranteed alphabet stock and blanket children's-kit/report availability with project-specific review. |
| Polymer Clay Slices | Confirm thickness, color performance, mix-ratio basis and dispatch date; remove unverified every-batch testing, fixed tolerance and general stock/custom shipping promises. |
| Resin Charms | Confirm backing/hole availability, dimensions and agreed tolerance; review theme assortments per order. |
| Slime Charms | Confirm bag units and included mix; remove unsupported buyer percentages and a guaranteed single carton/shipment. |

The four pages' Organization descriptions retain the existing identity and audit information while clarifying that document availability and scope are confirmed for the selected SKU and market. A historical supplier report is not treated as evidence that every catalog product has the same report.

## Scope and validation

- Based on latest remote main `73e8679` (PR #58); today's 15 additions and CDK080 refresh are preserved.
- SKU data, product measurements, prices, images, URLs, titles, meta descriptions and H1s remain unchanged.
- Only the four substantially edited category pages receive sitemap date updates.
- Required inquiry-email/attachment/DOM/basket/lead safeguards, protected-product checks, SEO checks (292 indexable pages) and IndexNow configuration checks passed.
- Preview-specific desktop/mobile rendering, FAQ/schema equality and selected-SKU quote prefill results are recorded in the associated PR.

This task does not merge the separate GA4 draft PR #54 or infer children's-product suitability from category membership.

## Post-release follow-up

The user confirmed that phone display is normal and inquiry emails are received. These are user-observed acceptance results for the previously released HAIBU #95 and QULA #59, rather than a new automated delivery test.

This follow-up starts from remote main `e47436d` and closes the two remaining category-copy scope gaps:

- Polymer Clay: replace application-wide 1–4 mm / 2–8 mm dimensions with SKU-specific confirmation. YX626's imported `Size: 5mm` is labelled as a listing reference, not a measured tolerance or a size shared by the entire assortment.
- Slime: remove the category-wide 30g–1000g range from the introduction, qualify assortment contents and packaging, and identify pack-reference examples by SKU. The imported titles list SLM10094 at 30g, SLM10093 and SLM10012 at 500g, and SLM10129 at 1000g. Current packing and MOQ are separate quotation confirmations.

Product source data, images, prices, product pages, URLs, titles, metadata, H1s, FAQs and their structured data remain unchanged. The two page sitemap dates already equal 2026-10-12. This is the single follow-up PR for these two scope gaps; the separate GA4 draft #54 remains outside this task.
