#!/usr/bin/env node

import fs from 'node:fs';
import path from 'node:path';
import process from 'node:process';
import { fileURLToPath } from 'node:url';

const EXPECTED_EMAIL = 'sales@qulacrafts.com';
const EXPECTED_ACTION = `https://formsubmit.co/${EXPECTED_EMAIL}`;
const BACKUP_EMAIL = '64224336@qq.com';
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

    const forms = [...content.matchAll(/<form\b[^>]*\baction=["'](https:\/\/formsubmit\.co\/[^"']+)["'][^>]*>[\s\S]*?<\/form>/gi)];
    for (const match of forms) {
      formCount += 1;
      if (match[1].toLowerCase() !== EXPECTED_ACTION) {
        errors.push(`${name} submits to ${match[1]} instead of ${EXPECTED_ACTION}`);
      }
      const ccFields = [...match[0].matchAll(/<input\b[^>]*\bname=["']_cc["'][^>]*\bvalue=["']([^"']+)["'][^>]*>/gi)];
      if (ccFields.length !== 1 || ccFields[0][1].toLowerCase() !== BACKUP_EMAIL) {
        errors.push(`${name} must include exactly one _cc backup field for ${BACKUP_EMAIL}`);
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
  console.log(`Inquiry email protection passed for ${label}: ${formCount} forms and ${mailtoCount} email links use ${EXPECTED_EMAIL}; all forms copy to ${BACKUP_EMAIL}.`);
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
  if (!quoteScript.includes("const IS_PRODUCTION_HOST = /^(www\\.)?qulacrafts\\.com$/i.test(window.location.hostname);") ||
      !quoteScript.includes("if (!IS_PRODUCTION_HOST)") ||
      !quoteScript.includes("Preview validation passed — inquiry sending is disabled outside qulacrafts.com.")) {
    fail(['assets/js/quote-v2.js must block native FormSubmit delivery on preview hosts']);
  }
  if (!quoteScript.includes("nextField.value = 'https://qulacrafts.com/thank-you.html'")) {
    fail(['assets/js/quote-v2.js is missing the canonical production thank-you redirect']);
  }
  if (quoteScript.includes("new URL('thank-you.html', window.location.href).href")) {
    fail(['assets/js/quote-v2.js must not derive the thank-you redirect from the www hostname']);
  }
  console.log('Native multipart attachment safeguard passed.');
  if (quoteScript.includes("info.innerHTML = `<b>${file.name")) {
    fail(['assets/js/quote-v2.js must not render user-controlled file names through innerHTML']);
  }
  if (!quoteScript.includes("imageUrl.origin === window.location.origin") ||
      !quoteScript.includes("imageUrl.pathname.startsWith('/assets/')")) {
    fail(['assets/js/quote-v2.js must restrict product preview image parameters to local asset paths']);
  }
  console.log('Quote DOM-safety safeguard passed.');
  const mainScript = fs.readFileSync(path.join(ROOT, 'assets/js/main.js'), 'utf8');
  if (!mainScript.includes('function safeLocalImage(src)') ||
      !mainScript.includes("url.origin!==location.origin||!url.pathname.startsWith('/assets/')")) {
    fail(['assets/js/main.js must restrict inquiry-basket images to local assets']);
  }
  for (const page of ['index.html', 'quote.html']) {
    const html = fs.readFileSync(path.join(ROOT, page), 'utf8');
    if (!html.includes('assets/js/main.js?v=20261004-local-images')) {
      fail([`${page} must load the local-image-safe main script version`]);
    }
  }
  console.log('Inquiry basket image safeguard passed.');
  const inquiryExperience = fs.readFileSync(path.join(ROOT, 'assets/js/inquiry-experience.js'), 'utf8');
  if (!inquiryExperience.includes("const isProductionHost = /^(www\\.)?qulacrafts\\.com$/i.test(location.hostname);") ||
      !inquiryExperience.includes("form.dataset.previewSubmissionDisabled = 'true'") ||
      !inquiryExperience.includes("Preview validation passed — inquiry sending is disabled outside qulacrafts.com.")) {
    fail(['assets/js/inquiry-experience.js must block real FormSubmit delivery on preview hosts']);
  }
  if (!inquiryExperience.includes("const applicationField = field('application');") ||
      !inquiryExperience.includes("if (!applicationField.value) applicationField.value = applicationValue;")) {
    fail(['assets/js/inquiry-experience.js must prefill an existing application field from the application query parameter']);
  }
  const quoteHtml = fs.readFileSync(path.join(ROOT, 'quote.html'), 'utf8');
  for (const page of ['index.html', 'quote.html', 'contact.html', 'customization.html']) {
    const html = fs.readFileSync(path.join(ROOT, page), 'utf8');
    if (!html.includes('assets/js/inquiry-experience.js?v=20261005-preview-safe')) {
      fail([`${page} must load the preview-safe inquiry script version`]);
    }
  }
  for (const page of ['index.html', 'quote.html']) {
    const html = fs.readFileSync(path.join(ROOT, page), 'utf8');
    if (!html.includes('assets/js/quote-v2.js?v=20261005-preview-safe')) {
      fail([`${page} must load the preview-safe quote script version`]);
    }
  }
  console.log('Application-context prefill safeguard passed.');
  const analyticsSource = fs.readFileSync(path.join(ROOT, 'assets/js/analytics.js'), 'utf8');
  if (!analyticsSource.includes("IS_CANONICAL_ANALYTICS_HOST") ||
      !analyticsSource.includes("/^(www\\.)?qulacrafts\\.com$/i.test(window.location.hostname)")) {
    fail(['assets/js/analytics.js must block non-production hosts from the production GA4 property']);
  }
  if (!analyticsSource.includes("gtag('event','inquiry_submit_attempt'") ||
      !analyticsSource.includes("gtag('event','generate_lead'") ||
      analyticsSource.includes("gtag('event','inquiry_accepted'") ||
      !analyticsSource.includes("/\\/thank-you\\.html$/") ||
      !analyticsSource.includes('QULA_MARK_INQUIRY_PENDING')) {
    fail(['assets/js/analytics.js must keep submit attempts separate and emit exactly one confirmed generate_lead return']);
  }
  if (!quoteScript.includes("QULA_MARK_INQUIRY_PENDING")) {
    fail(['assets/js/quote-v2.js must mark a pending inquiry only before native FormSubmit POST']);
  }
  for (const page of ['index.html', 'quote.html', 'contact.html', 'customization.html', 'thank-you.html']) {
    const html = fs.readFileSync(path.join(ROOT, page), 'utf8');
    if (!html.includes('assets/js/analytics.js?v=20261005-single-lead')) {
      fail([`${page} must load the confirmed-lead analytics script version`]);
    }
  }
  console.log('Confirmed-lead tracking safeguard passed.');
  const productionGuard = fs.readFileSync(path.join(ROOT, '.github/workflows/protect-inquiry-email.yml'), 'utf8');
  if (/contents:\s*write/.test(productionGuard) || /git\s+push\s+origin\s+HEAD:main/.test(productionGuard)) {
    fail(['production monitor must not write to main or trigger production recovery automatically']);
  }
  if (!productionGuard.includes('Manual review and explicit approval are required before any production change.')) {
    fail(['production monitor must state that explicit approval is required']);
  }
  console.log('Production-approval safeguard passed.');
}