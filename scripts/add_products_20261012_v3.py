"""Append the user-confirmed v3 product batch from the latest production catalog."""
import argparse, copy, hashlib, html, json, re, subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote
import openpyxl
from PIL import Image
from add_products_20261012 import card, save_json, sha256
from catalog_schema import catalog_list_item
ROOT=Path(__file__).resolve().parents[1]
BASE="https://www.qulacrafts.com/"
DATE="2026-10-12"
PAGES={"polymer-clay-slices":"polymer-clay-sprinkles.html","plastic-beads":"acrylic-beads.html","plastic-sequins":"glitter-sequins-fillers.html"}
MAP={"resin charms":"resin-charms","resin beads":"resin-charms","acrylic beads":"plastic-beads","polymer clay":"polymer-clay-slices","glitter sequins":"plastic-sequins","sequin glitter":"plastic-sequins","jewelry keychain":"keychain","jewelry charms":"jewelry-accessories","glass beads":"slime-charms"}
QUOTE_CATEGORIES={"resin-charms":"Resin Charms","plastic-beads":"Acrylic Beads","polymer-clay-slices":"Polymer Clay Sprinkles","plastic-sequins":"Glitter & Fillers","keychain":"Keychains","jewelry-accessories":"Jewelry Accessories","slime-charms":"Slime Charms"}
def norm(value):
 return re.sub(r"\s+"," ",str(value).strip()).lower()
def specs_from_source(raw):
 specs={"Material":re.sub(r"\s+"," ",raw["材质"].strip())}
 size=norm(raw["尺寸"])
 if size in {"无","咨询客服","none",""}:
  specs["Dimensions"]="Confirm dimensions by inquiry"
 else:
  text=re.sub(r"\s*\*\s*"," × ",str(raw["尺寸"]).strip()).replace("MM","mm")
  text=re.sub(r"\s*AND\s*"," / ",text)
  text=re.sub(r"(\d)mm\s+(?=\d)",r"\1 mm / ",text)
  text=re.sub(r"(?<=\d)\s*mm\b"," mm",text)
  specs["Size reference" if norm(raw["分类"])=="polymer clay" else "Size"]=text.strip()
 specs["Hole"]={"无":"No hole","有":"Present; confirm diameter by inquiry","咨询客服":"Confirm hole configuration by inquiry"}[raw["孔径"].strip()]
 if raw["颜色"].strip()=="混款":
  specs["Assortment"]="Mixed assortment; confirm the exact selection by inquiry"
 pack=re.search(r"(\d+)\s*(pcs|pair|g)/bag",raw["包装规格"],re.I)
 assert pack,raw["包装规格"]
 qty,unit=pack.groups()
 units={"pcs":"pieces","pair":"pairs","g":"g"}
 specs["Standard pack"]=f"{int(qty):,} {units[unit.lower()]} per bag; custom packing by inquiry"
 specs["Customization"]="Available; details confirmed by inquiry"
 return specs
