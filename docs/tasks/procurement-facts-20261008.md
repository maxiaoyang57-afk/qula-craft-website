# Procurement facts correction — 8 October 2026

Buyers opening imported resin pen-component pages saw `Product Type: Painting`
in both the specification table and Product JSON-LD. The correction uses the
same record's source title and resin material, while retaining the original
Alibaba capture unchanged.

## Changes

- Correct 17 pages in the existing `beads-for-pens` category: CZB26337,
  CZB23106, CZB25840, CZB25847, CZB26022, CZB001890, CZB001023, CZB001070,
  CZB26127, CZB25131, CZB25849, CZB25897, CZB23047, CZB26353, CZB26286,
  CZB26274 and CZB26272. CZB26337 is a resin flatback charm; the other source
  titles identify beads. This does not claim a measured hole or universal fit.
- `public_specs()` supplies the corrected public value to both outputs in
  `gen_pdp.py`. Existing generated pages receive only the two type replacements;
  the entire catalogue is not regenerated.
- Add an Acrylic selection section distinguishing shaped/stringing components,
  confirmed no-hole fillers (YA074/YA129), and cabochons/display props. Preserve
  every existing product card, URL, title and H1. YA425's stated 2.5 mm hole does
  not establish pen fit. YA382 remains a cupcake bead.
- Update Decoden copy and its source dictionary, Article date and FAQ together.
  The historical 19-design assortment no longer describes the entire resin
  catalogue (currently 55 catalogue entries). Packing and MOQ are confirmed by
  SKU; five to seven designs is a selection suggestion, not a guaranteed bag MOQ.
- Set sitemap lastmod to 2026-10-08 only for the 19 changed pages.

## Evidence and boundaries

- The two complete Search Console windows available on 8 October are
  11 August–7 September and 8 September–5 October. QULA site-level totals:
  impressions 1,029 → 202; clicks 32 → 21. HAIBU: 309 → 746 impressions;
  2 → 29 clicks. Daily source data ends on 5 October. Page-level impression
  totals differ from site totals and must not be substituted for them.
- Read-only production checks: QULA homepage, Acrylic/Pen category pages,
  pen guide, CZB26353, robots and sitemap respond 200; apex URLs resolve to www;
  sampled pages use self-canonicals and `index,follow`. These demonstrate HTTP
  crawlability, not Google indexing or the cause of the impression decline.
- YA893/YA690/YJ145/YA449/YA425/YA417/YA382 plus CZB26353 are the initial
  measurement batch. Still required: minimum hole diameter, hole direction,
  width/height/depth, occupied pen-rod length, actual rod measurement and sample
  assembly. Do not invent them from photos. Pack reference is not MOQ.
- YM216's title says resin while captured material fields say acrylic/plastic;
  YT025's title and material fields also conflict. Material remains a quotation
  confirmation item; this PR does not infer a replacement.
- HAIBU product consistency passes for all 139 products. No HAIBU public copy is
  changed in this batch. SLM26529's user-confirmed 5 g/bag, typical 100-bag MOQ
  and 7–15-day dispatch must not be generalized to other SKUs; additional bag
  options and their source evidence still require business confirmation.
- QULA #54 and HAIBU #90 remain separate draft analytics PRs. The available
  Oct 5–7 GA4 extract contains one QULA `form_submit` row dated Oct 5 and no
  `generate_lead` row. This is not a new successful-mail/event acceptance test.

## Validation

- Inquiry-email, required-products, SEO and IndexNow build checks pass.
- `gates_full.py`: 238 PDPs, 277 indexable URLs, valid JSON-LD and links pass.
- Python compilation and git whitespace checks pass.
- All 17 changed Product schemas match visible types and `public_specs()`;
  original imported data and catalogue remain byte-identical to `origin/main`.
- Existing homepage, Pen category/guide, measurement blog and quote form remain
  byte-identical; all changed pages retain their title, H1 and canonical URL;
  all 17 price blocks remain byte-identical.
- Decoden source answer, final FAQ answer and modification date match HTML.
- Preview deployment and browser verification are recorded separately once
  available. No production merge is included in this change.
