# SC048 product description and logo customization

- Repository: `maxiaoyang57-afk/qula-craft-website`
- Production source checked before work: `main` at `b0ccc2feb07b681ee7657343d7de3d8aa6712a69`
- Working branch: `pro/qula-sc048-customization-20260910`
- Product route: `/p-sc048.html`
- User approved the pink/mint design mockup and requested implementation on 2026-09-10.

The page now includes a product introduction, custom-order/logo badges, two specification rows, a logo-placement illustration, and a dedicated custom-logo quotation link. The new link uses the existing quote page and carries SC048, its original product image and the custom-logo request in its query parameters. Standard MOQ remains 100 pieces; custom quantities, prices and lead times are confirmed separately.

The illustration was generated specifically for this approved layout. Its caption identifies the logo placement as illustrative and the pouch/ring as styling props. It is not evidence of a completed branded order. The optimized WebP is 1200 × 900 pixels, 145,716 bytes.

All page styles are scoped under `.sc048-page` in a separate stylesheet. Original title, product gallery, price block, existing quote/WhatsApp/basket controls, four related-product cards, navigation and footer are preserved. The product-specific note replaces the generic decorative-craft/test-report sentence. Meta and Product descriptions now reflect the displayed cloth and customization services. No product records, other product pages, category cards, inquiry forms, receiving email, global assets or Vercel configuration were changed.

`scripts/sc048_customization.py` is the content source for these additions. `scripts/gen_pdp.py` invokes it only for asset key `sc048` so a later PDP regeneration preserves the customization content. This task applied it to SC048 only; the full generator was not run. For later content revisions, edit this helper and apply it to a clean generated SC048 page; already-customized pages are intentionally returned unchanged to prevent duplicate sections.

Validation completed:

- Existing Vercel build checks: four inquiry forms and 246 email links still use `sales@qulacrafts.com`; AJAX safeguard and protected-product checks pass.
- Repository page gates: 243 HTML pages, 204 PDPs, 204 catalog records and 241 sitemap entries; resource/link checks and JSON-LD parsing pass.
- SC048-specific source checks: preserved original elements, exactly one new section, quotation parameters, valid image references/dimensions, CSS scope, unique IDs, Python syntax and repeat-safe application.
- Browser interaction and responsive rendering were not exercised. The stylesheet contains a mobile layout breakpoint; use the PR's Vercel Preview for visual acceptance.

Delivery is through the PR and its Vercel Preview. Production main has not been merged or deployed by this change. Both accounts should use this branch/PR, and fetch the latest main before any later work or release.
