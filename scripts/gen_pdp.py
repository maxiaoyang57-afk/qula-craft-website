# -*- coding: utf-8 -*-
"""PDP 生成器(价格口径=只上 From $ 起步价,Jacken 07-24 拍板)
产出:p-<assetKey>.html + 分类/季节页卡接链 + main.js 搜索卡接链 + sitemap + llms-full.txt
铁律:零编造——每个字段都来自 pdp-data.json(阿里实抓)或 catalog.json(客户Excel)"""
import json, re, statistics
from pathlib import Path
from PIL import Image

SITE = Path(__file__).resolve().parents[1]
TODAY = "2026-09-06"
BASE = "https://www.qulacrafts.com/"
pdp = json.loads((SITE / "assets/data/pdp-data.json").read_text(encoding="utf-8"))
for _e in pdp:
    _e["ci"] = _e["catalogIndex"] - 1  # Codex 台账是 1-based
catp = SITE / "assets/data/product-catalog.json"
cat = json.loads(catp.read_text(encoding="utf-8"))

CATPAGE = {"polymer-clay-slices": "polymer-clay-sprinkles.html", "plastic-beads": "acrylic-beads.html",
           "plastic-sequins": "glitter-sequins-fillers.html"}

def catpage(slug):
    return CATPAGE.get(slug, slug + ".html")

# ---- 0) catalogIndex 对齐校验 + catalog 注入 pdp 字段 ----
flat = []
for c in cat["categories"]:
    for p in c["products"]:
        flat.append(p)
assert len(flat) == len(pdp), f"catalog={len(flat)} pdp={len(pdp)}"
mis = [(e["ci"], e["sku"], flat[e["ci"]]["sku"]) for e in pdp
       if flat[e["ci"]]["sku"] != e["sku"]]
assert not mis, f"catalogIndex 错位: {mis[:5]}"
for e in pdp:
    flat[e["ci"]]["pdp"] = f"p-{e['assetKey']}.html"
