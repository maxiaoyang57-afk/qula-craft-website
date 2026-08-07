# -*- coding: utf-8 -*-
"""④ 给 sitemap.xml 注入 image:image 扩展(860 张真实产品图)。
手工艺材料是视觉驱动品类,Google 图片搜索是真实采购入口。
幂等:重跑先剥旧 image 节点再重建;零编造(caption/title 全取页面真值)。"""
import json, re, html
from pathlib import Path

SITE = Path(r"E:\Claude\solacraft-site")
BASE = "https://www.qulacrafts.com/"
SM = SITE / "sitemap.xml"
NS_IMG = 'xmlns:image="http://www.google.com/schemas/sitemap-image/1.1"'

pdp = json.loads((SITE / "assets/data/pdp-data.json").read_text(encoding="utf-8"))
cat = json.loads((SITE / "assets/data/product-catalog.json").read_text(encoding="utf-8"))

ST = {"With","And","For","Of","The","A","An","In","On","Per","By","To"}
def clean_title(t):
    t = (t or "").replace("Wight","Weight").replace("Breads","Beads").replace("Artfcal","Artificial")
    w = re.sub(r"\s*-\s*Buy.*$", "", t, flags=re.I).split()
    while w and w[-1] in ST: w.pop()
    return " ".join(w)

def esc(s): return html.escape(s or "", quote=True)

# ---- 1) PDP 页 → 每页最多 4 张图 ----
imgs_by_url = {}
for e in pdp:
    url = BASE + f"p-{e['assetKey']}.html"
    title = clean_title(e.get("titleFull"))
    rows = []
    for rel in (e.get("imagesLocal") or [])[:4]:
        if (SITE / rel).exists():
            rows.append((BASE + rel, f"{e['sku']} — {title}"[:100]))
    if rows: imgs_by_url[url] = rows

# ---- 2) 分类页 → 该分类目录图 ----
CATPAGE = {"polymer-clay-slices":"polymer-clay-sprinkles.html","plastic-beads":"acrylic-beads.html",
           "plastic-sequins":"glitter-sequins-fillers.html"}
for c in cat["categories"]:
    page = BASE + CATPAGE.get(c["slug"], c["slug"] + ".html")
    rows = []
    for p in c["products"][:12]:          # 每分类页挂前 12 张,避免单 URL 图过多
        rel = p.get("image")
        if rel and (SITE / rel).exists():
            rows.append((BASE + rel, f"{p['sku']} — {clean_title(p.get('name') or c.get('name',''))}"[:100]))
    if rows: imgs_by_url.setdefault(page, []).extend(rows)

# ---- 3) 注入 sitemap(先剥旧 image 节点,保证幂等) ----
sm = SM.read_text(encoding="utf-8")
_url_count_before = sm.count("<url>")      # 注入前基准,用于校验只加 image 节点不动 URL
sm = re.sub(r"\s*<image:image>.*?</image:image>", "", sm, flags=re.S)
if NS_IMG not in sm:
    sm = sm.replace("<urlset ", f"<urlset {NS_IMG} ", 1)

added_urls = added_imgs = 0
def patch(m):
    global added_urls, added_imgs
    block, loc = m.group(0), m.group(1)
    rows = imgs_by_url.get(loc)
    if not rows: return block
    seen, nodes = set(), []
    for src, cap in rows:
        if src in seen: continue
        seen.add(src)
        nodes.append(f"<image:image><image:loc>{esc(src)}</image:loc>"
                     f"<image:title>{esc(cap)}</image:title></image:image>")
    added_urls += 1; added_imgs += len(nodes)
    return block.replace("</url>", "".join(nodes) + "</url>")

sm = re.sub(r"<url><loc>(.*?)</loc>.*?</url>", patch, sm, flags=re.S)
SM.write_text(sm, encoding="utf-8")

print(f"image sitemap 注入: {added_urls} 个 URL / {added_imgs} 张图")
print(f"sitemap URL 总数: {sm.count('<url>')}")
print(f"image:image 节点: {sm.count('<image:image>')}")
# 只校验"注入前后 URL 数不变",不写死具体数字 —— 写死会在每次加页时误报(实测加 6 篇指南即炸)
assert sm.count("<url>") == _url_count_before, f"URL 数被改变! {_url_count_before} → {sm.count('<url>')}"
assert "xmlns:image" in sm
# XML 合法性
import xml.etree.ElementTree as ET
ET.fromstring(sm)
print("XML 解析 ✓  IMAGE_SITEMAP_OK")
