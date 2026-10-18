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