catp.write_text(json.dumps(cat, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"catalog.json 注入 pdp 字段 ✓ ({len(flat)} 对齐)")

# ---- 标题清洗(与 main.js clean 同源) ----
ST = {"With", "And", "For", "Of", "The", "A", "An", "In", "On", "Per", "By", "To"}
def clean_title(t):
    t = (t or "").replace("Wight", "Weight").replace("Breads", "Beads").replace("Artfcal", "Artificial")
    w = t.split()
    while w and w[-1] in ST:
        w.pop()
    return " ".join(w)

def esc(s):
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")

def cut_words(s, n):
    out = ""
    for w in s.split():
        if len(out) + len(w) + 1 > n:
            break
        out = (out + " " + w).strip()
    return out or s[:n]

UNIT_OK = {"bag": "bag", "bags": "bag", "pc": "pc", "pcs": "pcs", "piece": "piece",
           "pieces": "pieces", "pair": "pair", "pairs": "pair", "set": "set", "sets": "set",
           "box": "box", "boxes": "box", "roll": "roll", "rolls": "roll"}
NOISE_CONST = {10.0, 20.0}          # 实测跨 60 个不相关 SKU 反复出现的页面固定元素值,非单价
BULK_UNITS = {"bag", "box", "set", "roll"}   # 整包单位,单价下限更高
def price_min(e):
    """起步价=与 MOQ 匹配的档,否则首档(listing 门面价)。部分 listing 阶梯混入噪声行
    (如 50 bags $0.04),取 min 会把假价上站,故不取最小值。单位仅白名单展示。"""
    tiers = []
    for t in e.get("priceTiers") or []:
        try:
            v = float(str(t.get("price", "")).replace(",", ""))
        except ValueError:
            continue
        tiers.append((v, (t.get("unit") or "").strip(), str(t.get("qty") or "").strip()))
    if not tiers:
        return None
    # 只留白名单单位
    tiers = [t for t in tiers if UNIT_OK.get(t[1].lower()) and 0 < t[0] <= 5000]
    if not tiers:
        return None
    # ① 剔除系统噪声常量。实测 $10/$20 跨 60 个互不相关的 SKU 反复出现在价格档里
    #    (阿里页面的固定元素被误抓,非单价) —— 必须**先于**下限过滤,否则低价档被滤掉会
    #    抬高中位数,让噪声判据失效(实测 YM228 因此反被判成 $10)。
    others = [t[0] for t in tiers if t[0] not in NOISE_CONST]
    if not others:
        # 白名单档【全部】是噪声常量(实测 10 个 SKU,含 CDK199/MSB164 这两个连主图都抓成
        # 平台徽标的 listing)→ 该 listing 价格整体不可信,直接降级
        return None
    med = statistics.median(others)
    # 两条剔除判据(任一命中即剔):
    #   a) 位置判据 —— 实测 CDK 全系是固定序列 "$20 → $10 → 真实价"($20/$10 是页面促销元素),
    #      故噪声常量若落在前两档且存在真实替代档,判为噪声;
    #   b) 倍数判据 —— 噪声常量出现在靠后位置时(如 SLM693 [0.78,0.57,0.5,10.0])靠倍数抓。
    tiers = [t for i, t in enumerate(tiers)
             if not (t[0] in NOISE_CONST and (i < 2 or t[0] > med * 2.5))]
    if not tiers:
        return None
    # ② 单位敏感下限:整包单位低于 $0.30 不合理(一整包货不可能 3 毛),单件保留 $0.03
    tiers = [t for t in tiers if (0.30 if UNIT_OK[t[1].lower()] in BULK_UNITS else 0.03) <= t[0]]
    if not tiers:
        return None
    # ③ 清洗后极差仍 >5 倍 = 该 listing 价格数据不可信 → 降级「按量报价」,绝不显示假价
    vals = [t[0] for t in tiers]
    if len(vals) >= 2 and max(vals) / min(vals) > 5:
        return None
    # ④ 取与 MOQ 匹配的档,否则首档(listing 门面价,非 min)
    moq = (e.get("moq") or "").lower()
    chosen = None
    for v, u, q in tiers:
        if u and q and (q + " " + u).lower() in moq:
            chosen = (v, u)
            break
    if chosen is None:
        chosen = (tiers[0][0], tiers[0][1])
    return (chosen[0], UNIT_OK[chosen[1].lower()])

def fmt_price(v):
    return f"{v:.2f}".rstrip("0").rstrip(".") if v < 100 else f"{v:.0f}"

def img_dim(rel):
    with Image.open(SITE / rel) as im:
        return im.size

def is_badge_img(rel):
    """阿里 'Trade Assurance' 等平台徽标会被误抓成产品图(实测 531x80)。
    判据=极端宽高比 >4:1 且高 <200px,真实产品图不会是这形状。既非产品图又有商标风险,一律剔除。"""
    try:
        w, h = img_dim(rel)
        return (w / h) > 4 and h < 200
    except Exception:
        return False

# ---- 1) 页壳(products.html) ----
shell = (SITE / "products.html").read_text(encoding="utf-8")
m = re.search(r"<main[^>]*>", shell)
pre_shell = shell[: m.end()]
post_shell = shell[shell.index("</main>"):]
pre_shell = re.sub(r'<script type="application/ld\+json">.*?</script>\s*', "", pre_shell, flags=re.S)

SKIP_VALS = {"NONE", "None", "none", "-", "", "No"}
# 阿里 listing 的无信息占位值(77 处):进 schema 会稀释真实事实密度,进规格表是废行 → 一律跳过
NOISE_VALS = {"other", "others", "n/a", "na", "unknown", "miscellaneous", "not applicable"}
# 不上站的规格键(Jacken 07-25:产地不展示)。规格表与 Product schema 两处同时排除
HIDE_SPEC_KEYS = {"Place of Origin"}
def is_noise(v):
    s = str(v).strip()
    return s in SKIP_VALS or s.lower() in NOISE_VALS
BAD_TITLE_TAIL = re.compile(r"\s*-\s*Buy.*$", re.I)
# 实体归一:全站 Organization 用同一 @id(见 index 等核心页的 Organization 节点),
# PDP 的 manufacturer/seller 指向它 → 全部产品与品牌实体绑定(GEO)
ORG_REF = {"@type": "Organization", "@id": BASE + "#organization", "name": "Qula Craft",
           "legalName": "Yiwu Sola Craft Co., Ltd.", "url": BASE}

made = 0
for e in pdp:
    sku, key = e["sku"], e["assetKey"]
    slug = f"p-{key}.html"
    url = BASE + slug
    catrow = flat[e["ci"]]
    cslug = e["categorySlug"]
    cname = e["category"]
    title_full = clean_title(BAD_TITLE_TAIL.sub("", e["titleFull"]).strip())
    short = cut_words(title_full, 42)
    page_title = f"{short} ({sku}) | Qula Craft"
    pm = price_min(e)
    moq = (e.get("moq") or "").strip()
    dparts = [cut_words(title_full, 60), f"Wholesale {cname}"]  # cname 靠前:同产品跨分类的两个 SKU(如 SLM680/YX3531)据此差异化,不被尾部截断
    if moq:
        dparts.append(f"MOQ {moq}")
    if pm:
        dparts.append(f"from ${fmt_price(pm[0])}/{pm[1]}" if pm[1] else f"from ${fmt_price(pm[0])}")
    desc = ". ".join(dparts) + ". From Yiwu; batch reports on request."
    if len(desc) > 158:
        desc = desc[:155].rsplit(" ", 1)[0] + "…"

    imgs = [r for r in (e.get("imagesLocal") or []) if not is_badge_img(r)]  # 防线:徽标图不上站
    dims = [img_dim(r) for r in imgs]

    # head
    h = pre_shell
    h = re.sub(r"<title>.*?</title>", f"<title>{esc(page_title)}</title>", h, 1, re.S)
    h = re.sub(r'(<meta name="description" content=")[^"]*(")', lambda mm: mm.group(1) + esc(desc) + mm.group(2), h, 1)
    h = re.sub(r'(<meta name="keywords" content=")[^"]*(")',
               lambda mm: mm.group(1) + esc(f"{sku}, {cut_words(title_full,60)}, {cname} wholesale, bulk craft supplies") + mm.group(2), h, 1)
    h = re.sub(r'(<link rel="canonical" href=")[^"]*(")', lambda mm: mm.group(1) + url + mm.group(2), h, 1)
    h = re.sub(r'(hreflang="[^"]*" href=")[^"]*(")', lambda mm: mm.group(1) + url + mm.group(2), h)
    h = re.sub(r'(<meta property="og:url" content=")[^"]*(")', lambda mm: mm.group(1) + url + mm.group(2), h, 1)
    h = re.sub(r'(<meta property="og:title" content=")[^"]*(")', lambda mm: mm.group(1) + esc(page_title) + mm.group(2), h, 1)
    h = re.sub(r'(<meta property="og:description" content=")[^"]*(")', lambda mm: mm.group(1) + esc(desc) + mm.group(2), h, 1)
    ogimg = BASE + imgs[0] if imgs else BASE + catrow["image"]
    h = re.sub(r'(<meta property="og:image" content=")[^"]*(")', lambda mm: mm.group(1) + ogimg + mm.group(2), h, 1)
    h = re.sub(r'(<meta name="twitter:title" content=")[^"]*(")', lambda mm: mm.group(1) + esc(page_title) + mm.group(2), h, 1)
    h = re.sub(r'(<meta name="twitter:description" content=")[^"]*(")', lambda mm: mm.group(1) + esc(desc) + mm.group(2), h, 1)
    h = re.sub(r'(<meta name="twitter:image" content=")[^"]*(")', lambda mm: mm.group(1) + ogimg + mm.group(2), h, 1)

    specs_raw = e.get("specs") or {}
    # schema
    product = {"@context": "https://schema.org", "@type": "Product", "name": title_full, "sku": sku,
               "image": [BASE + r for r in imgs] or [BASE + catrow["image"]],
               "description": desc, "category": cname, "url": url,
               "brand": {"@type": "Brand", "name": "Qula Craft"},
               "manufacturer": ORG_REF, "isFamilyFriendly": True}
    # 真实规格 → schema 官方属性(零编造:只取 pdp-data 抓到的值,SKIP_VALS 跳过)
    def sv(k):
        v = str(specs_raw.get(k, "")).strip()
        return v if v and not is_noise(v) else None
    for schema_key, spec_key in (("material", "Material"), ("color", "Color"),
                                 ("pattern", "Pattern"), ("size", "Size")):
        if sv(spec_key):
            product[schema_key] = sv(spec_key)
    if sv("Model Number"):
        product["mpn"] = sv("Model Number")          # 真实制造商编号(如 SS-RW5306)
    # 其余规格进 additionalProperty(Shape/Style/Feature/Usage/Application/Place of Origin 等)
    addl = [{"@type": "PropertyValue", "name": k, "value": str(v).strip()}
            for k, v in specs_raw.items()
            if not is_noise(v) and k not in HIDE_SPEC_KEYS
            and k not in ("Material", "Color", "Pattern", "Size", "Model Number", "Brand Name")]
    if addl:
        product["additionalProperty"] = addl
    if pm:
        product["offers"] = {"@type": "AggregateOffer", "lowPrice": fmt_price(pm[0]), "priceCurrency": "USD",
                             "offerCount": len(e.get("priceTiers") or []), "availability": "https://schema.org/InStock",
                             "url": url, "seller": ORG_REF}
    crumb = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": BASE},
        {"@type": "ListItem", "position": 2, "name": "Products", "item": BASE + "products.html"},
        {"@type": "ListItem", "position": 3, "name": cname, "item": BASE + catpage(cslug)},
        {"@type": "ListItem", "position": 4, "name": sku, "item": url}]}
    sc = "".join(f'<script type="application/ld+json">{json.dumps(o, ensure_ascii=False, separators=(", ", ": "))}</script>\n'
                 for o in [product, crumb])
    h = h.replace("</head>", sc + "</head>")
    if imgs:
        h = h.replace("</head>", f'<link rel="preload" as="image" href="{imgs[0]}"></head>')

    # specs 行
    specs = specs_raw
    rows = []
    has_material = specs.get("Material") and not is_noise(specs["Material"])
    if has_material:
        rows.append(("Material", str(specs["Material"]).strip()))
    for k, v in specs.items():
        if k == "Material" or is_noise(v) or k in HIDE_SPEC_KEYS:  # 占位行/不展示键不上表
            continue
        rows.append((k, str(v).strip()))
    spec_html = "".join(f"<tr><td><b>{esc(k)}</b></td><td>{esc(v)}</td></tr>" for k, v in rows[:12])
    if not has_material:
        spec_html += '<tr><td><b>Material</b></td><td>Not published on this listing — confirmed at quotation</td></tr>'

    # 价格块(只上 From $)
    if pm:
        unit_txt = f" / {esc(pm[1])}" if pm[1] else ""
        price_html = (f'<div class="answer-box" style="margin:14px 0"><b>From ${fmt_price(pm[0])}{unit_txt}</b>'
                      + (f" · MOQ {esc(moq)}" if moq else " · MOQ confirmed in quote")
                      + " — tiered pricing by quantity; the full tier table comes back with your quote within 12&#8211;24 hours.</div>")
    else:
        price_html = ('<div class="answer-box" style="margin:14px 0"><b>Quoted by pack and quantity</b>'
                      + (f" · MOQ {esc(moq)}" if moq else "") + " — full pricing comes back with your quote within 12&#8211;24 hours.</div>")

    # 图库
    if imgs:
        w0, h0 = dims[0]
        alt0 = esc(f"{sku} {cut_words(title_full, 55)}")
        gal = f'<div class="gallery-main"><img fetchpriority="high" src="{imgs[0]}" alt="{alt0}" width="{w0}" height="{h0}"></div>'
        if len(imgs) > 1:
            gal += '<div class="gallery-row">' + "".join(
                f'<img loading="lazy" src="{r}" alt="{esc(sku)} detail view {i+1}" width="{dims[i][0]}" height="{dims[i][1]}">'
                for i, r in enumerate(imgs) if i > 0) + "</div>"
    else:
        w0, h0 = img_dim(catrow["image"])
        gal = f'<div class="gallery-main"><img fetchpriority="high" src="{catrow["image"]}" alt="{esc(sku)}" width="{w0}" height="{h0}"></div>'

    # 相关产品 ×4(同分类,顺序循环)
    sibs = [x for x in pdp if x["categorySlug"] == cslug and x["assetKey"] != key]
    my_pos = [i for i, x in enumerate(pdp) if x["assetKey"] == key][0]
    sibs.sort(key=lambda x: (x["ci"] <= e["ci"], x["ci"]))
    rel_cards = ""
    for s in sibs[:4]:
        srow = flat[s["ci"]]
        simg = (s.get("imagesLocal") or [srow["image"]])[0]
        sw, sh = img_dim(simg)
        st = clean_title(s["titleFull"])
        # 标题存完整值(SEO/AI 可读),视觉两行省略交给 CSS .product-info h3 的 line-clamp
        rel_cards += (f'<article class="product-card"><div class="product-img"><a href="p-{s["assetKey"]}.html" style="display:block">'
                      f'<img loading="lazy" src="{simg}" alt="{esc(s["sku"])} {esc(cut_words(st,40))}" width="{sw}" height="{sh}"></a></div>'
                      f'<div class="product-info"><span class="pill soft">{esc(s["sku"])}</span>'
                      f'<h3><a href="p-{s["assetKey"]}.html" style="color:inherit;text-decoration:none">{esc(st)}</a></h3>'
                      f'<a class="btn btn-card" href="p-{s["assetKey"]}.html">View details <span>→</span></a></div></article>')

    main_img = imgs[0] if imgs else catrow["image"]
    q_url = f"quote.html?product={esc(cut_words(title_full, 50)).replace(' ', '%20')}&sku={esc(sku)}&image={esc(main_img)}"
    wa = ("https://wa.me/8618632026595?text=" +
          f"Hello%20Qula%20Craft%2C%20I%20just%20viewed%20SKU%20{sku}%20and%20would%20like%20to%20discuss%20a%20custom%20quote.%20Can%20we%20chat%3F")

    body = f"""
<section class="page-hero pdp-hero"><div class="container">
  <nav class="breadcrumb"><a href="index.html">Home</a> / <a href="products.html">Products</a> / <a href="{catpage(cslug)}">{esc(cname)}</a> / <span>{esc(sku)}</span></nav>
  <span class="eyebrow">{esc(cname)} · SKU {esc(sku)}</span>
  <h1>{esc(title_full)}</h1>
</div></section>
<section class="section" style="padding-top:26px"><div class="container detail-grid"><div>{gal}</div>
<div>
  {price_html}
  <table class="spec-table"><tr><th colspan="2">Listed specifications</th></tr>{spec_html}
  <tr><td><b>Stock status</b></td><td>Live production item</td></tr></table>
  <p style="font-size:.85rem;color:#77808c;margin:10px 0 16px">Decorative craft material — non-edible. Batch test reports (EN 71, ASTM F963, CPC, REACH) available on request.</p>
  <div class="pdp-cta" style="display:flex;flex-direction:column;gap:10px;max-width:340px">
    <a class="btn btn-primary" href="{q_url}">Request Quote for {esc(sku)} <span>→</span></a>
    <a class="btn btn-wa-3d" href="{wa}" target="_blank" rel="noopener">Chat on WhatsApp</a>
    <a class="basket-add" data-sku="{esc(sku)}" data-title="{esc(catrow['title'])}">＋ Add to inquiry list</a>
  </div>
</div></div></section>
<section class="section section-soft"><div class="container"><div class="section-head"><span class="eyebrow">Same Line</span><h2>More {esc(cname)}</h2><p>Every item below is a live stock listing — quote any SKU directly or <a href="{catpage(cslug)}">browse the full {esc(cname)} category</a>.</p></div><div class="product-grid" style="grid-template-columns:repeat(auto-fill,minmax(220px,1fr))">{rel_cards}</div></div></section>
"""
    (SITE / slug).write_text(h + body + post_shell, encoding="utf-8")
    made += 1
