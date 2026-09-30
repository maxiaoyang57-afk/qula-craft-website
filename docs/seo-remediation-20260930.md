# SEO remediation — 2026-09-30

Base: `a1cd8e79af83c9f2e444cb9349f8986f4acb0b6d` (remote main, PR #47).

## Changes

- Replace 18 unconditional `In Stock` category badges on the homepage and product hub with `Browse Products`, and remove stock assertions from their catalog headings.
- Replace 128 category-only product descriptions with product-specific summaries derived from the existing source titles and specifications. The curated text lives in `assets/data/pdp-description-details.json`; original import records remain unchanged.
- Show the same factual summary below each affected product H1, and synchronize metadata and Product descriptions through the existing refresh pipeline.
- Preserve the summary in future generated PDPs and add SEO checks against the old generic description and inventory badge patterns.
- Update sitemap lastmod only for the 130 HTML pages changed in this branch. Remove the refresh script's stale, unconditional 2026-09-26 date rewrite.

## Search Console observation and action

Observed in the authenticated `sc-domain:qulacrafts.com` property on 2026-09-30:

- Sitemap `https://www.qulacrafts.com/sitemap.xml`: successful, last read 2026-09-25, 268 discovered pages. No resubmission of the unchanged production sitemap was needed.
- Polymer Clay category: crawled, currently not indexed; last crawl 2026-09-25 15:20:30, smartphone crawler. Fetch successful, crawling and indexing allowed, Google-selected and declared canonical match the page. Indexing request successfully submitted; indexing is not guaranteed.
- Resin category URL inspection returned a temporary GSC error. Do not treat this as a website fetch failure or confirmed indexing result.
- Product snippets report last updated 2026-09-29: 38 invalid items, 0 valid; missing `offers`, `review`, or `aggregateRating`. The report is Google's processed subset, not the number of Product objects in the source.

## Data-dependent work remaining

The current source contains 231 Product objects; 112 have existing offers and 119 do not. This branch changes no offer object, price, availability or review. Products without verified public price/review data remain quotation-based and cannot be claimed eligible for Product rich results. Do not add zero-price offers, invented ratings or inventory to silence validation errors. Recheck rich results after a production release and Google's recrawl; only start validation for issues actually corrected.

## Verification

- `node scripts/check-seo.mjs`: 268 indexable pages pass.
- `node scripts/check-inquiry-email.mjs`, `node scripts/check-required-products.mjs`, `node scripts/check-indexnow.mjs`: pass.
- `python3 scripts/gates_full.py`: 270 HTML files, 231 PDPs, 268 sitemap URLs; local links and assets pass.
- `node scripts/tests/check-inquiry-basket-sync.mjs`, `node scripts/tests/check-20260920-products.mjs`: pass.
- Python compilation and `git diff --check`: pass.
- Semantic comparison against base: every existing offer object unchanged; 128 generic descriptions removed.

Production deployment is pending review of this branch's Preview. PR #48 is independent and is not incorporated here.
