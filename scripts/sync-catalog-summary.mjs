import fs from 'node:fs';
import path from 'node:path';
const root=process.cwd();
const check=process.argv.includes('--check');
const catalog=JSON.parse(fs.readFileSync(path.join(root,'assets/data/product-catalog.json'),'utf8'));
const total=catalog.categories.reduce((n,c)=>n+c.products.length,0);
const stale=[];
function save(file,next){
 const location=path.join(root,file);const old=fs.readFileSync(location,'utf8').replace(/\r\n/g,'\n');
 if(old===next)return;
 if(check)stale.push(file);else fs.writeFileSync(location,next);
}
let summary=fs.readFileSync(path.join(root,'llms.txt'),'utf8').replace(/\r\n/g,'\n');
const urls={
 'slime-charms':'slime-charms.html','polymer-clay-slices':'polymer-clay-sprinkles.html',
 'plastic-sequins':'glitter-sequins-fillers.html','resin-charms':'resin-charms.html',
 'pvc-plastic-charms':'pvc-plastic-charms.html','plastic-beads':'acrylic-beads.html',
 'beads-for-pens':'beads-for-pens.html','decorative-craft-accessories':'decorative-craft-accessories.html','keychain':'keychain.html','jewelry-accessories':'jewelry-accessories.html'
};
const lines=catalog.categories.map(c=>{
 const url=urls[c.slug];if(!url)throw new Error('Missing original category URL: '+c.slug);
 return `- [${c.name}](https://www.qulacrafts.com/${url}): ${c.products.length} catalog entries. Confirm specifications, pack units, MOQ, price and availability by SKU.`;
});
summary=summary.replace(/## Products \([^\n]*\)[\s\S]*?(?=- \[Seasonal Collections\])/,
 `## Products (${catalog.categories.length} categories, ${total} catalog entries)\n${lines.join('\n')}\n`);
save('llms.txt',summary);
let full=fs.readFileSync(path.join(root,'llms-full.txt'),'utf8').replace(/\r\n/g,'\n');
full=full.replace(/^# Qula Craft[^\n]*full product index[^\n]*/m,`# Qula Craft — full product index (${total} catalog entries)`);
save('llms-full.txt',full);
const indexed=new Set([...full.matchAll(/\]\(https:\/\/www\.qulacrafts\.com\/(p-[^)]+\.html)\)/g)].map(m=>m[1]));
for(const category of catalog.categories)for(const p of category.products){
 if(!indexed.has(p.pdp))throw new Error('Product missing from full index: '+p.sku);
}
if(stale.length)throw new Error(`Catalog summary needs synchronization: ${stale.join(', ')}. Run node scripts/sync-catalog-summary.mjs and commit the result.`);
console.log(`Catalog summary ${check?'check':'sync'} passed: ${total} catalog entries.`);
