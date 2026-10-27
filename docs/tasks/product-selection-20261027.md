# Product selection and inquiry continuity — 27 October 2026

Six existing PDPs showed source specifications and contact actions but lacked
product-specific project/sample questions. Add short selection sections for
YX043, YX3194, YX3301, YA425, YA382 and CZB26353. The selection is based on the
existing polymer shortlist, buyer questions about mix composition and the
original eight-product measurement batch; it is not a claim these six have the
most search traffic or confirmed orders.

## Content evidence

- Source records remain `assets/data/pdp-data.json`. Existing published
  specifications, commercial numbers, images, titles, metadata and Product
  schemas are unchanged.
- YX043's title references 500 g; it does not provide individual piece size.
- YX3194's pack is 1,000 g; components, dimensions and mix ratios require
  confirmation. YX3301's packing record is 500 g; no ratio is inferred.
- YA425 lists 16 × 18 mm, 2.5 mm hole and 500 g packing. Those figures do not
  establish pen fit or piece count. YA382 references 100 pieces, with dimensions
  and numeric hole size still unpublished.
- CZB26353's source title references 100 pieces. Its pen fit remains untested;
  no measurements are inferred from photos. The earlier public `Resin bead`
  correction is preserved.
- Application suggestions are sample-planning guidance, not liquid, adhesive,
  safety or pen-compatibility claims. No new MOQ, price, lead time, certification
  or availability promise is introduced.

## Implementation and checks

- Shared renderer `scripts/pdp_selection_guides.py` supplies the full PDP
  generator and an idempotent update of these six existing sections.
- Each new inquiry link retains the PDP's original destination, SKU, image and
  product fields. Four older primary links (YX043, YA425, YA382, CZB26353) lacked
  a category parameter; add the matching existing category option so buyers no
  longer have to select it again. Existing inquiry forms and analytics are
  unchanged. Links point to existing
  selection guides and relevant comparison products, without a new landing page.
- Only the six edited PDP sitemap dates change. Category titles and URLs remain
  in their 13 October–9 November observation window.
- Verify original HTML is byte-identical after removing only the added sections
  and jump links and restoring the four normalized inquiry hrefs, plus the
  normal SEO/email/catalog/IndexNow gates.
- Browser coverage checks the jump link, guide destinations, responsive layout,
  correct SKU/image/category in the quote page and draft contact text. It does not submit
  a form, open WhatsApp or count a test lead.

## Indexing and outcome boundary

Read-only public HTTP checks on 27 October returned 200 for the four main
categories, these six PDPs, robots and sitemap. All ten HTML pages have a single
H1, self canonical and `index,follow`; no X-Robots-Tag was returned. This checks
technical accessibility, not Google's actual indexed state. Current authorized
Google UI access was unavailable in this task, so the 22 October URL-inspection
results are retained as dated evidence. No repeated indexing requests, connector
renewal, account disconnection or new automation is performed.

Compare future non-brand search coverage, page-to-inquiry paths and actual
deduplicated inquiries after release. The latest inspected search window ends
24 October and cannot measure this change. No conversion improvement is claimed
before comparable data exists. Preview, CI and production results are recorded
in the existing continuation record after release.
