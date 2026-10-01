# QULA SEO optimization — 2026-10-01

Baseline: origin/main `acf34759f40e6e06631e58e2e3c4ec78e2d670b1` (merged PR #50). Prepared on an isolated branch. Production awaits review of this Preview.

## Findings and decisions

- Latest source workbook `QULA_2026-09-30_Product_Listings.xlsx` (formerly `9.30.xlsx`, current Library version read on 2026-10-01) contains no prices. YA893, YA690, YJ145, YA449, YA425, YA417 and YA382 remain quotation-only. No offers, inventory schema or ratings were fabricated or removed.
- These seven products are already in the acrylic category and sitemap. Additional entry points address buyer navigation, not a proven Google indexing bottleneck.
- The existing pen-bead guide incorrectly generalized resin material, one-bag minimums and fixed stock counts to the buying journey. Replace those with per-SKU checks, a seven-product comparison and explicit separation of pack size from MOQ.
- Preserve the guide's current CTR title and description, URL, original publication date, images, navigation and inquiry flow. Synchronize visible FAQs, FAQ markup, source content and modification date.
- Link each new product to the buying guide and link the guide to the seven products. Add a category-page guide entry below the product grid. Preserve these PDP links in the existing generator and copy records.
- Keep the existing brand name `Qula Craft`, legal identity and verified sameAs URLs. Add the real short name `QULA` and domain `qulacrafts.com` as homepage WebSite alternatives, with a stable website ID. This expresses site-name preference; it is not a guaranteed fix for Google query autocorrection.
- Public search returned brand mentions on YouTube and the existing Alibaba store, but full external profile contents could not be verified. No external profile changes made.
- GSC redirected to the signed-out Google account chooser. No new indexing requests or validation completion claims made in this branch.

## Validation

- All four Vercel build gates pass: inquiry email, required products, SEO and IndexNow.
- Full local site gate passes: 277 HTML pages, 238 PDPs, 275 sitemap URLs, local links and assets.
- All 238 product-page JSON-LD objects compare exactly with origin/main; product prices, schema, imagery and catalog order unchanged.
- Python syntax and git whitespace checks pass.
- Sitemap lastmod changes only for the ten changed public pages.

## Remaining

- Sign in to GSC and inspect three core categories, the polymer-clay guide and seven new SKUs. Follow the previous validation request; do not repeatedly submit unchanged pages.
- Product rich-result eligibility remains data-dependent for quotation-only products. Do not claim the absence of offers prevents ordinary indexing.
- Verify the deployed Preview before requesting production approval.
