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
{
 "slug": "guide-beadable-pen-beads.html",
 "title": "Beadable Pen Beads: Hole Size, Lots and What Actually Sells",
 "desc": "How to buy focal beads for beadable pens in bulk: vertical-hole vs side-hole, the 100pcs lot standard, size ranges that fit standard pen blanks, and how to build a theme range.",
 "crumb": "Beadable Pen Beads",
 "eyebrow": "Sourcing Guide",
 "h1": "Beadable Pen Beads: Hole Size, Lots and What Actually Sells",
 "updated": "July 2026",
 "hero": "assets/images/real-life-scenes-v1/real-life-beadable-pen-gift.webp",
 "heroW": 1200, "heroH": 1200,
 "heroAlt": "Finished beadable pens with cartoon resin focal beads and spacer beads",
 "heroCap": "Finished beadable pens — focal bead, spacers and a standard pen blank.",
 "answer": ("<b>Short answer:</b> beadable pen beads are resin focal beads with a hole wide enough to slide onto a "
            "standard pen blank. Our line runs <b>22 stock designs</b>, almost all packed <b>100pcs per bag</b> with a "
            "<b>1-bag minimum</b>, in sizes from roughly <b>12&nbsp;mm up to 37&nbsp;mm</b>. Buy by theme, not by single "
            "design — a pen needs one focal bead plus spacers, so a seller who stocks 6&ndash;8 themes outsells one who "
            "stocks 30 random shapes."),
 "bodyHtml": f"""
  <h2>1. The hole is the spec that decides everything</h2>
  <p>Nothing else matters if the bead will not go on the blank. Two things go wrong in practice: the hole is too narrow
  for the pen barrel, or the hole runs the wrong way through the bead. Both look identical in a photo.</p>
  <p><b>Vertical hole</b> (through the top and bottom) is what a beadable pen needs — the bead sits upright and faces
  the user. <b>Side hole</b> beads are for bracelets and phone chains; put one on a pen and the design lies sideways.
  Several of our stock designs are explicitly listed as vertical-hole for this reason, and a handful are dual-purpose.
  When you request a quote, say <em>&ldquo;for pens&rdquo;</em> and we confirm the hole direction per SKU before you pay.</p>
  <p>Ask for the hole diameter in millimetres, not &ldquo;large hole&rdquo;. Pen blanks vary by supplier, so the safe
  move on a first order is to post us one blank, or a photo with a ruler against the barrel.</p>

  <h2>2. Sizes: what a 12&nbsp;mm bead and a 37&nbsp;mm bead each do</h2>
  <table class="spec-table matrix">
    <tr><th>Size band (from our stock line)</th><th>Role on the pen</th><th>Typical use</th></tr>
    <tr><td><b>~12&ndash;15&nbsp;mm</b></td><td>Spacer / accent</td><td>Sits either side of the focal bead; keeps the barrel balanced</td></tr>
    <tr><td><b>~20&ndash;25&nbsp;mm</b></td><td>Everyday focal</td><td>The workhorse size — visible in a photo, still comfortable to hold</td></tr>
    <tr><td><b>~30&ndash;37&nbsp;mm</b></td><td>Statement focal</td><td>Gift and novelty pens; photographs well but adds weight at the top</td></tr>
  </table>
  <p>Our stock designs land across this whole band — for example a 15&times;20&nbsp;mm candy-corn bead, a 20&times;12&nbsp;mm
  cat bead, a 23&nbsp;mm curly-dog bead and a 25&times;37&nbsp;mm swan. If you are building a first range, weight it toward
  the middle band and add statement pieces only for seasonal gifting.</p>

  <h2>3. The 100pcs lot, and why it is the right unit</h2>
  <p>Nineteen of our 22 designs pack <b>100pcs per bag</b>, and the minimum is <b>one bag</b>. That is deliberate: a bag
  of 100 focal beads is roughly 100 finished pens, which is a realistic first production run for a market stall, an Etsy
  shop or a school fundraiser. It is small enough to test a theme and large enough that the per-unit freight stops hurting.</p>
  <p>Do the arithmetic before you commit to a design. If a bag lands at, say, <b>$3&ndash;$7 per 100pcs</b> depending on
  design and quantity band, your bead cost per pen is a few cents — the blank, the packaging and your labour will each cost
  more than the bead. That is why buying <em>the right</em> design matters more than shaving the bead price.</p>

  <h2>4. Resin, and the one physical limit worth knowing</h2>
  <p>Twenty-one of the 22 designs are cast resin. Resin casting is well suited to exactly this kind of product —
  it is used for <a href="{WIKI_RESIN}" target="_blank" rel="noopener">small-scale production of collectible toys, models
  and figures</a>, which is essentially what a novelty focal bead is.</p>
  <p>The limit to know: mixing the two resin parts causes an exothermic reaction, and the heat plus the aggressive
  compounds degrade the mould over time — <a href="{WIKI_RESIN}" target="_blank" rel="noopener">a flexible mould typically
  yields between 25 and 100 castings</a> before it starts losing fine detail. Two practical consequences for you:</p>
  <ul>
    <li><b>Custom shapes carry a real tooling cost.</b> A new design is not just artwork — it is a mould that wears out. That
    is why bespoke shapes are quoted per project while stock designs ship from one bag.</li>
    <li><b>Fine detail drifts slightly between batches.</b> On highly detailed designs, ask for a current-batch sample rather
    than relying on a listing photo shot from an early mould.</li>
  </ul>

  <h2>5. Resin or clay? They fail differently</h2>
  <p>Not every bead on the market is resin. The other common material is polymer clay, which is
  <a href="{WIKI_CLAY}" target="_blank" rel="noopener">a PVC-based modelling material cured at roughly
  129&ndash;135&nbsp;°C</a>. Both arrive as hard, finished pieces, but they behave differently once a customer is using the pen:</p>
  <ul>
    <li><b>Cast resin</b> takes sharper moulded detail and a glossier finish — better for faces, eyes and lettering.</li>
    <li><b>Polymer clay</b> pieces are usually built from canes, so patterns run through the body of the bead rather than
    sitting on the surface. Scuff a clay bead and the pattern is still there; scuff a painted resin bead and it shows.</li>
  </ul>
  <p>For pens, where the bead is handled constantly, we stock resin for detail-led designs and treat clay as a pattern option.
  If a customer complains about wear, that distinction is usually the reason.</p>

  <h2>6. Build a theme, not a catalogue</h2>
  <p>The sellers who reorder fastest do not stock the most designs. They pick a lane and go deep enough that a customer can
  buy a matching set: animals, desserts, Christmas, ocean. Our stock line already clusters that way — cartoon bears, dogs,
  cats and corgis; cookies, cakes, chocolate and candy corn; starfish and ocean animals; penguins, trees and gift boxes for
  the holiday range.</p>
  <p>A workable first order is <b>4&ndash;6 focal designs inside one theme plus one neutral spacer design</b>. That is five
  to seven bags, it photographs as a collection rather than a jumble, and it leaves budget to reorder whatever sells through
  first instead of sitting on 20 slow designs.</p>
 """,
 "note": ("<b>Before you order:</b> confirm hole direction (vertical for pens), send a photo of your pen blank with a ruler, "
          "and ask for a current-batch sample on any design where fine detail is the selling point."),
 "ctaH2": "Get a quote with the pen spec filled in",
 "ctaP": ("Tell us the theme, how many designs, and the blank you use. We confirm hole direction per SKU, quote by the bag, "
          "and come back with carton data so you can compare freight — first reply within three working hours."),
 "ctaHref": "quote.html?product=Beads%20for%20Pens",
 "ctaLabel": "Request a beadable pen bead quote",
 "faq": [
   ("Do beadable pen beads have a vertical or side hole?",
    "For pens you need a vertical hole so the design faces the user; side-hole beads are meant for bracelets and phone chains. "
    "Several of our stock designs are listed specifically as vertical-hole, and we confirm hole direction per SKU before you pay."),
   ("What is the minimum order for pen beads?",
    "One bag. Nineteen of the 22 stock designs pack 100pcs per bag, which is roughly 100 finished pens — small enough to test a "
    "theme, large enough that per-unit freight stops hurting."),
   ("Can you make a custom bead shape?",
    "Yes, but it is quoted per project rather than from stock, because a new shape means a new mould. Flexible moulds yield "
    "roughly 25 to 100 castings before fine detail degrades, so tooling is a real cost line rather than a one-off artwork fee."),
   ("What bead size should a first range use?",
    "Weight it toward the 20 to 25 mm band — visible in listing photos but still comfortable to hold. Add 30 mm-plus statement "
    "beads only for gift and seasonal lines, and keep a small spacer design in stock to balance the barrel."),
 ],
 "related": [
   ("beads-for-pens.html", "Beads for Pens — full stock range", "All 22 stock designs with photos, pack sizes and per-SKU quoting."),
   ("guide-private-label-collection.html", "Build a private label collection", "How to turn a stock range into your own branded line without going wide."),
   ("guide-craft-supply-packaging.html", "Bags vs bottles vs jars", "Which pack format makes a 100pcs lot look retail-ready."),
 ],
},

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
