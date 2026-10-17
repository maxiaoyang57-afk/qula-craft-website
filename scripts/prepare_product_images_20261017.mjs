// Render exact source facts as catalog graphics. Product photos remain uncropped.
import fs from 'node:fs/promises';
import path from 'node:path';
import { createRequire } from 'node:module';
const require=createRequire(import.meta.url);
const sharp=require('sharp');
const workspace=path.resolve(process.argv[2]||'..');
const site=process.argv[3]||'qula';
const plans=JSON.parse(await fs.readFile(path.join(workspace,'batch-plan.json'),'utf8'));
const neutral=site==='haibu'?JSON.parse(await fs.readFile(path.join(workspace,'neutral-images.json'),'utf8')):{};
const escape=s=>String(s).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;');
const wrap=(s,n)=>{const lines=[];let line='';for(const word of s.split(/\s+/)){if(line&&line.length+word.length+1>n){lines.push(line);line=word;}else line+=(line?' ':'')+word;}if(line)lines.push(line);return lines;};
const lines=(text,x,y,size,color,limit,leading=size*1.3)=>wrap(text,limit).map((s,i)=>`<text x="${x}" y="${y+i*leading}" fill="${color}" font-family="DejaVu Sans,Arial,sans-serif" font-size="${size}">${escape(s)}</text>`).join('');
const output=[];
for(const p of plans.filter(p=>p.operation==='new'&&(site==='qula'||p.haibu))){
 const supplied=path.join(workspace,'upload',p.source);
 const source=neutral[p.sku]||supplied;
 const dest=site==='qula'?path.join(workspace,'qula',path.dirname(p.imagesLocal[0])):path.join(workspace,'haibu/assets/images/products/batch-2026-10-17',p.key);
 await fs.mkdir(dest,{recursive:true});
 const paths=site==='qula'?p.imagesLocal.map(r=>path.join(workspace,'qula',r)):[1,2,3].map(n=>path.join(dest,p.key+'-'+p.keywords+'-'+String(n).padStart(2,'0')+'.jpg'));
 await sharp(source).rotate().resize({width:Math.min(p.sourceSize[0],1000),withoutEnlargement:true}).flatten({background:'#fff'}).jpeg({quality:85,mozjpeg:true}).toFile(paths[0]);
 const b64=(await fs.readFile(paths[0])).toString('base64');
 const ink=site==='haibu'?'#1d4e43':'#8c3854',brand=site==='haibu'?'HAIBUCRAFT':'QULA CRAFT';
 for(const n of [2,3]){
  const facts=n===2?[
   ['SOURCE DIMENSIONS',p.dimensions],['MATERIAL',p.sourceFields['材质']],['ATTACHMENT',p.sku==='ABC041-ABC042'?'Hole specification requires sample confirmation':p.sourceFields['孔径']==='有'?'Hole present; diameter not supplied':p.category==='keychain'?'Supplied keychain fittings; confirm each design':'No hole specified in the source']
  ]:[['STANDARD PACK','100 pieces per bag'],['ASSORTMENT','Confirm selected designs and mixing proportions'],['CUSTOM PACKING','Available by inquiry; confirm requirements'],['MOQ & DISPATCH','Confirm by quotation']];
  const title=n===2?'Size & attachment':'Packing & assortment';
  const foot=n===2?p.factNote:'Packing quantity is not the minimum order quantity. Send the full product code, selected designs, quantity and destination for quotation.';
  const metadata=await sharp(paths[0]).metadata();
  const iw=Math.min(490,metadata.width),ih=Math.min(580,metadata.height);
  let y=205;
  let body=lines(p.title,565,y,26,'#172a2b',25,33);y+=wrap(p.title,25).length*33+18;
  for(const [a,b] of facts){body+=`<path d="M565 ${y-7}H952" stroke="#cbd5ce"/>`+lines(a,565,y+14,12,ink,40)+lines(b,565,y+44,20,'#172a2b',29,27);y+=51+wrap(b,29).length*27;}
  if(y>798)throw new Error('Fact graphic overflow: '+p.sku+' '+n+' '+y);
  const svg=`<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="1000" height="1000"><rect width="1000" height="1000" fill="#f7f5f0"/>${lines(brand+' / PRODUCT GUIDE',48,55,17,ink,80)}${lines(title,48,112,40,'#172a2b',45)}${lines(p.sku,48,153,18,'#526160',85,25)}<rect x="48" y="190" width="490" height="600" rx="18" fill="#fff"/><image x="${48+(490-iw)/2}" y="${200+(580-ih)/2}" width="${iw}" height="${ih}" preserveAspectRatio="xMidYMid meet" xlink:href="data:image/jpeg;base64,${b64}"/>${body}<rect x="48" y="816" width="904" height="125" rx="12" fill="#e8ede5"/>${lines(foot,70,849,18,'#172a2b',86,27)}${lines('Source specification summary. Styling props are not included. Confirm the selected sample.',48,972,14,'#566560',110)}</svg>`;
  await sharp(Buffer.from(svg)).jpeg({quality:90,mozjpeg:true}).toFile(paths[n-1]);
 }
 // JFIF resolution only: preserve encoded pixels and omit EXIF/GPS metadata.
 for(const f of paths){const data=await fs.readFile(f);if(data.subarray(6,11).toString()!=='JFIF\0')await fs.writeFile(f,Buffer.concat([data.subarray(0,2),Buffer.from('ffe000104a46494600010101004800480000','hex'),data.subarray(2)]));}
 const dimensions=await Promise.all(paths.map(async f=>{const m=await sharp(f).metadata();return {width:m.width,height:m.height}}));
 output.push({sku:p.sku,paths,dimensions,source,sourceSize:p.sourceSize});
}
await fs.writeFile(path.join(workspace,site+'-media.json'),JSON.stringify(output,null,2));
console.log(JSON.stringify({site,products:output.length,images:output.length*3}));
