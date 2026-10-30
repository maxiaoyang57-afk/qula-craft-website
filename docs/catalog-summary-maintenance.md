# Published catalog summaries

After adding or removing catalog entries, run `node scripts/sync-catalog-summary.mjs`
and commit the updated `llms.txt` and `llms-full.txt` headers/summary. The checker
uses the existing catalog's category arrays and original page URLs; it does not
change product records, item-level index lines, parameters or inquiry settings.

CI runs `node scripts/sync-catalog-summary.mjs --check` to detect stale counts or
missing product URLs. A catalog entry is not a guarantee of current inventory.

Alibaba supplier metrics are a separate dated snapshot, checked October 30,
2026. Recheck the platform profile before changing its numbers or review date;
do not substitute merchant-authored storefront copy for platform metrics.
