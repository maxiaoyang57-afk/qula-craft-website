# QULA custom development scope — 2026-09-28

## Owner-confirmed business facts

- Enquiries may cover custom focal beads / 3D flatback charms and finished keychains, bracelets and necklaces.
- Do not accept baby or infant product projects.
- Do not offer silicone-material customization. This applies to silicone regardless of the intended age group.
- Other details require email discussion: design, material, process, proof format, prototype / pre-production sample, tooling and ownership/exclusivity terms, testing/documentation requirements, MOQ, pricing and lead time.
- Do not turn a general statement of capability into automatic acceptance of every design or a blanket certification promise.

## Implementation

The customization page explains components versus finished accessories and the enquiry stages. Homepage, quote form, keychain/jewelry category entrances, FAQ and quality page direct buyers to the same scope. The established private-label guide URL now explains briefs for focal beads, flatbacks and assembled products; its timeline is project-specific. Sampling guide and generator source use the same email-confirmation policy. Relevant JSON-LD, llms.txt and sitemap dates are aligned.

No SKU records or product images were changed. Existing stock items have not been delisted; the scope above governs custom project acceptance. Inquiry routing is unchanged.

## Validation and release

Repository baseline: 020c6ce804591b09a5f9c2232a105bff7272e132.
Branch: feat/qula-custom-capabilities-20260928.
Run the repository's Vercel gates and scripts/gates_full.py before release. This change is prepared for Preview review; production release requires approval of the resulting PR/Preview.

## Tone refinement — owner approved 2026-09-28

Keep the business exclusions unchanged, but concentrate buyer-facing wording in the customization FAQ and RFQ sidebar. Use “outside our current customization scope”. Homepage, category entrances and the blog emphasize available services and individual email review rather than repeating exclusions. Testing documentation is reviewed separately by product and target market.
