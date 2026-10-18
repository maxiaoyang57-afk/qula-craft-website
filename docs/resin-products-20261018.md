# October 18 resin batch

Source: owner-supplied `10.11(10).xlsx`, Sheet1 rows 122–132, plus 11 SKU-named PNG files. Add only the nine missing products: RW26808, RW25560, RW26804, RW26803, RW26801, RW26798, RW26797, RW26795, RW26794. Catalog: 350 → 359. All are Resin Charms. RW26800 and RW26796 pages remain byte-for-byte unchanged.

Raw source rows and normalized plans are in `scripts/data/product-source-20261018.json` and `product-plan-20261018.json`. The batch manifest records source references and output image hashes. Each product has its supplied reference, a source-specification graphic and a packing/order graphic. Graphics are explicitly labeled and do not represent extra photographs. The 100-piece bag is a pack reference, not MOQ. Prices, stock quantities and dispatch dates are not inferred.

Use `p-rw26808-acorn.html` for the new acorn product. The historical `p-rw26808.html` redirect continues to the corrected pig/cabbage product RW20809. Catalog search, category cards and inquiry context use the new acorn link. No global metadata, inquiry routing, analytics or legacy redirect was changed.

Validation: repository gates; email protection; required-product, SEO and IndexNow checks; four existing Python tests. PR browser verification covers all nine galleries, SKU searches and quote prefills at 375/414/1440 px. No live inquiry is submitted. This branch prepares a preview; production publishing remains separate.
