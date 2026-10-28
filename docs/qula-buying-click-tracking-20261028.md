# QULA buying-step measurement — 2026-10-28

The site declared `product_click` and `quote_click` in the Clarity event allowlist but did not emit either event. Add one delegated click listener to the existing analytics script so guide links, catalog cards, related products and dynamically rendered search results can be measured without treating a click as a lead.

| Event | Trigger | Meaning |
| --- | --- | --- |
| `product_click` | Link to a canonical-host `/p-*.html` page | A product link was activated, not proof the destination loaded |
| `quote_click` | Link to canonical-host `/quote.html` | The quote-page link was activated, not a submitted inquiry |
| `inquiry_submit_attempt` | Existing form submission handler | Submission attempt; unchanged |
| `generate_lead` | Existing valid pending marker and thank-you return | Confirmed return; not proof an email was delivered; unchanged |

New click events require saved analytics consent `granted` and are suppressed under GPC or DNT. They are never replayed when a visitor accepts later. The existing production-host guard also excludes previews. They carry only `page_path`, a query-free `page_location`, `destination_path` and an enumerated `link_location`. No link text, SKU query, form content, URL query or hash is added to these event payloads. Destination paths are restricted to the product/quote patterns; external lookalikes, credentials and custom ports are excluded.

`link_location`: `navigation`, `footer`, `product_card`, `hero`, `mobile_cta`, or `content`. Dynamic cards and nested link children use the same delegated listener. The listener does not delay navigation, send a form, or mark clicks as key events.

The original release updated all 688 root HTML pages only with the analytics resource version change to `20261028-buying-clicks`; page content, metadata and sitemap dates remained stable. PDP/guide generation inherits the current HTML shell. Update the inquiry guard's expected version as well.

Later on October 28, a read-only check of the 709-page main branch found two newly added pages (`p-rw26455.html` and `p-rw26633.html`) still referencing the older cache version. Their HTML changes only update that reference. The inquiry/build guard now checks every root HTML page for exactly one current analytics script, so stale or duplicate script references on future product uploads fail the build. The analytics runtime itself is unchanged. This corrects a cache-related measurement risk; it does not prove that historical events were lost or backfill any events.

Validation: existing email/BCC, product, SEO and full catalog gates; consent adapter tests; browser scenarios in `scripts/tests/lead-tracking.test.cjs` for real guide links, dynamically inserted quote links, one event per click, consent acceptance/withdrawal, query stripping, invalid destinations, GPC/DNT, preview isolation and confirmed-lead regression. Browser fixtures fulfill site requests locally and abort external requests, so they send no analytics hits or inquiries.

After release, verify event receipt and existing custom definitions in the actual GA4 property before building parameter-level reports. Do not mark these clicks as leads, register duplicate definitions, backfill historical clicks, or infer that a missing event means no user clicked before this release. Use event names and path exploration first; any custom-dimension registration requires checking existing definitions. Baseline begins on deployment, not on the dates of earlier reports.

Official event API: https://developers.google.com/analytics/devguides/collection/ga4/events
