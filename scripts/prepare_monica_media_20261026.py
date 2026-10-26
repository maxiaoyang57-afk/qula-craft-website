"""Build exact specification cards alongside same-SKU product references."""
import argparse,json,re
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps

FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
BOLD='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
def font(size,bold=False):return ImageFont.truetype(BOLD if bold else FONT,size)
def wrapped(draw,text,width,size=28,bold=False):
    f=font(size,bold);lines=[];line=''
    for word in str(text).split():
        nxt=(line+' '+word).strip()
        if draw.textlength(nxt,font=f)>width and line:lines.append(line);line=word
        else:line=nxt
    if line:lines.append(line)
    return lines

def text(draw,value,x,y,width=840,size=28,color='#25334a',bold=False,spacing=9):
    for line in wrapped(draw,value,width,size,bold):
        draw.text((x,y),line,font=font(size,bold),fill=color);y+=size+spacing
    return y

def card(plan,number):
    im=Image.new('RGB',(1000,1000),'#f6f8f8');d=ImageDraw.Draw(im)
    d.rectangle((0,0,1000,12),fill='#16877d')
    d.text((70,52),plan['sku'],font=font(25,True),fill='#16877d')
    y=text(d,'Product specifications' if number==2 else 'Packing and selection',70,102,size=42,bold=True)
    y=text(d,plan['title'],70,y+15,size=27,color='#5a6574')
    y+=35
    rows=([('MATERIAL',plan['material']),('DIMENSIONS',plan['dimensions']),('ATTACHMENT',plan['attachment'])] if number==2 else [('PACKING',plan['packing']),('ORDER QUANTITY','Confirm MOQ by inquiry'),('YOUR SELECTION','Confirm designs, colors and assortment')])
    for label,value in rows:
        d.rounded_rectangle((55,y-10,945,y+10),radius=6,fill='#e6efed')
        y+=10;d.text((70,y),label,font=font(18,True),fill='#16877d');y+=34
        y=text(d,value,70,y,size=27);y+=27
    if number==2:
        note='Dimensions are reference specifications, not a scale drawing. Confirm the selected variant before ordering.'
    else:
        note='Packing quantity is not the MOQ. Send the full SKU, required quantity and destination for a quotation. Props are not included.'
    y=max(y+15,805)
    assert y<910,(plan['sku'],number,y)
    text(d,note,70,y,size=20,color='#63717d',spacing=7)
    return im

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--plan',type=Path,required=True);ap.add_argument('--originals',type=Path,required=True);ap.add_argument('--edited',type=Path,required=True);ap.add_argument('--project',type=Path,required=True);ap.add_argument('--brand',choices=['haibu','qula'],required=True);a=ap.parse_args()
    plans=json.loads(a.plan.read_text());edited=json.loads(a.edited.read_text());refs={p.stem:p for p in a.originals.iterdir() if p.suffix.lower() in {'.jpg','.png'}}
    for p in plans:
        folder=a.project/('assets/images/products/batch-2026-10-26-monica/'+p['key'] if a.brand=='haibu' else 'assets/images/pdp/'+p['key']);folder.mkdir(parents=True,exist_ok=True)
        source=Path(edited[p['sku']]) if p['sku'] in edited else refs[p['sku']]
        im=Image.open(source).convert('RGB');im.thumbnail((1000,1000),Image.Resampling.LANCZOS)
        # Keep smaller original references at their native pixel size on a white
        # square, rather than inventing detail by enlarging them.
        canvas=Image.new('RGB',(1000,1000),'white');canvas.paste(im,((1000-im.width)//2,(1000-im.height)//2))
        outputs=[]
        for i,img in [(1,canvas),(2,card(p,2)),(3,card(p,3))]:
            name=(p['key']+'-'+p['keywords']+f'-{i:02}.jpg') if a.brand=='haibu' else (p['key']+f'-{i}-'+p['keywords']+'-20261026-monica.jpg')
            path=folder/name;img.save(path,quality=94,optimize=True);outputs.append(str(path.relative_to(a.project)))
        p['imagesLocal']=outputs;p['imageDimensions']=[{'width':1000,'height':1000}]*3
    dest=a.project/'scripts/data/product-plan-20261026-monica.json';dest.write_text(json.dumps(plans,ensure_ascii=False,indent=2)+'\n')
    print(a.brand,'prepared',len(plans)*3,'images')
