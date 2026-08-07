# -*- coding: utf-8 -*-
"""指南生成器 — 数据驱动产出 guide-*.html。
铁律:
  · 每条数字都来自 pdp-data.json / product-catalog.json 实抓值,或已 WebFetch 验证过正文的权威源
  · 权威外链每篇 ≥2 条,且必须是**已验证正文**的(2026-07-25 验证:ICC/trade.gov/Wikipedia 三站可达,
    CPSC/ASTM/ECHA/CBP 反爬 403 —— 未验证的一律不放)
  · 页壳克隆自现有 guide,保证导航/页脚/样式与全站一致
"""
import json, re
from pathlib import Path

SITE = Path(r"E:\Claude\solacraft-site")
BASE = "https://www.qulacrafts.com/"
TODAY = "2026-07-25"
V = "20260725f"
SHELL_SRC = SITE / "guide-slime-business-supply-checklist.html"

# ---------- 已验证权威源(2026-07-25 逐条 WebFetch 验证正文) ----------
SRC = {
    "polymer_clay": ('https://en.wikipedia.org/wiki/Polymer_clay',
                     'polymer clay is a PVC-based modelling material that cures at 129–135&nbsp;°C'),
    "pet": ('https://en.wikipedia.org/wiki/Polyethylene_terephthalate',
            'PET carries resin identification code 1 and is practically insoluble in water'),
    "resin_casting": ('https://en.wikipedia.org/wiki/Resin_casting',
                      'a flexible mould yields roughly 25–100 castings before it loses fine detail'),
    "incoterms": ('https://iccwbo.org/business-solutions/incoterms-rules/',
                  'ICC first published the Incoterms® rules in 1936; Incoterms® 2020 took effect 1 January 2020'),
    "hs_codes": ('https://www.trade.gov/harmonized-system-hs-codes',
                 'the Harmonized System assigns six-digit codes internationally, which the US extends to ten'),
}

def esc(s):
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")

# ---------- 页壳 ----------
shell = SHELL_SRC.read_text(encoding="utf-8")
_m = re.search(r"<main[^>]*>", shell)
PRE = shell[:_m.end()]
POST = shell[shell.index("</main>"):]
# 清掉源页的 JSON-LD(每篇自己生成)
PRE = re.sub(r'<script type="application/ld\+json">.*?</script>\s*', "", PRE, flags=re.S)


