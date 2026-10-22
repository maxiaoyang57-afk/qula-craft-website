// Render exact source facts as catalog graphics. Product photos remain uncropped.
import fs from 'node:fs/promises';
import path from 'node:path';
import { createRequire } from 'node:module';
const require=createRequire(path.join(process.env.CODEX_PRIMARY_RUNTIME_NODE_MODULES,'placeholder.js'));
const sharp=require('sharp');
const workspace=path.resolve(process.argv[2]||'..');
const site=process.argv[3]||'qula';
const plans=JSON.parse(await fs.readFile(path.join(workspace,'plan-20261022.json'),'utf8'));
const neutral=JSON.parse(await fs.readFile(path.join(workspace,'neutral-images-20261022.json'),'utf8').catch(()=>'{}'));
const escape=s=>String(s).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;');
const wrap=(s,n)=>{const lines=[];let line='';for(const word of s.split(/\s+/)){if(line&&line.length+word.length+1>n){lines.push(line);line=word;}else line+=(line?' ':'')+word;}if(line)lines.push(line);return lines;};
const lines=(text,x,y,size,color,limit,leading=size*1.3)=>wrap(text,limit).map((s,i)=>`<text x="${x}" y="${y+i*leading}" fill="${color}" font-family="DejaVu Sans,Arial,sans-serif" font-size="${size}">${escape(s)}</text>`).join('');
const output=[];
for(const p of plans.filter(p=>(site==='qula'||p.haibu))){
 const supplied=path.join(workspace,'upload',p.source);
 const source=(site==='haibu' && neutral[p.sku])||supplied;
 const dest=site==='qula'?path.join(workspace,'qula',path.dirname(p.imagesLocal[0])):path.join(workspace,'haibu/assets/images/products/batch-2026-10-22',p.key);
 await fs.mkdir(dest,{recursive:true});
 const paths=site==='qula'?p.imagesLocal.map(r=>path.join(workspace,'qula',r)):Array.from({length:p.galleryLabels.length},(_,i)=>i+1).map(n=>path.join(dest,p.key+'-'+p.keywords+'-'+String(n).padStart(2,'0')+'.jpg'));
 const scale=Math.min(1,1000/p.sourceSize[0]);
 await sharp(source).rotate().resize({width:Math.round(p.sourceSize[0]*scale),height:Math.round(p.sourceSize[1]*scale),fit:'contain',background:'#fff',withoutEnlargement:true}).flatten({background:'#fff'}).jpeg({quality:85,mozjpeg:true}).toFile(paths[0]);
 if(p.photos.length===p.galleryLabels.length){
  for(let k=1;k<p.photos.length;k++) await sharp(path.join(workspace,'upload',p.photos[k])).rotate().resize({width:1000,withoutEnlargement:true}).flatten({background:'#fff'}).jpeg({quality:85,mozjpeg:true}).toFile(paths[k]);
  for(const f of paths){const data=await fs.readFile(f); if(data.subarray(6,11).toString()==='JFIF\0'){data[13]=1;data.writeUInt16BE(72,14);data.writeUInt16BE(72,16);await fs.writeFile(f,data);}else await fs.writeFile(f,Buffer.concat([data.subarray(0,2),Buffer.from('ffe000104a46494600010101004800480000','hex'),data.subarray(2)]));}
  const dimensions=await Promise.all(paths.map(async f=>{const m=await sharp(f).metadata();return {width:m.width,height:m.height}}));
  output.push({sku:p.sku,paths,dimensions,source,sourceSize:p.sourceSize});continue;
 }
 const b64=(await fs.readFile(paths[0])).toString('base64');
 const ink=site==='haibu'?'#1d4e43':'#8c3854',brand=site==='haibu'?'HAIBUCRAFT':'QULA CRAFT';
 for(const n of [2,3]){
  if(p.photos[n-1] && !p.sku.startsWith('MA')){await sharp(path.join(workspace,'upload',p.photos[n-1])).rotate().flatten({background:'#fff'}).jpeg({quality:85,mozjpeg:true}).toFile(paths[n-1]);continue;}
  const facts=n===2?[
   ['SOURCE DIMENSIONS',p.dimensions],['MATERIAL',p.material],['ATTACHMENT',p.attachment]
  ]:[['STANDARD PACK',p.packing],['ASSORTMENT','Confirm selected designs and mixing proportions'],['CUSTOM PACKING','Available by inquiry; confirm requirements'],['MOQ & DISPATCH','Confirm by quotation']];
 
  if(n===2 && p.sku.startsWith('MA')){
   let cells='';const count=p.photos.length,columns=3,cell=280,top=190;
   for(let j=0;j<count;j++){
    const buf=await sharp(path.join(workspace,'upload',p.photos[j])).rotate().resize({width:280,height:210,fit:'inside'}).flatten({background:'#fff'}).jpeg({quality:90}).toBuffer();
    const md=await sharp(buf).metadata();const x=50+(j%columns)*310,y=top+Math.floor(j/columns)*245;
    cells+=`<rect x="${x}" y="${y}" width="280" height="210" rx="12" fill="#fff"/><image x="${x+(280-md.width)/2}" y="${y+(210-md.height)/2}" width="${md.width}" height="${md.height}" xlink:href="data:image/jpeg;base64,${buf.toString('base64')}"/>${lines('Reference '+(j+1),x,y+230,16,ink,30)}`;
   }
   const svg=`<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="1000" height="1000"><rect width="1000" height="1000" fill="#f7f5f0"/>${lines(brand+' / '+p.sku,50,55,18,ink,70)}${lines('Supplied color references',50,110,36,'#172a2b',50)}${lines('Select reference numbers when requesting a quote.',50,150,20,'#526160',80)}${cells}${lines('Confirm selected colors, dimensions and assortment. Props are not included.',50,972,17,'#526160',95)}</svg>`;
   await sharp(Buffer.from(svg)).jpeg({quality:92,mozjpeg:true}).toFile(paths[n-1]);continue;
  }
 const title=n===2?'Size & attachment':'Packing & assortment';
  const foot=n===2?p.factNote:'Packing quantity is not the minimum order quantity. Send the full product code, selected designs, quantity and destination for quotation.';
  const metadata=await sharp(paths[0]).metadata();
  const photoScale=Math.min(1,490/metadata.width,580/metadata.height);
  const iw=metadata.width*photoScale,ih=metadata.height*photoScale;
  let y=190;
  let body=lines(p.title,565,y,23,'#172a2b',28,29);y+=wrap(p.title,28).length*29+12;
  for(const [a,b] of facts){body+=`<path d="M565 ${y-7}H952" stroke="#cbd5ce"/>`+lines(a,565,y+14,12,ink,40)+lines(b,565,y+40,18,'#172a2b',33,24);y+=46+wrap(b,33).length*24;}
  if(y>798)throw new Error('Fact graphic overflow: '+p.sku+' '+n+' '+y);
  const svg=`<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="1000" height="1000"><rect width="1000" height="1000" fill="#f7f5f0"/>${lines(brand+' / PRODUCT GUIDE',48,55,17,ink,80)}${lines(title,48,112,40,'#172a2b',45)}${lines(p.sku,48,153,18,'#526160',85,25)}<rect x="48" y="190" width="490" height="600" rx="18" fill="#fff"/><image x="${48+(490-iw)/2}" y="${200+(580-ih)/2}" width="${iw}" height="${ih}" preserveAspectRatio="xMidYMid meet" xlink:href="data:image/jpeg;base64,${b64}"/>${body}<rect x="48" y="816" width="904" height="125" rx="12" fill="#e8ede5"/>${lines(foot,70,842,16,'#172a2b',94,23)}${lines('Source specification summary. Styling props are not included. Confirm the selected sample.',48,972,14,'#566560',110)}</svg>`;
  await sharp(Buffer.from(svg)).jpeg({quality:90,mozjpeg:true}).toFile(paths[n-1]);
 }
 // JFIF resolution only: preserve encoded pixels and omit EXIF/GPS metadata.
 for(const f of paths){const data=await fs.readFile(f);if(data.subarray(6,11).toString()==='JFIF\0'){data[13]=1;data.writeUInt16BE(72,14);data.writeUInt16BE(72,16);await fs.writeFile(f,data);}else await fs.writeFile(f,Buffer.concat([data.subarray(0,2),Buffer.from('ffe000104a46494600010101004800480000','hex'),data.subarray(2)]));}
 const dimensions=await Promise.all(paths.map(async f=>{const m=await sharp(f).metadata();return {width:m.width,height:m.height}}));
 output.push({sku:p.sku,paths,dimensions,source,sourceSize:p.sourceSize});
}
await fs.writeFile(path.join(workspace,site+'-media-20261022.json'),JSON.stringify(output,null,2));
console.log(JSON.stringify({site,products:output.length,images:output.reduce((n,p)=>n+p.paths.length,0)}));