def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("--plan",type=Path,required=True)
 ap.add_argument("--workbook",type=Path,required=True)
 args=ap.parse_args()
 plans=json.loads(args.plan.read_text())
 wb=openpyxl.load_workbook(args.workbook,data_only=True,read_only=True)
 vals=list(wb["Sheet1"].values);heads=vals[0]
 records={str(v[0]).strip():(i,dict(zip(heads,v))) for i,v in enumerate(vals[1:],2) if v[0]}
 wb.close()
 assert len(records)==37 and len(plans)==21
 batch={p["sku"] for p in plans}
 assert len(batch)==21 and batch.issubset(records)
 cat_path=ROOT/"assets/data/product-catalog.json"
 pdp_path=ROOT/"assets/data/pdp-data.json"
 copy_path=ROOT/"assets/data/pdp-copy.json"
 detail_path=ROOT/"assets/data/pdp-description-details.json"
 cat=json.loads(cat_path.read_text());pdp=json.loads(pdp_path.read_text())
 copies=json.loads(copy_path.read_text());details=json.loads(detail_path.read_text())
 before=copy.deepcopy(cat);old_flat=[p for c in cat["categories"] for p in c["products"]]
 assert len(old_flat)==253
 assert not batch.intersection(p["sku"] for p in old_flat)
 old_manifest=json.loads((ROOT/"docs/product-batch-manifest-20261012.json").read_text())
 for p in old_manifest["products"]:
  assert records[p["sku"]][1]==p["sourceFields"],"Earlier product source changed: "+p["sku"]
 baseline=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip()
 by_slug={c["slug"]:c for c in cat["categories"]}
 by_category={};new_rows=[];entries=[];manifest=[]
 for plan in plans:
  sku,key=plan["sku"],plan["key"]
  assert re.sub(r"[^a-z0-9]+","-",sku.lower()).strip("-")==key
  src_row,raw=records[sku]
  assert plan["category"]==MAP[norm(raw["分类"])]
  category=by_slug[plan["category"]]
  images=plan["imagesLocal"]
  assert len(images)==len(set(images))==3
  image_records=[]
  for n,rel in enumerate(images,1):
   assert rel.startswith(f"assets/images/pdp/{key}/{key}-{n}-")
   path=ROOT/rel
   with Image.open(path) as im:
    w,h=im.size
    assert 0<w<=1000 and h>0 and not im.getexif().get(34853)
   image_records.append({"path":rel,"role":["main","scene","detail"][n-1],"width":w,"height":h,"sha256":sha256(path),"bytes":path.stat().st_size,"origin":"supplied reference" if n==1 else "AI-assisted styling illustration",**({"prompt":plan["imagePrompts"][str(n)]} if n>1 else {})})
  with Image.open(ROOT/images[0]) as im:w,h=im.size
  assert 80<=len(plan["description"])<=160 and len(plan["metaTitle"])<=65
  query=f'quote.html?product={quote(sku+" "+plan["title"],safe="")}&sku={quote(sku,safe="")}&image={quote(images[0],safe="/")}&category={quote(QUOTE_CATEGORIES[category["slug"]],safe="")}'
  row={"category":category["name"],"categorySlug":category["slug"],"sourceSheet":"Sheet1","sourceRow":src_row,"sortOrder":0,
       "sku":sku,"title":plan["title"],"titleFull":plan["title"],"titleShort":plan["title"],"sourceTitle":raw["标题"],"sourceCategory":raw["分类"],
       "alibabaUrl":"","cleanAlibabaUrl":"","alibabaProductId":"","image":images[0],"imageAlt":sku+" "+plan["title"],"imageWidth":w,"imageHeight":h,
       "imageHash":hashlib.md5((ROOT/images[0]).read_bytes()).hexdigest(),"status":"ok","anchorNote":"","pdp":f"p-{key}.html","inquiryUrl":query}
  specs=specs_from_source(raw)
  assert raw["状态"]=="库存有货"
  if "/" in sku or sku.startswith("RX042-") or sku.startswith("RX155-"):
   specs["SKU group"]="Grouped assortment; confirm selected designs and mix by inquiry"
  if sku in {"YX720","YX3194","YX3900"}:
   specs["Mix components"]="Confirm the selected components and their individual sizes by inquiry"
  entry={"catalogIndex":0,"assetKey":key,"sku":sku,"category":category["name"],"categorySlug":category["slug"],"url":"","status":"ok","reason":"",
         "titleFull":raw["标题"],"moq":"","priceTiers":[],"stockStatus":"In stock; confirm the available quantity with your quote",
         "specs":specs,"images":[],"imagesLocal":images,"sourceWorkbook":args.workbook.name,"sourceSheet":"Sheet1","sourceRow":src_row,"sourceFields":raw,
         "importedAt":datetime.now(timezone.utc).isoformat(),"metaTitle":plan["metaTitle"],"metaDescription":plan["description"],"shortProductDescription":plan["description"]}
  copies[key]={"sku":sku,"displayTitle":plan["title"],"metaTitle":plan["metaTitle"],"metaDescription":plan["description"],"isFamilyFriendly":True}
  details[key]=plan["description"];new_rows.append(row);entries.append(entry)
  by_category.setdefault(category["slug"],[]).append(row)
  manifest.append({"sku":sku,"sourceRow":src_row,"sourceFields":raw,"displayTitle":plan["title"],"category":category["name"],"categorySlug":category["slug"],
                   "pdp":row["pdp"],"operation":"new grouped assortment" if "SKU group" in specs else "new","sourceImage":plan["source"],
                   "sourceImageSha256":plan["sourceImageSha256"],"imageOutputs":image_records})
 for c in cat["categories"]:
  c["products"]=by_category.get(c["slug"],[])+c["products"];c["productCount"]=len(c["products"])
  for i,p in enumerate(c["products"],1):p["sortOrder"]=i
 flat=[p for c in cat["categories"] for p in c["products"]]
 pdp.extend(entries);index={p["pdp"]:i for i,p in enumerate(flat,1)}
 for e in pdp:e["catalogIndex"]=index[f'p-{e["assetKey"]}.html']
 cat.update(totalProducts=len(flat),totalImages=len(flat),generatedAt=datetime.now(timezone.utc).isoformat())
 assert len(flat)==274
 for file,value,indent in [(cat_path,cat,1),(pdp_path,pdp,2),(copy_path,copies,2),(detail_path,details,2)]:save_json(file,value,indent)
 generator=(ROOT/"scripts/gen_pdp.py").read_text().split("# ---- 2)")[0]
 marker='for e in pdp:\n    sku, key'
 assert generator.count(marker)==1
 generator=generator.replace(marker,'for e in pdp:\n    if e["sku"] not in BATCH_SKUS: continue\n    sku, key')
 exec(compile(generator,str(ROOT/"scripts/gen_pdp.py"),"exec"),{"__file__":str(ROOT/"scripts/gen_pdp.py"),"BATCH_SKUS":batch})
 for row,e in zip(new_rows,entries):
  path=ROOT/row["pdp"];page=path.read_text()
  page=page.replace("Decorative craft material — non-edible. Batch test reports (EN 71, ASTM F963, CPC, REACH) available on request.",
                    "Confirm the selected assortment, minimum order quantity and dispatch date with your inquiry.")
  page,n=re.subn(r'<div class="answer-box" style="margin:14px 0">.*?</div>','<div class="answer-box" style="margin:14px 0"><b>Wholesale pricing by quotation</b> · Minimum order quantity confirmed by inquiry.</div>',page,count=1,flags=re.S)
  assert n==1
  page=page.replace("detail view 2","styled scene illustration").replace("detail view 3","styled detail illustration")
  marker='</div>\n<div>\n  <div class="answer-box"'
  assert marker in page
  note='<p class="pdp-image-note" style="font-size:.85rem;color:#667085">Image 1: supplied product reference. Images 2–3: styled illustrations. Props are not included; confirm the selected design or assortment before ordering.</p>'
  page=page.replace(marker,note+marker,1)
  page,n=re.subn(r'quote\.html\?product=[^"<>]+',html.escape(row["inquiryUrl"],quote=True),page,count=1);assert n==1
  path.write_text("\n".join(line.rstrip() for line in page.splitlines())+"\n")
 changed=[]
 for slug,rows in by_category.items():
  path=ROOT/PAGES.get(slug,slug+".html");page=path.read_text()
  first=re.search(r'<article class="product-card"',page);assert first
  page=page[:first.start()]+"".join(card(row) for row in rows)+page[first.start():]
  def update_schema(m):
   v=json.loads(m[1])
   if v.get("@type")=="ItemList":
    v.update(numberOfItems=len(by_slug[slug]["products"]),itemListElement=[catalog_list_item(p,i) for i,p in enumerate(by_slug[slug]["products"],1)])
   return '<script type="application/ld+json">'+json.dumps(v,ensure_ascii=False,separators=(",",":"))+"</script>"
  page=re.sub(r'<script type="application/ld\+json">(.*?)</script>',update_schema,page,flags=re.S)
  path.write_text(page);changed.append(path.name)
 sitemap=ROOT/"sitemap.xml";xml=sitemap.read_text()
 for row,e in zip(new_rows,entries):
  loc=BASE+row["pdp"]
  assert loc not in xml
  node="<url><loc>"+loc+"</loc><lastmod>"+DATE+"</lastmod><changefreq>monthly</changefreq><priority>0.7</priority>"
  node+="".join(f'<image:image><image:loc>{BASE+p}</image:loc><image:title>{html.escape(row["sku"]+" "+row["title"])}</image:title></image:image>' for p in e["imagesLocal"])+"</url>"
  xml=xml.replace("</urlset>","  "+node+"\n</urlset>")
 for page in changed:
  xml=re.sub(r"(<loc>"+re.escape(BASE+page)+r"</loc>\s*<lastmod>)[^<]+",r"\g<1>"+DATE,xml)
 sitemap.write_text(xml)
 llms=ROOT/"llms-full.txt";text=llms.read_text().replace("(253 live stock items)","(274 live stock items)")
 for slug,rows in by_category.items():
  heading="## "+by_slug[slug]["name"]+"\n";assert heading in text
  lines="".join(f'- [{p["title"]}]({BASE+p["pdp"]}): SKU {p["sku"]} · '+next(e for e in entries if e["sku"]==p["sku"])["specs"]["Standard pack"]+" · MOQ and pricing by quotation\n" for p in rows)
  text=text.replace(heading,heading+lines,1)
 llms.write_text(text)
 llms=ROOT/"llms.txt";text=llms.read_text()
 text=re.sub(r"## Products \(\d+ categories, \d+ live stock items\)","## Products (9 categories, 274 live stock items)",text);llms.write_text(text)
 old={p["pdp"]:p for p in old_flat};now={p["pdp"]:p for p in flat}
 for key,p in old.items():
  assert {k:v for k,v in now[key].items() if k!="sortOrder"}=={k:v for k,v in p.items() if k!="sortOrder"},key
 manifest_data={"batchId":"qula-products-20261012-v3","target":"QULA","baselineCommit":baseline,"sourceWorkbook":args.workbook.name,
   "sourceWorkbookSha256":sha256(args.workbook),"sourceProductRows":37,"preservedPreviousBatchRows":16,"newProductCount":21,"catalogCountBefore":253,
   "catalogCountAfter":274,"imageCount":63,"userCorrections":["User confirmed RW5463; supplied photo file is named RW5643.png."],
   "sourceCategoryMapping":MAP,"categoryMappingNotes":["Glass Beads is routed to the existing Slime Charms supplies category as no-hole decorative glass fillers; glass material remains explicit.",
   "RW728 uses source Acrylic/Plastic/Lucite material and source acrylic-beads classification; source title mentioning resin is retained only in raw sourceFields."],
   "products":manifest,"validationStatus":"pending"}
 save_json(ROOT/"docs/product-batch-manifest-20261012-v3.json",manifest_data)
 print(json.dumps({"new":21,"catalog":274,"images":63,"categoryPages":changed}))
if __name__=="__main__":main()
