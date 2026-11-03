# QULA Site Audit remediation 3 November 2026

Source baseline: origin/main `946b1dfa8223693736ba9dbd5ae2216a43d9ebb2`, after PR175. The 100-page Site Audit sample reported health 91%, AI search health 99%, 33 errors and 836 warnings. These are diagnostic counts, not Google indexing counts.

| Finding | Evidence and treatment |
| --- | --- |
| 33 hreflang conflicts | Every reported URL was a parameterized version of quote.html. Its canonical was already correct. Remove unnecessary English/x-default alternates on this single-language form. Published internal RFQ links now carry transient form state in a fragment, preserving every parameter. Old query links remain supported. Product, category and sitemap URLs do not change. |
| 558 unminified JS/CSS occurrences | Build minifies the eight local scripts and eleven local stylesheets with pinned esbuild. Readable source stays in Git; output goes to dist. Every HTML reference uses a build content fingerprint. |
| 255 external-link warnings | First 50 inspected occurrences were wa.me returning 429 to SiteAuditBot. The exact business number +86 186 3202 6595 was opened in the connected browser and reached WhatsApp's correct chat landing page. No message was sent. Keep the working customer contact route; external crawler throttling may remain in Semrush. |
| 16 URLs with too many parameters; 15 URLs over 200 characters | Form selections now use the quote fragment, without creating separate HTTP document URLs. Keep all SKU, image, category, application and acquisition context, and retain legacy-query support. |
| Four title/H1 warnings | Change only search/social titles on the three reported guides and YX625. Preserve their visible H1s and synchronize generator/copy sources. |
| Three low text/HTML ratios | These are product category pages with real product cards, images and ItemList data. Retain their contents and schema; minify the output without adding filler text or deleting product evidence to change a tool ratio. |
| 95 permanent redirects | Sampled redirects were index.html to /. Published navigation now links directly to /. Existing redirect remains for old URLs. |
| 31 pages with one incoming link | Full repository graph contradicts nine of the ten product examples: 2–5 incoming pages each. YX4102 actually had only one; add a relevant link from the existing seasonal procurement calendar. Remaining sampled examples are RFQ parameter variants handled above. A 100-page crawl does not measure the full-site link graph. |
| One resource formatted as a page link | Factory MP4 viewing/download link is intentional. Preserve it. |
| Core Web Vitals 0% | Ten mobile Lighthouse samples: 0 good, 2 need improvement, 8 poor; this is not a universal speed score. The consent panel was inserted in normal document flow after initial rendering. Build emits the existing consent markup and CSS before first paint, and the existing code binds its choices. Existing consent/GA4/Clarity rules remain unchanged. Match responsive image preloads to the selected hero resource; prioritize the two sampled first images previously lazy-loaded. A fresh measured result is required before claiming improved CWV. |

Validation includes full source routing/product/SEO/IndexNow guards; full PDP gates; 31 existing unit checks; 1,035-page built-output metadata, structured-data, catalog-fact and RFQ parameter preservation checks; browser regression on built output at 375, 414 and 1440 px; and actual deployed Preview verification before merge. No real inquiry, analytics hit or customer message is part of acceptance.

Preserved constraints: nine categories, 988 public records and two archived product references; original product identities and images; all commercial values; inquiry recipients and measurement definitions; existing observation windows. Existing PR175 changes remain in the base.

References: [esbuild minification](https://esbuild.github.io/api/#minify), [Google URL structure](https://developers.google.com/search/docs/crawling-indexing/url-structure), [Google language versions](https://developers.google.com/search/docs/specialty/international/localized-versions). Fragment state is exclusively for filling a form, never for indexable product or category content.