print(f"PDP 生成 ×{made}")

# ---- 2) 分类页 + seasonal 卡接链 ----
slug_by_sku_seq = {}
for e in pdp:
    slug_by_sku_seq.setdefault(e["sku"], []).append(f"p-{e['assetKey']}.html")
PAGES = ["polymer-clay-sprinkles", "resin-charms", "acrylic-beads", "glitter-sequins-fillers",
         "pvc-plastic-charms", "slime-charms", "beads-for-pens", "keychain", "jewelry-accessories",
         "seasonal-collections"]
CARD = re.compile(r'<article class="product-card"[^>]*>.*?</article>', re.S)
PILL = re.compile(r'<span class="pill soft">([^<]+)</span>')
linked_total = 0
for pg in PAGES:
    f = SITE / f"{pg}.html"
    h = f.read_text(encoding="utf-8")
    seen = {}
    def patch(mm):
        global linked_total
        c = mm.group(0)
        if 'href="p-' in c:
            return c
        pm2 = re.search(r'<span class="pill soft">([^<]+)</span>', c)
        if pm2:
            sku = pm2.group(1).strip()
        else:
            qm = re.search(r'quote\.html\?product=([A-Za-z0-9-]+)%20', c)
            if not qm:
                return c
            sku = qm.group(1).strip()
        lst = slug_by_sku_seq.get(sku)
        if not lst:
            return c
        idx = min(seen.get(sku, 0), len(lst) - 1)
        seen[sku] = idx + 1
        slug = lst[idx]
        c2 = c.replace('<div class="product-img"><img', f'<div class="product-img"><a href="{slug}" style="display:block"><img', 1)
        c2 = re.sub(r"(</div><div class=\"product-info\">)", r"</a>\1", c2, 1) if c2 != c else c2
        # h3 包链
        c2 = re.sub(r"<h3>([^<]+)</h3>", lambda hm: f'<h3><a href="{slug}" style="color:inherit;text-decoration:none">{hm.group(1)}</a></h3>', c2, 1)
        linked_total += 1
        return c2
    h2 = CARD.sub(patch, h)
    f.write_text(h2, encoding="utf-8")
