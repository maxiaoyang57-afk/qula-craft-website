# Inquiry-only product pages

On 2026-11-03 the owner confirmed that the reported products have no real public
quotation and should be handled by inquiry. Product rich-result eligibility must
not be obtained by inventing prices, ratings or reviews.

Based on main `3b4135c5920349546d8cf721a01dc64506bc7412`, 861 of 970 PDPs
have Product markup without offers, review or aggregateRating. Remove that
ineligible Product block only. Keep their visible facts, images, inquiry URLs,
metadata, canonical URLs, robots directives and BreadcrumbList byte-for-byte.
859 of these pages are public; two archived references remain excluded from the
sitemap. Update lastmod only for the 859 changed public URLs. The other 109
pages' existing pricing and Product blocks are outside this targeted change.
No source commercial data, categories, images, analytics or inquiry destinations change.
Generic header/footer inquiry links identify the current product from its explicit
PDP inquiry CTA, so SKU/image/category context no longer depends on Product markup.
Existing mobile integration checks caught this dependency and cover the fix.

The generator uses the same eligibility decision, and SEO checks reject a new
inquiry-only Product even when nested. Existing product identity, packing and
image-maintenance checks use visible content/BreadcrumbList for inquiry pages.
The owner’s screenshot reports 38 invalid items as of November 1; 861 is a
current source-code count, not the GSC count or an indexing total.

After release, GSC must recrawl before the report can change. Removal means no
Product rich-result claim for these pages; it does not turn them into valid
Product rich results or guarantee ordinary indexing/ranking improvements.

Concurrent batch 37 PR #172 must integrate this template and run the same schema
cleanup on its 20 new inquiry pages before release. The SEO gate catches stale
generated Product markup; do not bypass it or discard either branch’s products.
Run `python scripts/inquiry_schema.py` to inspect, then use `--write --date YYYY-MM-DD`
with the actual modification date to apply only the needed cleanup and dates.

Local validation: nine focused Python regressions, 31 existing Node regressions,
full PDP/SEO gates, 13-SKU preservation, inquiry/email/attachments/lead guards,
catalog summary, protected products, IndexNow and basket checks passed.
All 861 changed HTML files compare exactly with the baseline after removing only
the ineligible Product script. Existing priced pages and all source/data/image
files are unchanged. Remote CI, Preview and production acceptance are separate.
