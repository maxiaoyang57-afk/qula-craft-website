// Convert supplied catalog references proportionally; preserve all individual product pixels.
import fs from 'node:fs/promises';
import path from 'node:path';
import { createRequire } from 'node:module';
const require=createRequire(path.join(process.env.CODEX_PRIMARY_RUNTIME_NODE_MODULES,'placeholder.js'));
const sharp=require('sharp');
const root=path.resolve(import.meta.dirname,'..');
const workspace=path.resolve(process.argv[2]||'..');
const edits=JSON.parse(await fs.readFile(path.join(workspace,'heart-edit-paths.json'),'utf8'));
const planPath=path.join(root,'scripts/data/product-plan-20261019-heart-keychains.json');
const plans=JSON.parse(await fs.readFile(planPath,'utf8'));
for(let i=0;i<plans.length;i++){
 const p=plans[i];
 for(let j=0;j<p.photos.length;j++){
  const original=path.join(workspace,'upload',p.photos[j]);
  const edited=j===0&&p.sourceRow!==205;
  const source=edited?edits[i]:original;
  const dims=await sharp(original).metadata();
  const maxWidth=Math.min(1000,dims.width);
  const destination=path.join(root,p.imagesLocal[j]);await fs.mkdir(path.dirname(destination),{recursive:true});
  await sharp(source).rotate().resize({width:maxWidth,withoutEnlargement:true}).flatten({background:'#fff'}).jpeg({quality:85,mozjpeg:true}).toFile(destination);
  const data=await fs.readFile(destination);
  if(data.subarray(6,11).toString()==='JFIF\0'){data[13]=1;data.writeUInt16BE(72,14);data.writeUInt16BE(72,16);await fs.writeFile(destination,data);}
  else await fs.writeFile(destination,Buffer.concat([data.subarray(0,2),Buffer.from('ffe000104a46494600010101004800480000','hex'),data.subarray(2)]));
 }
}
console.log(JSON.stringify({groups:plans.length,images:plans.reduce((n,p)=>n+p.imagesLocal.length,0)}));
