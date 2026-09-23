import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const key = '4e316ddf27bc705d6d3edbf5bcabf6e4';
const keyFile = `${key}.txt`;
const failures = [];

const keyPath = path.join(root, keyFile);
if (!fs.existsSync(keyPath)) failures.push(`missing ${keyFile}`);
else if (fs.readFileSync(keyPath, 'utf8').trim() !== key) failures.push(`${keyFile} content does not match configured key`);

const workflowPath = path.join(root, '.github', 'workflows', 'indexnow.yml');
if (!fs.existsSync(workflowPath)) failures.push('missing .github/workflows/indexnow.yml');
else {
  const workflow = fs.readFileSync(workflowPath, 'utf8');
  for (const required of ['scripts/submit-indexnow.mjs', 'Wait for Vercel production']) {
    if (!workflow.includes(required)) failures.push(`indexnow workflow missing: ${required}`);
  }
}

const submitPath = path.join(root, 'scripts', 'submit-indexnow.mjs');
if (!fs.existsSync(submitPath)) failures.push('missing scripts/submit-indexnow.mjs');
else {
  const submit = fs.readFileSync(submitPath, 'utf8');
  if (!submit.includes('www.qulacrafts.com')) failures.push('IndexNow submitter host is not canonical www host');
  if (!submit.includes('https://api.indexnow.org/indexnow')) failures.push('IndexNow submitter endpoint is missing');
  if (!submit.includes(keyFile)) failures.push('IndexNow submitter does not reference hosted key file');
}

const robots = fs.readFileSync(path.join(root, 'robots.txt'), 'utf8');
if (!robots.includes('Sitemap: https://www.qulacrafts.com/sitemap.xml')) {
  failures.push('robots.txt sitemap does not use canonical host');
}

if (failures.length) {
  console.error(`IndexNow checks failed (${failures.length}):`);
  for (const failure of failures) console.error(`- ${failure}`);
  process.exit(1);
}

console.log('IndexNow checks passed: key file, canonical host, workflow and submitter are consistent.');
