# Pen bead size and fit blog — 2026-10-01

- Target: QULA / qula-craft-website. Baseline: main a3e62bc8c127db983fb8d0d7c30c6441363a138c (PR #51).
- Request: detailed English buying blog with bead diameter, hole diameter and usable pen beading length illustrations. Preview only; production approval is separate.
- New URL: blog-beadable-pen-bead-size-guide.html. Distinct measurement intent; the existing wholesale sourcing guide and its URL remain in place.
- Source: current QULA_2026-09-30_Product_Listings.xlsx, Library version 2, read 2026-10-01. YA893: 15 mm outer diameter, 100 pieces/bag, hole unconfirmed. YA425: 16 × 18 mm, 2.5 mm hole, 500 g/bag; measurement axes and stack height are not supplied.
- No measured pen rod or usable pen length is supplied. D, d, H, r and L are symbolic in the first two diagrams. The third diagram's 50 mm usable length, three 15 mm heights and two 2 mm spacer heights are explicitly hypothetical, giving 49 mm occupied and 1 mm remaining. This is not a product specification or universal clearance recommendation.
- Three original SVG technical diagrams, not generated product photographs. Labels remain editable and open at full size. Original YA893 and YA425 main photographs are reused unchanged. No product data, prices, MOQ, shipping promises, catalog order or product schema changes.
- New article includes material/shape selection, measurement procedure, stack calculation, sample checks, real SKU comparisons, and wholesale enquiry checklist. BlogPosting, BreadcrumbList and matching visible FAQ/FAQPage data included.
- Added entrances from Resources, Beads for Pens, and the existing pen-bead guide; synchronized that guide's source content.
- Corrected the category FAQ's blanket standard-pen compatibility claim in both visible text and JSON-LD because it contradicts the measurement guidance. No unrelated category claims edited.
- Build the blog and SVGs with `python scripts/build_pen_fit_blog.py`; source body is scripts/data/pen-bead-size-guide-body.html. The new CSS is page-scoped and versioned.
- All four build gates and the full local site gate pass: 278 HTML pages, 238 PDPs, 276 sitemap URLs. Python syntax passes. PR #52 Preview deployment succeeded.
- Browser verification: reviewed all three SVGs individually, corrected a label near a dimension line, confirmed all five article images load, verified the enquiry CTA carries the bead-fit request, and expanded a FAQ answer successfully.
- Responsive verification used temporary same-origin iframe viewports at 375 and 390 px outer width (360 and 375 px document width after scrollbars). Both had equal client/scroll widths: no horizontal overflow. Diagram labels, navigation and inquiry controls were inspected. This is viewport testing, not a physical-device test. The temporary verification page was removed from the final branch.

## Research used

Checked October 1, 2026. Primary seller pages demonstrate model-specific fit requirements, not QULA measurements; no competitor images copied.

- https://www.madisonbeads.com/products/diy-blank-black-beadable-pens-pen-blanks-custom-pen-beaded-pens-unique-gifts — 52 mm stick, stated minimum 1.5 mm hole.
- https://www.pandahall.com/p-2536787-brass-beadable-pens-press-ball-point-pens-for-diy-pen-decoration.html — AJEW-L082-B02, approximately 2 mm pole, stated minimum 2.5 mm hole.

## Buyer limitations

Dimensions must be confirmed for the buyer's actual pen blank. Equal nominal rod/hole values do not establish clearance. Shaped bead size is not interchangeable with axial stack height. The sample must close correctly without forcing beads or leaving the cap partly fastened.
