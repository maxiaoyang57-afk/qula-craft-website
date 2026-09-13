#!/usr/bin/env node

import fs from 'node:fs';
import path from 'node:path';
import process from 'node:process';
import { fileURLToPath } from 'node:url';

const EXPECTED_EMAIL = 'sales@qulacrafts.com';
const EXPECTED_ACTION = `https://formsubmit.co/${EXPECTED_EMAIL}`;
const FORBIDDEN_EMAILS = ['sale008@sola-craft.com', 'monica@qulacrafts.com'];
const EXPECTED_FORM_COUNT = 4;
const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');

function fail(messages) {
  console.error('\nInquiry email protection failed:');
  for (const message of messages) console.error(`- ${message}`);
  process.exit(1);
}

function checkHtmlDocuments(documents, label, expectedFormCount) {
  const errors = [];
  let formCount = 0;
  let mailtoCount = 0;

  for (const { name, content } of documents) {
    const lower = content.toLowerCase();

    for (const forbidden of FORBIDDEN_EMAILS) {
      if (lower.includes(forbidden)) {
        errors.push(`${name} contains forbidden address ${forbidden}`);
      }
    }

    const actions = [...content.matchAll(/action=["'](https:\/\/formsubmit\.co\/[^"']+)["']/gi)];
    for (const match of actions) {
      formCount += 1;
      if (match[1].toLowerCase() !== EXPECTED_ACTION) {
        errors.push(`${name} submits to ${match[1]} instead of ${EXPECTED_ACTION}`);
      }
    }

    const mailtos = [...content.matchAll(/href=["']mailto:([^?"']+)/gi)];
    for (const match of mailtos) {
      mailtoCount += 1;
      if (match[1].toLowerCase() !== EXPECTED_EMAIL) {
        errors.push(`${name} links to mailto:${match[1]} instead of ${EXPECTED_EMAIL}`);
      }
    }
  }

  if (formCount !== expectedFormCount) {
    errors.push(`${label} has ${formCount} FormSubmit forms; expected ${expectedFormCount}`);
  }
  if (mailtoCount === 0) {
    errors.push(`${label} has no mailto:${EXPECTED_EMAIL} links`);
  }

  if (errors.length) fail(errors);
  console.log(`Inquiry email protection passed for ${label}: ${formCount} forms and ${mailtoCount} email links use ${EXPECTED_EMAIL}.`);
}

function collectLocalHtml(directory) {
  return fs.readdirSync(directory, { withFileTypes: true })
    .filter((entry) => entry.isFile() && entry.name.endsWith('.html'))
    .map((entry) => ({
      name: entry.name,
      content: fs.readFileSync(path.join(directory, entry.name), 'utf8'),
    }));
}

if (process.argv[2] === '--live') {
  const liveFile = process.argv[3];
  if (!liveFile) fail(['--live requires the downloaded homepage path']);
  checkHtmlDocuments(
    [{ name: 'production homepage', content: fs.readFileSync(liveFile, 'utf8') }],
    'production homepage',
    1,
  );
} else {
  checkHtmlDocuments(collectLocalHtml(ROOT), 'repository', EXPECTED_FORM_COUNT);

  const quoteScript = fs.readFileSync(path.join(ROOT, 'assets/js/quote-v2.js'), 'utf8');
  if (quoteScript.includes('formsubmit.co/ajax/') || quoteScript.includes('fetch(ajaxEndpoint')) {
    fail(['assets/js/quote-v2.js must not use the FormSubmit AJAX endpoint because it drops attachments']);
  }
  if (!quoteScript.includes('MAX_ATTACHMENT_BYTES = 10 * 1024 * 1024')) {
    fail(['assets/js/quote-v2.js is missing the 10MB total attachment limit']);
  }
  if (!quoteScript.includes('HTMLFormElement.prototype.submit.call(form)')) {
    fail(['assets/js/quote-v2.js is missing verified native multipart submission']);
  }
  console.log('Native multipart attachment safeguard passed.');
}
