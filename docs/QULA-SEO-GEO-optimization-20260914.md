# QULA SEO / GEO Optimization — 2026-09-14

Target: `https://www.qulacrafts.com/`  
Repository: `maxiaoyang57-afk/qula-craft-website`  
Baseline: `38ce32c` (`main`)  
Mode: Preview only

## Verified baseline

- 257 HTML pages on disk
- 255 indexable pages represented in `sitemap.xml`
- 218 product detail pages represented in the catalog and `llms-full.txt`
- Existing JSON-LD parses successfully
- Existing inquiry protection passes: four forms and 260 email links use `sales@qulacrafts.com`
- Both `qulacrafts.com` and `www.qulacrafts.com` returned HTTP 200 before this change, while every canonical and Sitemap URL used `www`

## Changes in this round

1. Enforce one crawlable host by redirecting non-`www` requests permanently to the existing `www` canonical host.
2. Add a build-blocking SEO test for unique metadata and canonicals, valid JSON-LD, complete image attributes, Sitemap coverage and conflicting commercial units.
3. Suppress unverified prices on 34 product pages where the displayed price unit conflicts with the MOQ unit. The visible page, metadata, Product JSON-LD and `llms-full.txt` now agree.
4. Add the same price/MOQ guard to `scripts/gen_pdp.py` so a future regeneration does not restore the conflict.
5. Shorten one overlong core-page title, six overlong PDP titles and 20 descriptions without adding unsupported claims.
6. Replace three unverified named buyer testimonials with links to verifiable company, audit and third-party supplier records.
7. Refresh Sitemap `lastmod` values from real file history and make image Sitemap titles stop at word boundaries.

## Measured result after changes

- 255/255 indexable pages have a unique title, description and canonical
- 0 titles over 65 characters
- 0 descriptions outside the 80–160 character range on indexable pages
- 0 invalid JSON-LD blocks
- 0 images missing an `alt` attribute or numeric width/height
- 0 visible price/MOQ unit-family conflicts
- 0 missing or extra indexable URLs in the Sitemap
- Existing catalog, PDP, internal-link and inquiry-email gates pass

## Requires user access or verified source data

- Google Search Console ownership verification, Sitemap submission and Coverage inspection
- A real GA4 Measurement ID to replace `G-XXXXXXXXXX`
- Real customer-review text and authorization if named testimonials are desired
- Confirmed sales units for the 34 suppressed-price products before exact prices can be restored

Public search checks cannot substitute for Search Console's exact indexed/not-indexed reports. No ranking, indexing date or AI citation is guaranteed.
