import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

const source = fs.readFileSync(new URL('../../assets/js/main.js', import.meta.url), 'utf8');
const start = source.indexOf('    function syncTa(){');
const end = source.indexOf('    async function renderPanel(){', start);
assert.ok(start >= 0 && end > start, 'Basket message synchronizer is present');
const state = { ta: { value: 'Please quote 500 pieces.\n- Keep my custom packaging note.' }, items: [] };
const context = vm.createContext({
  ta: state.ta,
  load: () => state.items,
  normalizeList: list => list,
});
vm.runInContext(source.slice(start, end), context);
const sync = () => vm.runInContext('syncTa()', context);
const notes = state.ta.value;

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
state.ta.value = 'Inquiry list:\r\n- MA612\r\n\r\n' + notes;
sync();
assert.equal(state.ta.value, notes, 'Windows line endings also synchronize');
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
