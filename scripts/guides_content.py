# -*- coding: utf-8 -*-
"""指南内容定义。数字来源:
  · SKU/包装/MOQ/价格 → assets/data/pdp-data.json 实抓值
  · 材质与工艺事实 → 2026-07-25 逐条 WebFetch 验证过正文的权威源(见 gen_guides.SRC)
禁止在此文件写任何未经核实的数字。
"""

WIKI_CLAY = "https://en.wikipedia.org/wiki/Polymer_clay"
WIKI_PET = "https://en.wikipedia.org/wiki/Polyethylene_terephthalate"
WIKI_RESIN = "https://en.wikipedia.org/wiki/Resin_casting"
ICC = "https://iccwbo.org/business-solutions/incoterms-rules/"
HS = "https://www.trade.gov/harmonized-system-hs-codes"

GUIDES = [

# ─────────────────────────────────────────────────────────────
{'slug': 'guide-beadable-pen-beads.html',
 'title': 'Beadable Pen Beads Wholesale: Sizes, Focal Beads & Sourcing',
 'desc': 'Source beadable pen beads wholesale with hole-fit, focal bead, lot size and theme guidance for DIY '
         'pen makers, craft stores and private-label kits.',
 'crumb': 'Beadable Pen Beads',
 'eyebrow': 'Sourcing Guide',
 'h1': 'Beadable Pen Beads: Hole Fit, Materials and Wholesale Packs',
 'updated': 'October 1, 2026',
 'hero': 'assets/images/real-life-scenes-v1/real-life-beadable-pen-gift.webp',
 'heroW': 1200,
 'heroH': 1200,
 'heroAlt': 'Finished beadable pens with cartoon resin focal beads and spacer beads',
 'heroCap': 'Finished beadable pens — focal bead, spacers and a standard pen blank.',
 'answer': '<b>Short answer:</b> choose beadable pen beads by <b>hole diameter, hole direction and usable '
           'rod length</b> before choosing a color or theme. Qula Craft offers resin focal designs and '
           'acrylic beads, but a bead with a hole is not automatically compatible with your pen blank. Check '
           'the SKU, pack unit, minimum order and sample requirements before requesting a wholesale quote.',
 'bodyHtml': '\n'
             '  <h2>1. What hole size do beadable pen beads need?</h2>\n'
             '  <p>There is no single hole diameter that fits every beadable pen. Measure the rod that '
             'passes through the beads, including any threaded section they must slide over. Share that '
             'measurement and the usable beading length with your enquiry. The outside diameter of the pen '
             'grip does not establish the rod size.</p>\n'
             '  <p>Check the hole direction against the way you want the design to face. A top-to-bottom '
             'hole may suit an upright focal design; a side-to-side hole can change its orientation. Ask us '
             'to confirm the exact SKU with a photo or sample. Never force a bead onto a rod that is too '
             'wide.</p>\n'
             '  <p>For example, <a href="p-ya425.html">YA425 heart acrylic beads</a> have a listed <b>2.5 mm '
             'hole</b>. This is a product measurement, not a universal pen-fit guarantee. The other acrylic '
             'styles below require hole-diameter confirmation before ordering.</p>\n'
             '\n'
             '  <h2>2. Acrylic beads and resin focal beads: where to start</h2>\n'
             '  <p>Browse <a href="acrylic-beads.html">acrylic beads</a> for round, leaf, heart and novelty '
             'shapes, or <a href="beads-for-pens.html">beads for pens</a> for focal designs. Confirm the '
             'material on the individual product page. Do not assume that every bead in a pen photograph has '
             'the same material, hole size or supply unit.</p>\n'
             '  <p>Choose a focal shape first, then compare its height and width with the available rod '
             'length and any spacers you plan to use. Test an assembled sample for balance, clearance and '
             'the intended orientation. Styling photos illustrate an idea; pen blanks and other props are '
             'not included unless the quotation explicitly lists them.</p>\n'
             '\n'
             '  <h2 id="acrylic-bead-options">3. Acrylic bead options to compare</h2>\n'
             '  <p>These are the supplied bead dimensions and pack references. Pack size does not establish '
             'the minimum order. Send the SKU and your pen-rod or cord measurement so we can confirm '
             'suitability.</p>\n'
             '  <div style="overflow-x:auto"><table class="spec-table matrix">\n'
             '    <thead><tr><th scope="col">Product</th><th scope="col">Listed size</th><th '
             'scope="col">Pack reference</th><th scope="col">Hole fit</th></tr></thead>\n'
             '    <tbody>\n'
             '    <tr><td><a href="p-ya893.html">YA893 · AB swirl round</a></td><td>15 mm '
             'diameter</td><td>100 pieces/bag</td><td>Diameter to confirm</td></tr>\n'
             '    <tr><td><a href="p-ya690.html">YA690 · AB leaf</a></td><td>12 × 23 mm</td><td>100 '
             'pieces/bag</td><td>Diameter to confirm</td></tr>\n'
             '    <tr><td><a href="p-yj145.html">YJ145 · AB heart</a></td><td>19 mm listed size</td><td>100 '
             'pieces/bag</td><td>Diameter to confirm</td></tr>\n'
             '    <tr><td><a href="p-ya449.html">YA449 · Textured candy</a></td><td>16 mm listed '
             'size</td><td>200 pieces/bag</td><td>Diameter to confirm</td></tr>\n'
             '    <tr><td><a href="p-ya425.html">YA425 · AB heart</a></td><td>16 × 18 mm</td><td>500 '
             'g/bag</td><td>2.5 mm; compare with your rod</td></tr>\n'
             '    <tr><td><a href="p-ya417.html">YA417 · Pig</a></td><td>19 × 26 mm</td><td>100 '
             'pieces/bag</td><td>Diameter to confirm</td></tr>\n'
             '    <tr><td><a href="p-ya382.html">YA382 · Cupcake</a></td><td>Dimensions to '
             'confirm</td><td>100 pieces/bag</td><td>Diameter to confirm</td></tr>\n'
             '    </tbody>\n'
             '  </table></div>\n'
             '  <p>For YJ145 and YA449, ask which measurement axis the listed size describes if your design '
             'has limited clearance. For YA382, request dimensions before planning your bead '
             'arrangement.</p>\n'
             '\n'
             '  <h2>4. Compare piece-count and weight-based packs</h2>\n'
             '  <p>A 100-piece bag and a 500 g bag are different ordering units. Do not treat 500 g as 500 '
             'pieces or assume a fixed bead count without confirmation. Compare quotations using the same '
             'product, color selection, pack unit and quantity.</p>\n'
             '  <p>For a pen project, calculate the beads required from your own design: finished pens '
             'multiplied by beads of that SKU per pen. Agree any allowance for sampling or assembly '
             'separately. Confirm whether colors are mixed or selected and whether different SKUs can ship '
             'together.</p>\n'
             '  <p>Prices, minimum quantities, sample fees and dispatch dates are confirmed in the '
             'quotation. The pack references above are not a price list or a promise that one bag is the '
             'minimum for every product.</p>\n'
             '\n'
             '  <h2>5. Check a sample before planning your collection</h2>\n'
             '  <p>Use the pen blank you intend to sell with the beads. Check that each bead slides into '
             'place without force, sits in the intended direction and leaves room for the end fittings. '
             'Review the finish and color against your approved sample, then confirm the packaging for the '
             'order.</p>\n'
             '  <p>For a themed range, start with a small selection you can compare together, such as '
             'hearts, animals or desserts. Choose the quantity from your sales plan and confirmed minimums. '
             'See our <a href="guide-samples-and-inspection.html">sample and inspection checklist</a> and <a '
             'href="guide-craft-supply-packaging.html">craft packaging guide</a> for the details to agree '
             'before a bulk order.</p>\n'
             '\n'
             '  <h2>6. What to include in your wholesale enquiry</h2>\n'
             '  <ul><li>SKU, color or finish, and quantity in pieces or bags.</li><li>Pen-rod diameter, '
             'usable length and a photo of the blank.</li><li>Required hole direction and your intended bead '
             'arrangement.</li><li>Packaging, sample needs, destination and requested delivery '
             'date.</li><li>Reference artwork and material preference for custom projects.</li></ul>\n'
             '  <p>Custom focal beads and finished accessories are reviewed individually. Design, sample, '
             'tooling and packaging details are agreed by email. Explore <a '
             'href="customization.html#finished-accessories">custom components and finished accessories</a> '
             'when you need a coordinated collection.</p>\n'
             '\n'
             '<h2>Frequently asked questions</h2><div class="faq-list"><details><summary>What hole size fits '
             'a beadable pen?</summary><p>It depends on the pen rod. Measure the rod and any threaded '
             'section the bead must pass over, then confirm the bead hole diameter and direction for the '
             'exact SKU.</p></details><details><summary>Are these acrylic beads guaranteed to fit my '
             'pen?</summary><p>No. YA425 has a listed 2.5 mm hole; the other acrylic styles in this guide '
             'require hole-diameter confirmation. Check dimensions and fit with your own pen blank before '
             'ordering.</p></details><details><summary>Does a 100-piece bag mean a one-bag '
             'minimum?</summary><p>No. Pack size and minimum order are separate. Confirm the minimum '
             'quantity, price and color selection for each SKU by '
             'quotation.</p></details><details><summary>Can Qula Craft make custom focal beads or finished '
             'accessories?</summary><p>Custom components and finished accessories can be discussed. Design, '
             'material, sample, tooling and packaging details are reviewed for the project and confirmed by '
             'email.</p></details></div>\n',
 'note': '<b>Before you order:</b> confirm dimensions, hole fit, pack unit and minimum quantity for each '
         'SKU. Approve the sample and written quotation before committing to bulk quantities.',
 'ctaH2': 'Get a quote with the pen spec filled in',
 'ctaP': 'Send the SKUs you like, your pen-rod measurements, required quantities and destination. We will '
         'review hole fit, packaging and sample requirements with your quotation.',
 'ctaHref': 'quote.html?product=Beads%20for%20Pens',
 'ctaLabel': 'Request a beadable pen bead quote',
 'faq': [('What hole size fits a beadable pen?',
          'It depends on the pen rod. Measure the rod and any threaded section the bead must pass over, then '
          'confirm the bead hole diameter and direction for the exact SKU.'),
         ('Are these acrylic beads guaranteed to fit my pen?',
          'No. YA425 has a listed 2.5 mm hole; the other acrylic styles in this guide require hole-diameter '
          'confirmation. Check dimensions and fit with your own pen blank before ordering.'),
         ('Does a 100-piece bag mean a one-bag minimum?',
          'No. Pack size and minimum order are separate. Confirm the minimum quantity, price and color '
          'selection for each SKU by quotation.'),
         ('Can Qula Craft make custom focal beads or finished accessories?',
          'Custom components and finished accessories can be discussed. Design, material, sample, tooling '
          'and packaging details are reviewed for the project and confirmed by email.')],
 'related': [('beads-for-pens.html',
              'Browse beads for pens',
              'Compare focal designs and confirm the specifications for your pen blank.'),
             ('acrylic-beads.html',
              'Compare acrylic beads',
              'Browse shapes, pack units and per-SKU enquiry options.'),
             ('guide-craft-supply-packaging.html',
              'Choose your packaging',
              'Discuss bulk bags, retail packs and labeling for your order.')],
 'dateModified': '2026-10-01'},

# ─────────────────────────────────────────────────────────────
{
 "slug": "guide-bingsu-beads-slime-fillers.html",
 "title": "Bingsu Beads vs Fishbowl Beads vs Foam: Slime Filler Guide",
 "desc": "What bingsu beads actually are (PET, not glass), how they differ from fishbowl beads and foam balls, what 500g of each covers, and how to pick a filler by the texture you are selling.",
 "crumb": "Slime Filler Guide",
 "eyebrow": "Sourcing Guide",
 "h1": "Bingsu Beads vs Fishbowl Beads vs Foam: A Filler Guide",
 "updated": "July 2026",
 "hero": "assets/images/downstream-covers-v2/downstream-topped-slime-jars-v2.webp",
 "heroW": 1200, "heroH": 1200,
 "heroAlt": "Finished slime jars topped with bingsu beads, sprinkles and charms",
 "heroCap": "Finished jars — the filler decides the sound and the texture, not the topping.",
 "answer": ("<b>Short answer:</b> bingsu beads are soft, iridescent <b>PET</b> strands that give slime a crunchy-but-light "
            "texture; fishbowl beads are hard, rounded and louder; foam balls are the cheapest bulk volume and change the "
            "texture to floam. Our bingsu packs ship <b>500g per bag from one bag</b>. Pick by the sound and stretch you are "
            "selling, then match the topping to it — not the other way round."),
 "bodyHtml": f"""
  <h2>1. The three fillers, side by side</h2>
  <table class="spec-table matrix">
    <tr><th>Filler</th><th>Material &amp; feel</th><th>What it does to the slime</th><th>Watch out for</th></tr>
    <tr><td><b>Bingsu beads</b></td><td>Soft PET strands, iridescent, very light</td><td>Fine crunch with almost no weight; keeps stretch</td><td>Colour can migrate into pale bases — test before a big batch</td></tr>
    <tr><td><b>Fishbowl beads</b></td><td>Hard rounded plastic</td><td>Loud, obvious crackle; adds visible volume</td><td>Sinks and pools at the bottom of a jar on the shelf</td></tr>
    <tr><td><b>Foam balls</b></td><td>Expanded foam, various diameters</td><td>Turns the base into floam; cheapest way to add bulk</td><td>Changes the product category — floam buyers and slime buyers differ</td></tr>
  </table>
  <p>Our stock bingsu is listed as PET. That matters more than it sounds:
  <a href="{WIKI_PET}" target="_blank" rel="noopener">PET carries resin identification code&nbsp;1 and is practically insoluble
  in water</a>, which is why the strands hold their shape in a wet slime base instead of softening into mush the way some
  cheaper substitutes do.</p>

  <h2>2. What 500g actually covers</h2>
  <p>Both of our bingsu packs are <b>500g per bag, minimum one bag</b>. Because bingsu is so light, 500g is a lot of visible
  volume — considerably more jars than 500g of a dense filler would cover. Rather than guess at a jars-per-bag figure that
  depends entirely on your dosing, do it the reliable way:</p>
  <ul>
    <li>Weigh the filler you put into <b>one</b> finished jar at the density you actually like.</li>
    <li>Divide 500 by that number. That is your jars per bag, for your recipe.</li>
    <li>Re-check after the first production run — most makers use less than they expect once they see it in the jar.</li>
  </ul>
  <p>This is the same reason we sell trial sizes on the sprinkle side of the catalogue: guessing dosage from a photo is the
  fastest way to end up with dead stock.</p>

  <h2>3. Colour bleed is the failure mode that costs a batch</h2>
  <p>The single most common complaint about any iridescent filler is colour migrating into a pale base after a few weeks on
  a shelf. It is not always visible on day one, which is what makes it expensive — you find out after the batch has shipped.</p>
  <p>Test it in 20 minutes before you commit: put a pinch of filler into your palest base, seal it, leave it somewhere warm
  and check at 24&nbsp;hours and again at a week. If the base has picked up a tint, keep that filler for saturated colours only.
  Do this per batch, not per supplier — pigment lots change.</p>

  <h2>4. Filler versus topping — they are different jobs</h2>
  <p>Fillers change the <em>texture and sound</em> of the slime and get mixed through. Toppings sit on the surface, sell the
  photograph, and are usually clay or resin. Confusing the two is why some jars look great and feel wrong.</p>
  <p>Clay sprinkles are a topping, not a filler, and there is a physical reason:
  <a href="{WIKI_CLAY}" target="_blank" rel="noopener">polymer clay is a PVC-based material that cures at roughly
  129&ndash;135&nbsp;°C</a> — it is a fully cured solid by the time it reaches you, so it holds its printed detail on the
  surface where buyers see it, rather than being worked through the base where the detail is wasted.</p>

  <h2>5. A filler range that does not overstock you</h2>
  <p>You do not need every filler. Most shops that reorder steadily run one crunchy filler, one visual topping range and one
  seasonal set, then rotate the seasonal slot four times a year. Concretely: one bingsu pack for the crunch, a clay sprinkle
  mix for the surface, and a themed charm set that changes with the calendar.</p>
  <p>Everything above ships from one bag, so you can build that three-part range for a first order without committing to
  bulk on any single line — then scale only what sells through.</p>
 """,
 "note": ("<b>Test before you scale:</b> pinch of filler into your palest base, sealed, checked at 24 hours and one week. "
          "Do it per batch — pigment lots change, and colour bleed does not show on day one."),
 "ctaH2": "Get a filler quote with your texture in mind",
 "ctaP": ("Tell us the texture you sell — light crunch, loud crackle, floam — and the base colour. We quote by the bag with "
          "carton data attached, and can send trial quantities before you commit to a season."),
 "ctaHref": "quote.html?product=Bingsu%20Beads%20and%20Slime%20Fillers",
 "ctaLabel": "Request a slime filler quote",
 "faq": [
   ("What are bingsu beads made of?",
    "Our stock bingsu is PET — resin identification code 1, and practically insoluble in water, which is why the strands keep "
    "their shape in a wet slime base instead of softening. They are soft and very light, giving a fine crunch without weight."),
   ("How many jars does 500g of bingsu beads make?",
    "It depends entirely on your dosing, so measure rather than guess: weigh the filler in one finished jar at the density you "
    "like, then divide 500 by that figure. Because bingsu is light, 500g goes considerably further than a dense filler."),
   ("Will iridescent fillers bleed colour into pale slime?",
    "It can happen, and usually shows up after days rather than immediately. Test a pinch in your palest base, sealed and kept "
    "warm, checking at 24 hours and again at a week. Test per batch, not per supplier, because pigment lots change."),
   ("Are clay sprinkles a filler or a topping?",
    "A topping. Polymer clay is a PVC-based material cured at around 129 to 135 °C, so it arrives as a fully cured solid that "
    "holds printed detail — that detail is only worth paying for where buyers can see it, on the surface."),
 ],
 "related": [
   ("glitter-sequins-fillers.html", "Glitter, sequins &amp; fillers", "The full stock range including bingsu, hollow stars and holographic paillettes."),
   ("guide-clay-slices-vs-resin-charms-slime.html", "Clay slices vs resin charms", "Which topping to use where, and the 70/30 sourcing split."),
   ("guide-slime-business-supply-checklist.html", "Slime business supply checklist", "The full add-in list a new slime shop actually needs."),
 ],
},

# ─────────────────────────────────────────────────────────────
{
 "slug": "guide-decoden-supplies.html",
 "title": "Decoden Supplies: What Actually Goes on a Phone Case",
 "desc": "A sourcing guide to decoden charms: flatback vs 3D pieces, the size mix that makes a case look finished, why batch detail drifts, and how to buy a starter range from one bag.",
 "crumb": "Decoden Supplies",
 "eyebrow": "Sourcing Guide",
 "h1": "Decoden Supplies: What Actually Goes on a Phone Case",
 "updated": "July 2026",
 "hero": "assets/images/real-life-scenes-v1/real-life-decoden-collection.webp",
 "heroW": 1200, "heroH": 1200,
 "heroAlt": "Decoden phone cases decorated with resin flatback charms, bows and cabochons",
 "heroCap": "A finished decoden case reads as one composition — not as a pile of charms.",
 "answer": ("<b>Short answer:</b> decoden needs <b>flatback</b> pieces that glue flush, in a deliberate mix of sizes — a few "
            "large focal pieces, more mid-size, and a scatter of small fillers. Our resin charm line runs <b>19 stock designs</b> "
            "from about <b>12&nbsp;mm to 36&nbsp;mm</b>, mostly <b>100pcs per bag from one bag</b>, so a starter range costs a few "
            "bags rather than a bulk commitment."),
 "bodyHtml": f"""
  <h2>1. Flatback is the requirement, not a preference</h2>
  <p>Decoden works by gluing pieces onto a curved surface, usually over a whipped-cream base. A piece with a flat reverse side
  sits flush and bonds across its whole footprint. A rounded or 3D piece touches the glue at one point, sticks out, and is the
  first thing to catch on a pocket and pop off.</p>
  <p>That is why the useful phrase when sourcing is <b>&ldquo;flatback cabochon&rdquo;</b> rather than &ldquo;charm&rdquo;.
  Charm often implies a drilled hole and a jump ring — useful for keychains, wrong for a case. Our resin line is described as
  flatback for exactly this reason, and the pieces that are drilled are listed separately for jewellery and keychain use.</p>

  <h2>2. The size mix that makes a case look finished</h2>
  <p>Beginners buy one size and wonder why the result looks like a sticker sheet. A case that reads as a composition uses three
  tiers, and our stock sizes map onto them:</p>
  <table class="spec-table matrix">
    <tr><th>Tier</th><th>Rough size</th><th>Count per case</th><th>Job</th></tr>
    <tr><td><b>Focal</b></td><td>~30&ndash;36&nbsp;mm</td><td>1&ndash;3</td><td>The piece the eye lands on; sets the theme</td></tr>
    <tr><td><b>Mid</b></td><td>~18&ndash;25&nbsp;mm</td><td>5&ndash;10</td><td>Carries the theme around the focal piece</td></tr>
    <tr><td><b>Filler</b></td><td>~12&nbsp;mm and under</td><td>20&ndash;40</td><td>Closes gaps so no base shows through</td></tr>
  </table>
  <p>Filler pieces are where most of the count goes, which is exactly why 100pcs bags suit this craft — one bag of small
  pieces covers many cases, while you only need a handful of focal pieces per design.</p>

  <h2>3. Why detail drifts between batches — and what to do</h2>
  <p>Cast resin is the right process for these shapes, but it has a physical limit worth understanding before you order at scale.
  Mixing the two parts <a href="{WIKI_RESIN}" target="_blank" rel="noopener">causes an exothermic reaction that generates heat</a>,
  and that heat plus the casting compounds gradually degrade the mould —
  <a href="{WIKI_RESIN}" target="_blank" rel="noopener">a flexible mould typically yields between 25 and 100 castings</a> before
  fine detail softens.</p>
  <p>Practical consequences:</p>
  <ul>
    <li><b>Judge highly detailed designs from a current-batch sample</b>, not from a listing photo that may have been shot from
    the first pull off a fresh mould.</li>
    <li><b>Expect minor variation on reorders</b> of intricate pieces. On simple geometric shapes it is negligible; on a
    detailed animal face it is visible if you line up two batches.</li>
    <li><b>Custom shapes are quoted per project</b> because a bespoke design means new tooling that wears out — it is not an
    artwork fee.</li>
  </ul>

  <h2>4. Resin or clay on a case?</h2>
  <p>Both materials turn up in decoden supplies and they are not interchangeable. Polymer clay is
  <a href="{WIKI_CLAY}" target="_blank" rel="noopener">PVC-based and cured at around 129&ndash;135&nbsp;°C</a>, which is why clay
  slices arrive as fully hardened pieces with the pattern running right through them. Cast resin takes finer moulded detail
  and a glossier finish.</p>
  <p>On a phone case the practical split is: <b>resin for the focal and mid pieces</b> where moulded detail is the selling
  point, and <b>clay slices for scatter and gap-filling</b> where you want pattern and colour without paying for detail nobody
  will look at closely. Mixing both is normal — most finished cases in our reference photos use resin shapes over a clay-slice
  confetti layer.</p>

  <h2>5. What sells, by buyer</h2>
  <p>Decoden buyers split into three groups, and they want different things from the same catalogue. Kawaii food pieces —
  jelly beans, strawberries, cookies, cake slices — are the steady sellers for case makers. Ocean and animal sets (crabs,
  starfish, dolphins, frogs) move for kids' channels and summer ranges. Seasonal shapes carry a short, sharp window: order
  Christmas pieces a season early, because a decoden case takes hours to build and sellers buy the supplies long before the
  gift rush.</p>
  <p>One useful note for kids' channels: everything here is decorative and non-edible, and must be labelled that way. If you
  sell into retailers that ask for paperwork, batch test reports for EN&nbsp;71, ASTM&nbsp;F963, CPC and REACH are available on
  request — our <a href="guide-non-food-safety-labeling.html">safety labeling guide</a> covers the wording that keeps you out
  of trouble.</p>

  <h2>6. A starter range in one order</h2>
  <p>You can build a working decoden range without a bulk commitment. Sixteen of our 19 resin designs have a one-bag minimum
  (three are two bags), and most pack 100pcs. A sensible first order is:</p>
  <ul>
    <li><b>1&ndash;2 focal designs</b> in the 30&nbsp;mm-plus band, matched to one theme;</li>
    <li><b>2&ndash;3 mid-size designs</b> that carry the same theme;</li>
    <li><b>1&ndash;2 small filler designs</b> — these get used fastest, so buy the deepest here;</li>
    <li>plus whipped-cream base and glue from your local supplier, which are cheaper to source domestically than to freight.</li>
  </ul>
  <p>That is five to seven bags. It photographs as a coherent range, it leaves budget to reorder the fillers you burn through,
  and it tells you which theme to go deep on before you spend on bulk.</p>
 """,
 "note": ("<b>Sourcing shorthand:</b> say &ldquo;flatback cabochon, no drill hole&rdquo; for decoden and &ldquo;drilled charm&rdquo; "
          "for keychains. The same design often exists both ways, and the wrong one is unusable on a case."),
 "ctaH2": "Get a decoden starter range quoted",
 "ctaP": ("Send the theme and roughly how many cases per month. We put together a focal / mid / filler mix from stock, quote by "
          "the bag with carton data, and can send current-batch samples on the detailed pieces before you commit."),
 "ctaHref": "quote.html?product=Decoden%20Resin%20Charms",
 "ctaLabel": "Request a decoden supply quote",
 "faq": [
   ("What is the difference between a flatback cabochon and a charm?",
    "A flatback cabochon has a flat reverse side and glues flush to a surface — that is what decoden needs. A charm usually has "
    "a drilled hole and a jump ring for keychains and jewellery. The same design often exists in both versions, so specify which."),
   ("How many pieces does one phone case take?",
    "A case that looks finished normally uses one to three focal pieces around 30 to 36 mm, five to ten mid-size pieces, and "
    "twenty to forty small fillers under about 12 mm. Filler pieces are consumed fastest, so buy deepest there."),
   ("Why do detailed resin pieces vary slightly between orders?",
    "Resin curing is exothermic, and that heat plus the casting compounds gradually degrade the mould — a flexible mould yields "
    "roughly 25 to 100 castings before fine detail softens. On simple shapes it is negligible; on intricate designs, judge from a "
    "current-batch sample rather than a listing photo."),
   ("Can I order a decoden starter range without buying bulk?",
    "Yes. Sixteen of the 19 stock resin designs have a one-bag minimum and most pack 100pcs, so a focal / mid / filler range is "
    "typically five to seven bags — enough to photograph as a collection and find out which theme to scale."),
 ],
 "related": [
   ("resin-charms.html", "Resin charms &amp; flatback cabochons", "The full stock range with sizes, pack counts and per-SKU quoting."),
   ("guide-non-food-safety-labeling.html", "Non-food safety labeling", "The wording kids' channels ask for, with copy-paste templates."),
   ("applications.html", "Applications by buyer type", "Where each line fits — decoden, nail art, jewellery, slime, party."),
 ],
},

]
