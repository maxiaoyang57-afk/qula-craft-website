# QULA SEO priority follow-up — 2026-09-17

Target: `maxiaoyang57-afk/qula-craft-website` only.
Baseline: `02e1fdbe4c4b563fbccd52b4f0f3ff041df993d5` (latest main at start).
Branch: `pro/qula-seo-priority-20260917`. Preview only; production requires explicit PR approval.

## Implemented

- Nine category ItemLists now contain ordered ListItem name/URL/image entries linking to all 218 existing products, without nested Product declarations. Product cards are byte-for-byte unchanged.
- The three stored product-addition scripts share `catalog_schema.py` so future reruns use the same representation. SEO build checks reject nested category Product declarations and catalog mismatches.
- Resin Charms and Slime Charms gain distinct buyer-oriented sourcing sections and contextual links to existing products/guides. No new price, MOQ, certification, lead-time or compatibility promises.
- Canonical redirects explicitly use 301. Apex `/index.html` goes straight to the www root; other `/index.html` requests go to their own host root so Preview stays on Preview. Existing apex-to-www rule is retained with an explicit status code; .html routes, build command and security headers are unchanged.
- Sitemap lastmod updated only for the nine changed category pages. No pages or images added/removed.

## Corrections to the preceding audit

- Main already contained an apex-to-www permanent redirect. The audit fetch returned 200, but that alone does not establish whether the origin ignored the rule or a fetch layer followed it. Confirm raw Location/status after deployment from a normal client; do not claim that changing 308 to 301 solves deployment configuration.
- RW22372 is intentionally quote-only: source MOQ is 1 bag, remaining usable source prices are per-piece tiers. Do not invent a bag price or restore a misleading Offer. Product semantic markup without an Offer is not, by itself, a crawl/indexing error; Google rich-result eligibility is a separate matter.
- Fresh URL Inspection in this run reported RW22372 as `Submitted and indexed`, with last crawl 2026-08-10. This is not evidence that this task caused new indexing.

## Google-side status — NOT submitted by this change

GSC Wizard offers URL Inspection and IndexNow but exposes no Google Sitemap submit or Google request-indexing operation in this session. Plugin discovery found no additional suitable submission capability. IndexNow does not submit to Google. Updating GSC Wizard metadata or running Inspection is not a submission.

GSC Sitemap read: lastSubmitted 2026-08-07, lastDownloaded 2026-08-27, 220 submitted web URLs, zero errors/warnings. Live/local Sitemap contains 255 URLs. These differing totals alone do not establish a Sitemap failure; Google's processing can lag.

After the approved change reaches production:

1. Open Search Console for `sc-domain:qulacrafts.com`, Sitemaps; submit `https://www.qulacrafts.com/sitemap.xml` and record the submission response.
2. Inspect the priority URLs below, run the live URL test, then use **Request indexing** as quota permits. Record each response; submission is not guaranteed indexing.
3. Re-read Sitemap submission/download dates and URL Inspection status in the next check. Do not repeatedly submit unchanged URLs or treat API `indexed: 0` Sitemap statistics as the site's true index count.

Priority URLs freshly inspected (all INDEXING_ALLOWED; seven Crawled-currently-not-indexed):

- https://www.qulacrafts.com/resin-charms.html
- https://www.qulacrafts.com/slime-charms.html
- https://www.qulacrafts.com/polymer-clay-sprinkles.html
- https://www.qulacrafts.com/acrylic-beads.html
- https://www.qulacrafts.com/guide-polymer-clay-sprinkles-bulk.html
- https://www.qulacrafts.com/guide-clay-slices-vs-resin-charms-slime.html
- https://www.qulacrafts.com/guide-slime-business-supply-checklist.html

Already indexed in the fresh check: https://www.qulacrafts.com/p-rw22372.html

## Validation

Passed locally:

- `node scripts/check-seo.mjs` — 255 indexable pages
- `python3 scripts/gates_full.py` — 257 HTML pages, 218 PDPs, links/assets/schema
- `node scripts/check-required-products.mjs`
- `node scripts/check-inquiry-email.mjs` — existing four forms and recipients preserved
- `node scripts/tests/check-inquiry-basket-sync.mjs`
- `python3 -m unittest discover -s scripts/tests -p test_catalog_schema.py`
- `git diff --check`
- Baseline comparison: all 218 product-card article blocks identical; all PDP/data/assets and four form pages untouched

PR #18 (CSP Report-Only) is separate and untouched. No main merge, production deploy, credentials, environment variables or customer messages are part of this change.

References:

- https://developers.google.com/search/docs/appearance/structured-data/product-snippet
- https://vercel.com/docs/project-configuration/vercel-json#redirects
