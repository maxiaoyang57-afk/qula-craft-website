# QULA SEO optimization — 2026-10-01

Baseline: origin/main `acf34759f40e6e06631e58e2e3c4ec78e2d670b1` (merged PR #50). Prepared on an isolated branch. Production awaits review of this Preview.

## Findings and decisions

- Latest source workbook `QULA_2026-09-30_Product_Listings.xlsx` (formerly `9.30.xlsx`, current Library version read on 2026-10-01) contains no prices. YA893, YA690, YJ145, YA449, YA425, YA417 and YA382 remain quotation-only. No offers, inventory schema or ratings were fabricated or removed.
- These seven products are already in the acrylic category and sitemap. Additional entry points address buyer navigation, not a proven Google indexing bottleneck.
- The existing pen-bead guide incorrectly generalized resin material, one-bag minimums and fixed stock counts to the buying journey. Replace those with per-SKU checks, a seven-product comparison and explicit separation of pack size from MOQ.
- Preserve the guide's current CTR title and description, URL, original publication date, images, navigation and inquiry flow. Synchronize visible FAQs, FAQ markup, source content and modification date.
- Link each new product to the buying guide and link the guide to the seven products. Add a category-page guide entry below the product grid. Preserve these PDP links in the existing generator and copy records.
- Keep the existing brand name `Qula Craft`, legal identity and verified sameAs URLs. Add the real short name `QULA` and domain `qulacrafts.com` as homepage WebSite alternatives, with a stable website ID. This expresses site-name preference; it is not a guaranteed fix for Google query autocorrection.
- The linked official YouTube channel shows `Qula Craft` and links to `qulacrafts.com`. No change needed there. No external profile edits made; Alibaba's full profile remains outside this verification.

## Authenticated GSC work on 2026-10-01

- Polymer, resin and slime category pages remain "Crawled - currently not indexed". Their last crawls were respectively 2026-09-30 21:04:52, 2026-09-30 21:28:34 and 2026-10-01 01:19:12, as displayed by GSC. Fetch succeeded, crawling/indexing is allowed, and declared and Google-selected canonicals agree. No redundant individual requests submitted for these recently crawled pages.
- The polymer-clay buying guide remains in the same exclusion state, last crawled 2026-09-25 15:24:32. A new indexing request succeeded today.
- Inspected all seven new SKUs individually. Each reports "URL is unknown to Google", with no recorded crawl. YA893's individual indexing request succeeded and was added to the priority crawl queue. These are request receipts, not evidence of indexing.
- Resubmitted the existing `https://www.qulacrafts.com/sitemap.xml`. GSC confirmed success and immediately changed its discovered-page count from 268 to 275, with submission and last-read dates of 2026-10-01. This covers all seven new product URLs; the remaining six were not individually resubmitted.
- Product snippets report still shows 38 invalid, 0 valid; last report update 2026-09-30. Existing validation status is "Started", not passed. Did not restart validation.

## Validation

- All four Vercel build gates pass: inquiry email, required products, SEO and IndexNow.
- Full local site gate passes: 277 HTML pages, 238 PDPs, 275 sitemap URLs, local links and assets.
- All 238 product-page JSON-LD objects compare exactly with origin/main; product prices, schema, imagery and catalog order unchanged.
- Python syntax and git whitespace checks pass.
- Sitemap lastmod changes only for the ten changed public pages.
- PR #51 Vercel Preview deployed successfully. Inspected the guide's seven-row comparison table at desktop width, confirmed no document overflow, and followed the YA425 link and verified its guide backlink. No real mobile-viewport test claimed.

## Remaining

- Monitor Google processing and the existing product-snippet validation. New requests and sitemap discovery do not guarantee indexing or ranking.
- Product rich-result eligibility remains data-dependent for quotation-only products. Do not claim the absence of offers prevents ordinary indexing.
- Preview is ready for review. Production requires approval of this specific PR/Preview; this branch has not been merged.
