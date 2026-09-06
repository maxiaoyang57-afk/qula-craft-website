# -*- coding: utf-8 -*-
"""PDP 轮终极闸门:全量"""
import json, re, sys
from pathlib import Path
from collections import Counter

SITE = Path(__file__).resolve().parents[1]
fails = []
pages = sorted(SITE.glob("*.html"))
pdps = sorted(SITE.glob("p-*.html"))
expected_products = len(json.loads((SITE / "assets/data/pdp-data.json").read_text(encoding="utf-8")))
print(f"总页数: {len(pages)} PDP: {len(pdps)}")
if len(pdps) != expected_products:
    fails.append(f"PDP 数 {len(pdps)} != {expected_products}")

disk = {q.name for q in pages}
titles = Counter()
LQ, RQ = "“", "”"
for p in pages:
    h = p.read_text(encoding="utf-8")
    for s in re.findall(r'<script type="application/ld\+json">(.*?)</script>', h, re.S):
        try:
            json.loads(s)
        except Exception as e:
            fails.append(f"JSONLD {p.name}: {e}")
    if re.search("=[" + LQ + RQ + "]|[" + LQ + RQ + "]>", h):
        fails.append(f"智能引号 {p.name}")
    t = re.search(r"<title>(.*?)</title>", h, re.S)
    if t:
        titles[t.group(1)] += 1
    for href in re.findall(r'href="([^"#?]+\.html)', h):
        if href.startswith("http"):
            continue
        if Path(href).name not in disk:
            fails.append(f"死链 {p.name} -> {href}")
    for src in re.findall(r'(?:src|href)="(assets/[^"]+\.(?:webp|jpg|png|css|js))', h):
        if not (SITE / src.split("?")[0]).exists():
            fails.append(f"资源缺失 {p.name} -> {src}")
    if "?v=20260720i" in h:
        fails.append(f"旧版本号 {p.name}")

dup = {k[:60]: v for k, v in titles.items() if v > 1}
if dup:
    fails.append(f"标题重复: {dup}")

# PDP 专项
long_t = 0
for p in pdps:
    h = p.read_text(encoding="utf-8")
    import html as H
    t = H.unescape(re.search(r"<title>(.*?)</title>", h, re.S).group(1))
    if len(t) > 72:
        long_t += 1
    if 'class="answer-box"' not in h:
        fails.append(f"PDP缺价格块 {p.name}")
    if '"@type": "Product"' not in h:
        fails.append(f"PDP缺Product schema {p.name}")
    if "gallery-main" not in h:
        fails.append(f"PDP缺主图 {p.name}")
print(f"PDP 标题 >72字符: {long_t}")

# main.js 语法
import subprocess
r = subprocess.run(["node", "--check", str(SITE / "assets/js/main.js")], capture_output=True, text=True)
if r.returncode != 0:
    fails.append(f"main.js 语法: {r.stderr[:200]}")
else:
    print("main.js 语法 ✓")

# catalog 完整性
cat = json.loads((SITE / "assets/data/product-catalog.json").read_text(encoding="utf-8"))
flat = [p for c in cat["categories"] for p in c["products"]]
n_pdp = sum(1 for p in flat if p.get("pdp"))
n_core = sum(1 for p in flat if p.get("sku") and p.get("title") and p.get("image"))
print(f"catalog: {len(flat)} 条, 带pdp: {n_pdp}, 核心字段齐: {n_core}")
if n_pdp != expected_products or n_core != expected_products:
    fails.append(f"catalog 异常 pdp={n_pdp} core={n_core}")
for p in flat:
    if p.get("pdp") and not (SITE / p["pdp"]).exists():
        fails.append(f"catalog pdp 指向缺失: {p['pdp']}")

# sitemap
sm = (SITE / "sitemap.xml").read_text(encoding="utf-8")
import xml.etree.ElementTree as ET
try:
    ET.fromstring(sm)
except Exception as e:
    fails.append(f"sitemap XML: {e}")
locs = re.findall(r"<loc>([^<]+)</loc>", sm)
print(f"sitemap: {len(locs)}")
# 期望值 = 磁盘上应收录的页数(排除 noindex 的 404/thank-you),动态算,别写死 ——
# 写死的数字每次加页都会误报 FAIL(实测加 6 篇指南后 203→209 就炸了一次)
_expected = len([p for p in SITE.glob("*.html") if p.name not in ("404.html", "thank-you.html")])
print(f"sitemap 期望 {_expected}(磁盘页数减 noindex 页)")
if len(locs) != _expected:
    fails.append(f"sitemap {len(locs)} != 磁盘应收录页数 {_expected}")
for u in locs:
    fn = u.rstrip("/").split("/")[-1]
    fn = fn if fn.endswith(".html") else "index.html"
    if not (SITE / fn).exists():
        fails.append(f"sitemap 指向缺失: {u}")

# 分类页/seasonal 卡接链计数
for pg in ["polymer-clay-sprinkles", "resin-charms", "acrylic-beads", "glitter-sequins-fillers",
           "pvc-plastic-charms", "slime-charms", "beads-for-pens", "keychain", "jewelry-accessories",
           "seasonal-collections"]:
    h = (SITE / f"{pg}.html").read_text(encoding="utf-8")
    n = h.count('href="p-')
    print(f"  {pg}: {n} 个 PDP 链")
    if pg != "seasonal-collections" and n == 0:
        fails.append(f"{pg} 零 PDP 链")

# llms
if "llms-full.txt" not in (SITE / "llms.txt").read_text(encoding="utf-8"):
    fails.append("llms.txt 未引用 full")
lf = (SITE / "llms-full.txt").read_text(encoding="utf-8")
print(f"llms-full: {lf.count('](https')} 条产品行")

print("\n" + ("FAIL:\n" + "\n".join(fails[:30]) if fails else "PDP_ROUND_GATES_OK 全部通过"))
sys.exit(1 if fails else 0)
