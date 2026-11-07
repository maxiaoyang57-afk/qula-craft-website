"""Create a new text-only specification graphic from verified YA855 facts.

This is a reference card, not a product photograph or measurement record.
The original product photo and historical specification graphic are preserved.
"""
from pathlib import Path
import sys,textwrap
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from pdp_public_copy import VERIFIED_SPECS
facts=VERIFIED_SPECS['YA855']
assert facts['Size']=='14 mm bead diameter'
assert 'Approx. 2 mm' in facts['Hole']
font_root=Path('/usr/share/fonts/truetype/dejavu')
def font(size,bold=False):return ImageFont.truetype(str(font_root/('DejaVuSans-Bold.ttf' if bold else 'DejaVuSans.ttf')),size)
im=Image.new('RGB',(1000,1000),'#f7f6f1');d=ImageDraw.Draw(im)
d.text((64,48),'QULA CRAFT / PRODUCT REFERENCE',font=font(21),fill='#8d4056')
d.text((64,105),'YA855',font=font(54,True),fill='#18363c')
d.text((64,181),'AB heart-pattern acrylic round beads',font=font(29),fill='#18363c')
d.rounded_rectangle((60,244,940,411),radius=20,fill='#e2eee7')
d.text((88,268),'SUPPLIER-REFERENCE HOLE DIAMETER',font=font(19),fill='#35574b')
d.text((88,312),'Approximately 2 mm',font=font(43,True),fill='#183f37')
for y,label,value in [(452,'BEAD DIAMETER','14 mm'),(548,'MATERIAL','Acrylic'),(644,'REFERENCE PACK','100 pieces per bag')]:
 d.line((64,y-14,936,y-14),fill='#d2d8d2',width=2)
 d.text((64,y),label,font=font(18),fill='#8d4056');d.text((64,y+30),value,font=font(30),fill='#18363c')
notes=['Confirm hole tolerance, direction and fit on the selected sample.','For a pen, check rod diameter and occupied length along the hole.','The reference pack is separate from minimum order quantity.']
y=770
for text in notes:
 for line in textwrap.wrap(text,70):d.text((64,y),line,font=font(20),fill='#35504d');y+=29
 d.text((64,937),'Supplier confirmation: 7 Nov 2026. Not a measurement photograph.',font=font(19),fill='#526660')
out=ROOT/'assets/images/pdp/ya855/ya855-2-reference-specifications-20261107.png'
im.save(out,optimize=True);print(out.relative_to(ROOT))
