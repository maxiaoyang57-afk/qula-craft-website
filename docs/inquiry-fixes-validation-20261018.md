# Inquiry draft and keyboard fixes — 2026-10-18

Based on fresh `origin/main` at `a54476412dd6746d5d0270b54387d952c709bd6d` (#84), checked again before commit. Work is isolated on `fix/inquiry-fallback-keyboard-latest-20261018`. The older `fix/inquiry-fallback-keyboard-20261018` branch remains at `582fabd9ceac98de03801df977dc35b98c2271f6`.

## Result

- All six email/WhatsApp links on the quote page carry the current selected product, saved inquiry SKUs, product requirements, active reply details and source page. Form changes and basket changes refresh the links; a final click-time refresh covers programmatic changes. User text, Unicode and literal `&amp;` survive URL encoding.
- Links over 2,000 characters retain the complete draft, show a visible advisory and prevent launching an unreliable link. Reference-file reminders follow the actual attachment list; files still require separate attachment in an email or WhatsApp client.
- Inquiry add, remove and clear controls are native `type="button"` controls. Removal retains keyboard focus on a remaining action or the requirements field. SKU quantity edits on retained lines and independent customer notes survive synchronization; initial customer text is never claimed as generated text.
- About is no longer active on `quote.html`; Get Quote has `aria-current="page"`.
- 776 static add controls in 397 pages and their generators were updated. All 432 HTML pages receive only relevant script/style cache-version changes plus the specified button/navigation edits. The precise SKU-search filtering and ranking are unchanged.

## Preservation checks

`assets/data`, `assets/images`, `sitemap.xml`, `llms.txt`, and `llms-full.txt` have no diff from the base. The catalog still contains 388 groups and 388 PDPs; the site contains 432 HTML pages, including 430 indexable pages. No generator was run. A stale SKU-correction test count was updated from 372 to the current 388 without changing catalog data.

## Validation performed on Windows

Browser engine: installed Microsoft Edge `149.0.4022.98`, driven by bundled Playwright `1.62.1`. Automated runs used isolated browser contexts. The connected desktop Edge also opened the preview at desktop and 375px widths for keyboard/add/clear, selected-product coexistence, link-body and layout inspection.

| Check | Result |
| --- | --- |
| New inquiry browser scenarios at 375, 414 and 1440px | 24 passed |
| Existing product batches and article browser scenarios at 375, 414 and 1440px | 18 passed (part of a 39-test run including 21 earlier inquiry cases) |
| Existing mobile-layout suite, including 360, 390, 768px and desktop comparisons | 13 passed |
| Confirmed-lead / preview / consent browser and VM tests | 16 passed |
| Python catalog-schema, image-batch and SKU-correction tests | 4 passed |
| Basket synchronization VM regression | Passed, including CRLF, quantity edits, customer bullets and initial matching-SKU draft |
| Inquiry email, multipart, 10MB, local-image, preview, analytics and production-approval guards | Passed |
| Required-products, SEO, IndexNow, custom-design guide, September product-batch checks | Passed |
| `scripts/gates_full.py`, JavaScript syntax, `git diff --check` | Passed |

The new scenarios verify Tab/Enter/Space, deduplication, remove/clear focus, all six contact links, URL product plus saved list, typed quantities and requirements, literal ampersand entities and Unicode, long-link blocking, attachments, reply-method validation, non-production sending protection, and distinct RW26808/RW20809 searches. External requests and native submission are intercepted. Production submission behavior is simulated with local fixtures; no real delivery or external client launch was performed.

The existing Linux-oriented test server command and browser executable were replaced only in local test configuration outside the repository, using the bundled Python interpreter and installed Edge. Initial sandbox socket/process restrictions were resolved by running these local-only test processes with approved access. Final screenshots were captured with reduced motion and the page at the top to avoid reveal-animation artifacts.

## Source-package transfer limitation

The exact Library item `libfile_b0aa67fe2ce08191bb5e1c05b2f51be8` was resolved through the current supported materialization flow. Its official transfer helper failed on Windows with `AttributeError: module 'os' has no attribute 'setxattr'` before installing the final file. No readable final ZIP was produced, so the supplied ZIP SHA256 was not verified and no semantic diff against that ZIP is claimed. These fixes were independently reconstructed from the freshly fetched #84 source and verified there. The old #83 package was never overlaid on the current site.

No merge, production deployment, real inquiry, email, or WhatsApp message was performed. Local preview: `http://127.0.0.1:4175/quote.html`.
