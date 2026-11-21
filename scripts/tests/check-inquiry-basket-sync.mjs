import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

const source = fs.readFileSync(new URL('../../assets/js/main.js', import.meta.url), 'utf8');
const start = source.indexOf('    let previousSkus=[];');
const end = source.indexOf('    async function renderPanel(){', start);
assert.ok(start >= 0 && end > start, 'Basket message synchronizer is present');
const state = { ta: { value: 'Please quote 500 pieces.\n- Keep my custom packaging note.', dispatchEvent() {} }, items: [] };
const context = vm.createContext({
  ta: state.ta,
  load: () => state.items,
  normalizeList: list => list,
  Event,
  location:{origin:'https://www.qulacrafts.com'},
});
vm.runInContext(source.slice(start, end), context);
const sync = () => vm.runInContext('syncTa()', context);
const notes = state.ta.value;

state.ta.value = 'Inquiry list:\n- MA612: 900 pcs in my own draft\n\nKeep this draft.';
const ownDraft = state.ta.value;
state.items = [{ sku: 'MA612' }];
sync();
state.items = [];
sync();
assert.equal(state.ta.value, ownDraft, 'Initial customer text is not claimed even when its SKU matches the basket');
state.ta.value = notes;

state.items = [{ sku: 'MA612' }, { sku: 'RW001884' }];
sync();
assert.equal(state.ta.value, 'Inquiry list:\n- MA612\n- RW001884\n\n' + notes);
sync();
assert.equal(state.ta.value, 'Inquiry list:\n- MA612\n- RW001884\n\n' + notes, 'Repeated rendering does not duplicate SKUs');
state.items = [{ sku: 'RW001884' }];
sync();
assert.equal(state.ta.value, 'Inquiry list:\n- RW001884\n\n' + notes, 'Removing one item removes only its generated line');
state.items = [];
sync();
assert.equal(state.ta.value, notes, 'Clearing the basket preserves customer requirements');
state.items = [{ sku: 'MA612' }];
sync();
state.ta.value = 'Inquiry list:\r\n- MA612: 500 pieces\r\n- Keep this extra note\r\n\r\n' + notes;
sync();
assert.ok(state.ta.value.includes('- MA612: 500 pieces'), 'Quantity edits survive repeated synchronization');
state.items = [];
sync();
assert.equal(state.ta.value, '- Keep this extra note\n\n' + notes, 'CRLF removal preserves unrecognized customer bullet points');
state.ta.value = 'Inquiry list:\n- My own list item\n\n' + notes;
sync();
assert.equal(state.ta.value, 'Inquiry list:\n- My own list item\n\n' + notes, 'A customer-written Inquiry list block is not owned by the basket');
state.ta.value = '';
state.items = [{ sku: 'MA612' }];
sync();
state.items = [];
sync();
assert.equal(state.ta.value, '', 'Removing the last item leaves no stale SKU');
state.ta.value = '- Keep my bullet-point request.';
state.items = [{ sku: 'MA612' }];
sync();
state.items = [];
sync();
assert.equal(state.ta.value, '- Keep my bullet-point request.', 'Customer bullet points are separate from generated SKU lines');
console.log('Inquiry basket synchronization passed: add, repeated render, remove, clear, notes, and CRLF.');

state.ta.value='Please pack the two references separately.';
state.items=[
  {sku:'YM109',productPath:'/p-ym109.html',title:'First PET tube reference',category:'Plastic Sequins'},
  {sku:'YM109',productPath:'/p-ym109-2.html',title:'Second PET tube reference',category:'Plastic Sequins'}
];
sync();
assert.ok(state.ta.value.includes('First PET tube reference | https://www.qulacrafts.com/p-ym109.html'));
assert.ok(state.ta.value.includes('Second PET tube reference | https://www.qulacrafts.com/p-ym109-2.html'));
state.ta.value=state.ta.value.replace('p-ym109-2.html | Plastic Sequins','p-ym109-2.html | Plastic Sequins: 2 bags');
sync();
state.items=state.items.slice(1);
sync();
assert.ok(!state.ta.value.includes('First PET tube reference'),'Removing one reference does not remove or retain the wrong same-SKU line');
assert.ok(state.ta.value.includes('Second PET tube reference')&&state.ta.value.includes('2 bags'),'The other reference and edited quantity survive');
state.items=[];sync();
assert.equal(state.ta.value,'Please pack the two references separately.','Clearing both variants preserves the buyer requirements');


state.ta.value='Please pack separately.\n- My own packaging request.';
const packing=state.ta.value;
state.items=[{sku:'RW26808',productPath:'/p-rw26808-acorn.html',title:'Smiling Acorn Resin Flatback Charms',category:'Resin Charms'},{sku:'RW20809',productPath:'/p-rw20809.html',title:'Pig and Cabbage Resin Flatback Charms',category:'Resin Charms'}];
sync();
state.ta.value='Inquiry list:\r\n- RW26808: 700 pcs\r\n- RW20809: 200 packs\r\n- Keep my custom mix: 雪 & stars\r\n\r\n'+packing;
sync();
assert.equal((state.ta.value.match(/Inquiry list:/g)||[]).length,1,'Replacing full lines with unique SKU quantities does not duplicate the list');
assert.ok(state.ta.value.includes('RW26808: 700 pcs')&&state.ta.value.includes('RW20809: 200 packs'));
state.items=state.items.slice(1);sync();
assert.ok(!state.ta.value.includes('RW26808'),'Removed product does not remain in a buyer-edited quantity line');
assert.ok(state.ta.value.includes('RW20809: 200 packs')&&state.ta.value.includes('Keep my custom mix: 雪 & stars'));
state.items=[];sync();
assert.equal(state.ta.value,'- Keep my custom mix: 雪 & stars\n\n'+packing,'Clear removes remaining quantity and preserves buyer notes');