print(f"分类/季节页卡接链 ×{linked_total}")

# ---- 3) main.js 搜索卡接链 ----
mj = SITE / "assets/js/main.js"
js = mj.read_text(encoding="utf-8")
OLD_IMG = "'<article class=\"product-card\"><div class=\"product-img\"><img loading=\"lazy\" src=\"'+p.image+'\" alt=\"'+p.imageAlt+'\" width=\"'+p.imageWidth+'\" height=\"'+p.imageHeight+'\"></div>"
NEW_IMG = "'<article class=\"product-card\"><div class=\"product-img\">'+(p.pdp?'<a href=\"'+p.pdp+'\" style=\"display:block\">':'')+'<img loading=\"lazy\" src=\"'+p.image+'\" alt=\"'+p.imageAlt+'\" width=\"'+p.imageWidth+'\" height=\"'+p.imageHeight+'\">'+(p.pdp?'</a>':'')+'</div>"
OLD_H3 = "<h3>'+t+'</h3>"
NEW_H3 = "<h3>'+(p.pdp?'<a href=\"'+p.pdp+'\" style=\"color:inherit;text-decoration:none\">'+t+'</a>':t)+'</h3>"
if "p.pdp" in js:
    print("main.js 已打过补丁,跳过")
else:
    assert OLD_IMG in js and OLD_H3 in js, "main.js card 模板未匹配"
    js = js.replace(OLD_IMG, NEW_IMG, 1).replace(OLD_H3, NEW_H3, 1)
    mj.write_text(js, encoding="utf-8")
    print("main.js 搜索卡接链 ✓")

