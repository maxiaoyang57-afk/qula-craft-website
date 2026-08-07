# -*- coding: utf-8 -*-
"""交易信任簇 3 篇。填 Reddit 实证的最高频痛点(supplier 39/alibaba 33/customs 25/import 23/duty 9)。
铁律:关税税率、付款条款这类会变或需客户确认的,一律不写死 —— 给方法与官方查询入口。
"""
ICC = "https://iccwbo.org/business-solutions/incoterms-rules/"
HS = "https://www.trade.gov/harmonized-system-hs-codes"
WIKI_RESIN = "https://en.wikipedia.org/wiki/Resin_casting"
WIKI_CLAY = "https://en.wikipedia.org/wiki/Polymer_clay"

GUIDES = [

# ─────────────────────────────────────────────────────────────
{
 "slug": "guide-paying-a-craft-supplier.html",
 "title": "Paying a Craft Supplies Supplier: Terms, Stages and Red Flags",
 "desc": "How payment actually works on a craft supply order: what the deposit covers, why Incoterms decide who pays what, the checks that protect a first order, and the warning signs worth walking away from.",
 "crumb": "Paying a Supplier",
 "eyebrow": "Trade Guide",
 "h1": "Paying a Craft Supplies Supplier: Terms, Stages and Red Flags",
 "updated": "July 2026",
 "hero": "assets/images/real-life-scenes-v1/real-life-multi-category.webp",
 "heroW": 1200, "heroH": 1200,
 "heroAlt": "Assorted craft supply stock ready for packing and export",
 "heroCap": "Every order runs through the same stages — the terms decide who carries risk at each one.",
 "answer": ("<b>Short answer:</b> a craft supply order normally moves in stages — quotation, proforma invoice, deposit, "
            "production, balance before or against shipping documents. What you pay <em>for</em> at each stage depends on the "
            "Incoterms rule on the invoice, not on goodwill. Get the proforma invoice right and most payment disputes never happen."),
 "bodyHtml": f"""
  <h2>1. The proforma invoice is the contract</h2>
  <p>Before money moves, you should be holding a proforma invoice that states product, quantity, pack format, unit price,
  lead time and shipping terms. If any of those five is missing, that is where the argument will start later.</p>
  <p>The most commonly skipped line is <b>pack format</b>. &ldquo;100pcs&rdquo; and &ldquo;100pcs in a labelled retail bag&rdquo;
  are different products with different costs. Craft supplies are light but bulky, so packaging drives both your freight bill
  and your shelf presentation — pin it down in writing.</p>

  <h2>2. Incoterms decide who pays for what</h2>
  <p>The three letters after the price are not decoration. The
  <a href="{ICC}" target="_blank" rel="noopener">Incoterms&reg; rules were first published by the International Chamber of
  Commerce in 1936, with Incoterms&reg; 2020 in force since 1 January 2020</a>, and they define exactly where the seller's
  responsibility ends and yours begins.</p>
  <p>For small craft supply orders you will mostly meet these:</p>
  <table class="spec-table matrix">
    <tr><th>Term</th><th>Seller covers</th><th>You cover</th><th>When it suits you</th></tr>
    <tr><td><b>EXW</b></td><td>Goods ready at the workshop</td><td>Everything from the door onward</td><td>You already have a freight forwarder in China</td></tr>
    <tr><td><b>FOB</b></td><td>Goods cleared and loaded at the port of origin</td><td>Sea freight, insurance, import clearance, duty</td><td>The common default once volumes justify sea freight</td></tr>
    <tr><td><b>DDP</b></td><td>Everything to your door, duties included</td><td>Nothing further</td><td>First orders and small parcels, when you want one number</td></tr>
  </table>
  <p>A quote is not comparable across suppliers until you know the term. A cheaper EXW price can easily land dearer than a
  higher DDP price once freight and clearance are added — which is the whole point of working out
  <a href="guide-importing-craft-supplies.html">landed cost</a> rather than unit cost.</p>

  <h2>3. Deposit, balance, and what the deposit is really for</h2>
  <p>A deposit is not a gesture of trust; it funds materials and reserves production time. For stock items the gap between
  deposit and shipment can be short. For custom work it covers tooling — and tooling is a genuine cost, because
  <a href="{WIKI_RESIN}" target="_blank" rel="noopener">a flexible mould only yields roughly 25 to 100 castings</a> before it
  loses fine detail, so a bespoke shape means real hardware that wears out, not just a drawing.</p>
  <p>Two questions worth asking before you send anything:</p>
  <ul>
    <li><b>What exactly does the deposit release?</b> Materials purchase, mould cutting, or line time — the answer tells you
    how much work is genuinely underway.</li>
    <li><b>What happens to the balance if the pre-production sample is rejected?</b> Agree this <em>before</em> production,
    not after.</li>
  </ul>

  <h2>4. Red flags worth walking away from</h2>
  <p>These come up repeatedly in importer forums, and they are cheap to check:</p>
  <ul>
    <li><b>Bank details that do not match the company on the invoice.</b> A payment redirected to a personal account or a
    third-country entity is the single most common loss. Confirm any change of banking details by voice, not by email.</li>
    <li><b>Pressure to skip the sample.</b> A supplier confident in the goods wants you to see them.</li>
    <li><b>A price far below every other quote.</b> On craft supplies the material cost is real; an outlier usually means a
    different specification, not a better deal.</li>
    <li><b>Vague answers on pack format and carton dimensions.</b> A factory that packs these lines weekly knows its carton
    sizes without checking.</li>
    <li><b>No willingness to put the specification in writing.</b> If it is not on the proforma invoice, it is not agreed.</li>
  </ul>

  <h2>5. How we handle it</h2>
  <p>We work from a proforma invoice that lists product, quantity, pack format, price, lead time and shipping terms, so both
  sides are agreeing to the same thing before money moves. Stock orders start at one bag, which means a first order can be
  small enough to verify us cheaply rather than requiring a leap of faith.</p>
  <p class="small-note"><b>Payment methods and deposit percentages are confirmed per order</b> — tell us your preferred method
  and destination market in the enquiry, and our sales team will confirm in writing what works for your bank and your order
  size before you commit.</p>
 """,
 "note": ("<b>The one habit that prevents most disputes:</b> never accept a change of bank details by email alone. Confirm it "
          "by a voice call to a number you already had, before any transfer."),
 "ctaH2": "Get a quotation with the terms spelled out",
 "ctaP": ("Send product, quantity, pack format and destination. You get a written quotation with lead time, shipping terms and "
          "carton data — first reply within three working hours, full quotation typically within 12&ndash;24 hours."),
 "ctaHref": "quote.html",
 "ctaLabel": "Request a written quotation",
 "faq": [
   ("What should be on the invoice before I pay a deposit?",
    "Product, quantity, pack format, unit price, lead time and shipping terms. Pack format is the line most often skipped and "
    "the one most likely to cause a dispute — 100pcs loose and 100pcs in a labelled retail bag are different products."),
   ("Why does the Incoterms rule matter for a small order?",
    "It defines where the seller's responsibility ends and yours begins. The ICC first published the Incoterms rules in 1936 and "
    "Incoterms 2020 has been in force since 1 January 2020. A cheaper EXW price can land dearer than a higher DDP price once "
    "freight, clearance and duty are added, so quotes are not comparable until you know the term."),
   ("What is a deposit actually paying for?",
    "Materials and reserved production time — and on custom work, tooling. A bespoke resin shape needs a new mould, and a "
    "flexible mould only yields roughly 25 to 100 castings before fine detail degrades, so tooling is real hardware rather than "
    "a one-off design fee."),
   ("What is the most common way importers lose money?",
    "A payment redirected to bank details that do not match the company on the invoice. Never accept a change of banking details "
    "by email alone — confirm by voice on a number you already had."),
 ],
 "related": [
   ("guide-importing-craft-supplies.html", "Importing craft supplies", "HS codes, landed cost and who clears the goods."),
   ("guide-samples-and-inspection.html", "Samples and inspection", "What to check before you release the balance."),
   ("quote.html", "Request a quotation", "Product, quantity, pack format and destination — we reply within three working hours."),
 ],
},

# ─────────────────────────────────────────────────────────────
{
 "slug": "guide-importing-craft-supplies.html",
 "title": "Importing Craft Supplies: HS Codes, Duty and Landed Cost",
 "desc": "How to work out what a craft supply order really costs to land: how HS classification works, where to look up your own duty rate, why volumetric weight matters more than actual weight, and who clears the goods.",
 "crumb": "Importing Craft Supplies",
 "eyebrow": "Trade Guide",
 "h1": "Importing Craft Supplies: HS Codes, Duty and Landed Cost",
 "updated": "July 2026",
 "hero": "assets/images/real-life-scenes-v1/real-life-multi-category-components.webp",
 "heroW": 1200, "heroH": 1200,
 "heroAlt": "Craft supply components sorted for packing and export",
 "heroCap": "Light but bulky — craft supplies are usually charged on volume, not weight.",
 "answer": ("<b>Short answer:</b> landed cost = goods + freight + insurance + duty + clearance fees + any local tax. The duty "
            "rate depends on your product's HS classification and your own country's tariff schedule, so nobody can quote you a "
            "single universal figure — but you can look yours up in a few minutes, and we supply the carton data you need to get "
            "a real freight number."),
 "bodyHtml": f"""
  <h2>1. Landed cost, not unit price</h2>
  <p>The number that decides whether your margin works is not the price per bag. It is:</p>
  <div class="guide-note" style="margin:14px 0"><b>Landed cost = goods + freight + insurance + duty + customs clearance fees
  + any local sales tax or VAT</b></div>
  <p>Two quotes can only be compared once both are converted to this figure. That is also why the Incoterms rule on the
  invoice matters so much —
  <a href="{ICC}" target="_blank" rel="noopener">the ICC's Incoterms&reg; rules define which of those cost lines the seller
  already covered</a> and which are still coming toward you.</p>

  <h2>2. HS codes: how classification works</h2>
  <p>Every traded product is classified under the Harmonized System.
  <a href="{HS}" target="_blank" rel="noopener">The US International Trade Administration explains that the HS assigns
  six-digit codes internationally, which the United States extends to ten digits</a> for imports. Other countries extend it to
  eight or ten digits of their own.</p>
  <p>Practical implications for craft supplies:</p>
  <ul>
    <li><b>The first six digits are the same worldwide;</b> the last digits are national. So a code from a Chinese supplier gets
    you to the right chapter but not necessarily to your national tariff line.</li>
    <li><b>Material and function both matter.</b> A plastic bead, a resin ornament and a printed paper label can sit in
    different chapters even inside one carton.</li>
    <li><b>Classification is the importer's responsibility</b> in most jurisdictions, which is why it is worth confirming with
    your own broker rather than accepting a supplier's code unchecked.</li>
  </ul>
  <p>We can tell you what the goods physically are — material, composition, pack format — which is exactly what a broker needs
  to classify them correctly. We do not guess at your national tariff line, because getting that wrong is your risk, not ours.</p>

  <h2>3. Look up your own duty rate</h2>
  <p>Duty rates change, and they differ by country, by trade agreement and sometimes by month. Any guide that prints a
  percentage will be wrong eventually — so use the official sources instead:</p>
  <ul>
    <li><b>United States</b> — the Harmonized Tariff Schedule is searchable online, and the
    <a href="{HS}" target="_blank" rel="noopener">ITA's HS code overview</a> explains how the ten-digit US extension works.</li>
    <li><b>European Union, United Kingdom, Australia, Canada</b> — each publishes its own online tariff lookup; search for the
    national customs authority plus &ldquo;tariff lookup&rdquo;.</li>
    <li><b>Anywhere</b> — a licensed customs broker will classify and quote duty for a modest fee, which is cheap next to a
    misclassification penalty.</li>
  </ul>
  <p class="small-note">Check the rate yourself close to shipment date rather than relying on a figure quoted months earlier.</p>

  <h2>4. Volumetric weight is what actually bills you</h2>
  <p>This is where craft supply importers get surprised. A bag of foam-light filler weighs almost nothing but fills a carton.
  Air freight and courier services bill on <b>volumetric weight</b> — a formula based on carton dimensions — whenever that
  exceeds actual weight, which for these products it usually does.</p>
  <p>So the useful question to your supplier is not &ldquo;how heavy is it?&rdquo; but <b>&ldquo;what are the carton dimensions
  and how many bags per carton?&rdquo;</b> With that you can get a real quote from a forwarder instead of an estimate. We
  include carton data with every quotation for exactly this reason.</p>
  <p>Two consequences worth planning around: consolidating several stock lines into one shipment usually beats several small
  parcels, and compressible pack formats (bags rather than rigid jars) can meaningfully cut the volumetric bill.</p>

  <h2>5. Who clears the goods</h2>
  <p>Under DDP the seller handles clearance and duty, which is why it suits first orders — you get one number and no paperwork.
  Under FOB or EXW you or your broker clear the goods, and you will need the commercial invoice, packing list and, depending on
  the destination and product, any applicable compliance paperwork.</p>
  <p>For craft supplies sold into children's channels, retailers commonly ask for batch test reports such as EN&nbsp;71,
  ASTM&nbsp;F963, CPC or REACH. Those are supplied on request — see our
  <a href="guide-non-food-safety-labeling.html">non-food safety labeling guide</a> for how the wording works on the retail pack.</p>
 """,
 "note": ("<b>Ask for carton dimensions, not just weight.</b> Craft supplies are light and bulky, so air and courier shipments "
          "almost always bill on volumetric weight — carton size is the number that decides your freight bill."),
 "ctaH2": "Get a quote with carton data attached",
 "ctaP": ("Tell us the products, quantities and destination country. The quotation comes back with pack format and carton "
          "dimensions so you can price freight and duty properly before you commit."),
 "ctaHref": "quote.html",
 "ctaLabel": "Request a quote with carton data",
 "faq": [
   ("What is landed cost?",
    "Goods plus freight, insurance, duty, customs clearance fees and any local sales tax or VAT. Unit price alone cannot be "
    "compared across suppliers — a cheaper EXW price often lands dearer than a higher DDP price once everything is added."),
   ("Can you tell me my duty rate?",
    "No, and be wary of any supplier who does. Duty depends on your national tariff line and current trade policy. We describe "
    "what the goods physically are — material, composition, pack format — which is what your broker needs to classify them. "
    "Classification is the importer's responsibility in most jurisdictions."),
   ("How many digits is an HS code?",
    "Six digits are the international standard; the United States extends this to ten digits for imports, and other countries "
    "extend to eight or ten of their own. A supplier's code gets you to the right chapter but not necessarily to your national line."),
   ("Why is freight quoted on volume rather than weight?",
    "Craft supplies are light but bulky, so volumetric weight — calculated from carton dimensions — usually exceeds actual "
    "weight, and carriers bill on whichever is higher. Ask for carton dimensions and units per carton, not just kilos."),
 ],
 "related": [
   ("guide-paying-a-craft-supplier.html", "Paying a supplier", "Proforma invoices, deposits, Incoterms and red flags."),
   ("guide-craft-supply-packaging.html", "Bags vs bottles vs jars", "Pack format drives both shelf presentation and your freight bill."),
   ("guide-samples-and-inspection.html", "Samples and inspection", "What to check before the balance goes out."),
 ],
},

# ─────────────────────────────────────────────────────────────
{
 "slug": "guide-samples-and-inspection.html",
 "title": "Samples and Inspection: What to Check Before You Pay the Balance",
 "desc": "The three kinds of sample, what each one proves, a five-point inspection list for craft supplies, and why batch variation on detailed resin pieces is physics rather than carelessness.",
 "crumb": "Samples &amp; Inspection",
 "eyebrow": "Trade Guide",
 "h1": "Samples and Inspection: What to Check Before You Pay the Balance",
 "updated": "July 2026",
 "hero": "assets/images/real-life-scenes-v1/real-life-multi-category-components-no-box.webp",
 "heroW": 1200, "heroH": 1200,
 "heroAlt": "Craft supply samples laid out for inspection before bulk production",
 "heroCap": "A sample only proves what you asked it to prove — decide that before you request one.",
 "answer": ("<b>Short answer:</b> there are three kinds of sample and they prove different things — a stock sample proves "
            "quality, a colour-matched sample proves your palette, a pre-production sample proves the actual production run. "
            "Check colourfastness, size consistency, hole and back finish, pack format and count before releasing the balance."),
 "bodyHtml": f"""
  <h2>1. Three kinds of sample, three different jobs</h2>
  <table class="spec-table matrix">
    <tr><th>Sample type</th><th>What it proves</th><th>When to ask</th></tr>
    <tr><td><b>Stock sample</b></td><td>Real material, finish and size of an existing line</td><td>Before a first order from a new supplier</td></tr>
    <tr><td><b>Colour / mix sample</b></td><td>Your palette or ratio, on an existing shape</td><td>When you are customising a stock design</td></tr>
    <tr><td><b>Pre-production sample</b></td><td>The actual run, from the actual mould, in the actual pack</td><td>Always, on custom work, before mass production</td></tr>
  </table>
  <p>Confusing the first and the third is a classic and expensive mistake. A stock sample tells you the factory can make good
  goods. Only a pre-production sample tells you <em>your</em> goods are right.</p>

  <h2>2. The five checks that matter for craft supplies</h2>
  <ol>
    <li><b>Colourfastness.</b> Put a pinch into your palest base or resin, seal it, leave it somewhere warm and check at 24
    hours and again at a week. Bleed rarely shows on day one — it shows after the batch has shipped.</li>
    <li><b>Size consistency across the bag</b>, not just the top layer. Pour some out, measure a handful from the middle.
    Nominal sizes are nominal.</li>
    <li><b>Hole and reverse-side finish.</b> For pen beads, confirm hole direction and that it is clear of flash. For flatback
    pieces, confirm the back is genuinely flat and clean enough to glue.</li>
    <li><b>Pack format and count.</b> Weigh or count one bag against the spec. If you are reselling the bag as retail, check the
    seal and print now, not after 500 arrive.</li>
    <li><b>Smell and residue.</b> A strong chemical smell on arrival usually means insufficient curing time. It is a legitimate
    reason to hold a batch.</li>
  </ol>

  <h2>3. Batch variation on detailed pieces is physics</h2>
  <p>On highly detailed resin designs you may notice small differences between orders. That is not necessarily carelessness.
  Mixing the two resin components <a href="{WIKI_RESIN}" target="_blank" rel="noopener">causes an exothermic reaction that
  generates heat</a>, and that heat plus the casting compounds degrades the mould —
  <a href="{WIKI_RESIN}" target="_blank" rel="noopener">a flexible mould typically yields between 25 and 100 castings</a>
  before it starts losing fine detail.</p>
  <p>What to do with that knowledge:</p>
  <ul>
    <li>Judge intricate designs from a <b>current-batch</b> sample, not from a listing photo that may have been taken from an
    early pull.</li>
    <li>On reorders of detailed pieces, ask whether the run came from a fresh mould if crispness matters to your customer.</li>
    <li>Do not apply the same tolerance to clay slices — <a href="{WIKI_CLAY}" target="_blank" rel="noopener">polymer clay is
    PVC-based and cured at roughly 129&ndash;135&nbsp;°C</a> with patterns running through the cane, so its variation shows up
    as pattern and thickness rather than lost detail.</li>
  </ul>

  <h2>4. Inspecting without flying anywhere</h2>
  <p>For a first order at craft-supply values, a full third-party inspection often costs more than the goods. Cheaper checks
  that catch most problems:</p>
  <ul>
    <li><b>Photos of the packed cartons</b> before shipment — count, labels and carton condition.</li>
    <li><b>A short video of a bag being opened and poured out</b>, which catches size and colour spread far better than a
    styled photo.</li>
    <li><b>A retained sample</b> kept by you from the approved pre-production batch, so any later dispute is comparison rather
    than memory.</li>
  </ul>
  <p>Once your order values justify it, a third-party inspection at the factory before shipment is the standard next step.</p>

  <h2>5. What we do on our side</h2>
  <p>Stock samples ship quickly, and custom projects always include a pre-production sample so shape, colour, mix ratio and
  packaging are confirmed before mass production. Every quotation comes with carton data so you can check pack format against
  what arrives. Batch test reports for EN&nbsp;71, ASTM&nbsp;F963, CPC and REACH are available on request for buyers who need
  them for retail channels.</p>
  <p class="small-note">Sample fees and whether they are credited against a bulk order are confirmed per project — ask in the
  enquiry and it will be in writing on the quotation.</p>
 """,
 "note": ("<b>Keep a retained sample.</b> Put the approved pre-production sample in a labelled bag with the date and keep it. "
          "If a later batch is questioned, you are comparing two physical objects instead of arguing from memory."),
 "ctaH2": "Ask for a sample with the checks specified",
 "ctaP": ("Tell us which designs and what you need the sample to prove — colour match, size, pack format. Stock samples move "
          "quickly; custom projects always include a pre-production sample before mass production."),
 "ctaHref": "quote.html?product=Sample%20request",
 "ctaLabel": "Request samples",
 "faq": [
   ("What is the difference between a stock sample and a pre-production sample?",
    "A stock sample proves the factory can make good goods from an existing line. A pre-production sample proves your goods are "
    "right — actual mould, actual colours, actual pack. On custom work always insist on the second before mass production."),
   ("How do I test for colour bleed?",
    "Put a pinch of the material into your palest base or resin, seal it, keep it somewhere warm, and check at 24 hours and "
    "again at a week. Bleed usually does not show on day one, which is why it gets discovered after a batch has already shipped."),
   ("Why do detailed resin pieces vary slightly between batches?",
    "Resin curing is exothermic, and the heat plus the casting compounds gradually degrade the mould. A flexible mould typically "
    "yields 25 to 100 castings before fine detail softens, so judge intricate designs from a current-batch sample rather than an "
    "older listing photo."),
   ("Do I need a third-party inspection on a small craft supply order?",
    "Often it costs more than the goods. Photos of packed cartons, a short video of a bag being poured out, and a retained "
    "approved sample catch most problems at a first-order scale. Move to third-party inspection as order values grow."),
 ],
 "related": [
   ("guide-paying-a-craft-supplier.html", "Paying a supplier", "What the deposit covers and when the balance should move."),
   ("guide-importing-craft-supplies.html", "Importing craft supplies", "HS codes, duty and the landed-cost arithmetic."),
   ("guide-non-food-safety-labeling.html", "Non-food safety labeling", "The paperwork and wording retail buyers ask for."),
 ],
},

]