def build(g):
    slug, title, desc = g["slug"], g["title"], g["desc"]
    url = BASE + slug
    h = PRE
    h = re.sub(r"<title>.*?</title>", f"<title>{esc(title)}</title>", h, 1, re.S)
    h = re.sub(r'(<meta name="description" content=")[^"]*(")',
               lambda m: m.group(1) + esc(desc) + m.group(2), h, 1)
    h = re.sub(r'(<link rel="canonical" href=")[^"]*(")', lambda m: m.group(1) + url + m.group(2), h, 1)
    h = re.sub(r'(hreflang="[^"]*" href=")[^"]*(")', lambda m: m.group(1) + url + m.group(2), h)
    h = re.sub(r'(<meta property="og:url" content=")[^"]*(")', lambda m: m.group(1) + url + m.group(2), h, 1)
    for k in ("og:title", "twitter:title"):
        h = re.sub(rf'(<meta (?:property|name)="{k}" content=")[^"]*(")',
                   lambda m: m.group(1) + esc(title) + m.group(2), h, 1)
    for k in ("og:description",):
        h = re.sub(rf'(<meta property="{k}" content=")[^"]*(")',
                   lambda m: m.group(1) + esc(desc) + m.group(2), h, 1)
    ogimg = BASE + g["hero"]
    for k in ("og:image", "twitter:image"):
        h = re.sub(rf'(<meta (?:property|name)="{k}" content=")[^"]*(")',
                   lambda m: m.group(1) + ogimg + m.group(2), h, 1)

    art = {"@context": "https://schema.org", "@type": "Article", "headline": title,
           "description": desc, "image": ogimg, "datePublished": TODAY, "dateModified": TODAY,
           "author": {"@type": "Organization", "@id": BASE + "#organization",
                      "name": "Qula Craft Sourcing Team", "url": BASE},
           "publisher": {"@type": "Organization", "name": "Qula Craft",
                         "logo": {"@type": "ImageObject", "url": BASE + "assets/images/favicon.png"}},
           "mainEntityOfPage": url}
    crumb = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": BASE},
        {"@type": "ListItem", "position": 2, "name": "Resources", "item": BASE + "resources.html"},
        {"@type": "ListItem", "position": 3, "name": title, "item": url}]}
    faq = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
        for q, a in g["faq"]]}
    sc = "".join(f'<script type="application/ld+json">{json.dumps(o, ensure_ascii=False, separators=(", ", ": "))}</script>\n'
                 for o in (art, crumb, faq))
    h = h.replace("</head>", sc + "</head>")

    rel_html = "".join(
        f'<article class="article-card"><span>Guide</span>'
        f'<h3><a href="{r[0]}" style="color:inherit;text-decoration:none">{esc(r[1])}</a></h3>'
        f'<p>{esc(r[2])}</p><a class="text-link" href="{r[0]}">Read guide &rarr;</a></article>'
        for r in g["related"])

    body = f"""
<section class="page-hero"><div class="container narrow">
  <nav class="breadcrumb"><a href="index.html">Home</a> / <a href="resources.html">Resources</a> / <span>{esc(g['crumb'])}</span></nav>
  <span class="eyebrow">{esc(g['eyebrow'])}</span>
  <h1>{esc(g['h1'])}</h1>
  <p class="small-note" style="margin-top:10px">Updated {g['updated']} &middot; by the Qula Craft Sourcing Team &mdash; the people who quote and pack these lines every week.</p>
</div></section>
<section class="section" style="padding-top:26px"><div class="container guide-body">
  <div class="answer-box">{g['answer']}</div>
  <figure style="margin:26px 0"><img loading="lazy" src="{g['hero']}?v={V}" alt="{esc(g['heroAlt'])}" width="{g['heroW']}" height="{g['heroH']}" style="width:100%;height:auto;aspect-ratio:1/1;object-fit:contain;background:#fbf7f9;border-radius:22px;max-width:520px;display:block;margin:0 auto"><figcaption class="small-note" style="text-align:center;margin-top:8px">{esc(g['heroCap'])}</figcaption></figure>
  {g['bodyHtml']}
  <div class="guide-note">{g['note']}</div>
  <h2 style="font-family:var(--serif);font-size:30px;line-height:1.12;margin:12px 0 10px">{esc(g['ctaH2'])}</h2>
  <p>{g['ctaP']}</p>
  <p><a class="btn btn-primary" href="{g['ctaHref']}">{esc(g['ctaLabel'])} <span>&rarr;</span></a></p>
</div></section>
<section class="section section-soft"><div class="container guide-body">
  <div class="section-head" style="text-align:left;margin-bottom:20px"><span class="eyebrow">Keep Reading</span>
  <h2 style="font-family:var(--serif);font-size:30px;margin:12px 0 0">Related buyer guides</h2></div>
  <div class="article-grid">{rel_html}</div>
</div></section>
"""
    (SITE / slug).write_text(h + body + POST, encoding="utf-8")
    words = len(re.findall(r"[A-Za-z]{2,}", re.sub(r"<[^>]+>", " ", body)))
    return words


if __name__ == "__main__":
    from guides_content import GUIDES as G1
    from guides_trade import GUIDES as G2
    GUIDES = G1 + G2
    print(f"生成 {len(GUIDES)} 篇指南\n")
    for g in GUIDES:
        w = build(g)
        ext = len(re.findall(r'href="https?://(?!www\.qulacrafts)', g["bodyHtml"] + g["note"]))
        flag = "" if w >= 800 else "  ⚠ <800词"
        print(f"  {g['slug']:52} {w:>5} 词{flag}")
