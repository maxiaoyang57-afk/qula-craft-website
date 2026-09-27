# QULA SEO follow-up — 2026-09-27

## Production release

PR #45 was explicitly approved for release and merged as `57fd869cdfbe0e14ec18cd56b7439d09ccc8f91c`.
GitHub's Vercel production check succeeded. The live homepage, RX399, YX4075,
MSB401, RW26746, SC048, sitemap.xml and robots.txt were fetched and matched
that commit byte for byte. The Vercel connector could not retrieve deployment
details, so the evidence is the GitHub deployment check plus public content.

## Follow-up scope (preview)

- Remove inferred `availability: InStock` and `offerCount` from 112 AggregateOffer
  objects. Imported price-tier rows establish neither current inventory nor a
  count of independently published offers. Preserve every published price,
  currency, Product field and inquiry route. Update both PDP scripts and the SEO gate.
- Replace 49 guide-card descriptions across 27 pages with complete text relevant
  to their actual destination; remove clipped words and the unsupported 70/30 teaser.
- In the polymer clay bulk guide, clarify bag/pack/kg quotation units, require
  item-specific MOQ and timing confirmation, remove asserted sales/damage norms,
  align visible and structured FAQs, and add a contextual YX4075 product link.
- Update that guide's visible and structured modification date, and sitemap
  lastmod only for the 139 HTML pages changed in this batch.

## Verification

Passed: inquiry-email protection, required-products check, SEO check, IndexNow
configuration check, full site gates, September 20 product-batch test, Python
compilation and git diff --check. 268 indexable URLs and 231 PDPs remain.
Semantic comparison of every Product object against the production baseline
confirmed that the only Product changes are removal of the two unsupported fields.

No price, review, rating or inventory has been invented to make quote-only pages
eligible for rich results. Google Search Console URL inspection and sitemap
submission have not been performed; public search results are not GSC evidence.
This follow-up is a separate preview and requires approval before production.