# ---- 4) sitemap ----
sp = SITE / "sitemap.xml"
sm = sp.read_text(encoding="utf-8")
nodes = "".join(f"<url><loc>{BASE}p-{e['assetKey']}.html</loc><lastmod>{TODAY}</lastmod><changefreq>monthly</changefreq><priority>0.6</priority></url>\n"
                for e in pdp if f"p-{e['assetKey']}.html" not in sm)
sm = sm.replace("</urlset>", nodes + "</urlset>")
sp.write_text(sm, encoding="utf-8")
print("sitemap URL:", sm.count("<url>"))

# ---- 5) llms-full.txt + llms.txt 引用 ----
lines = [f"# Qula Craft — full product index ({len(pdp)} live stock items)", ""]
for c in cat["categories"]:
    lines.append(f"## {c.get('name', c.get('slug',''))}")
    for prow in c["products"]:
        ee = next((x for x in pdp if x["ci"] == flat.index(prow)), None)
        if not ee:
            continue
        pm = price_min(ee)
        seg = [clean_title(ee["titleFull"]), f"SKU {ee['sku']}"]
        if ee.get("moq"):
            seg.append(f"MOQ {ee['moq']}")
        if pm:
            seg.append(f"from ${fmt_price(pm[0])}" + (f"/{pm[1]}" if pm[1] else ""))
        lines.append(f"- [{seg[0]}]({BASE}p-{ee['assetKey']}.html): " + " · ".join(seg[1:]))
    lines.append("")
(SITE / "llms-full.txt").write_text("\n".join(lines), encoding="utf-8")
lt = SITE / "llms.txt"
t = lt.read_text(encoding="utf-8")
product_heading = f"## Products ({len(cat['categories'])} categories, {len(pdp)} live stock items)"
t = re.sub(r"## Products \(\d+ categories, \d+ live stock items\)", product_heading, t, count=1)
if "llms-full.txt" not in t:
    t = t.replace(product_heading,
                  f"Full per-item index with prices and MOQ: {BASE}llms-full.txt\n\n{product_heading}")
lt.write_text(t, encoding="utf-8")
print("llms-full.txt ✓ +", len(lines), "行; llms.txt 引用 ✓")
