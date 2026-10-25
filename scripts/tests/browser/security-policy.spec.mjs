import { test, expect } from '@playwright/test';
import { readFileSync } from 'node:fs';

const config=JSON.parse(readFileSync('vercel.json','utf8'));
const policy=config.headers.flatMap(rule=>rule.headers).find(header=>header.key==='Content-Security-Policy')?.value;

test('production CSP protects the base URL and keeps the existing inquiry delivery target',async({page})=>{
  expect(policy).toContain("base-uri 'self'");
  expect(policy).toContain("object-src 'none'");
  expect(policy).toContain("form-action 'self' https://formsubmit.co;");
  await page.route('**/formsubmit.co/**',route=>route.abort());
  await page.route('**/customization.html',async route=>{
    const response=await route.fetch();
    await route.fulfill({response,headers:{...response.headers(),'content-security-policy':policy}});
  });
  await page.goto('customization.html');
  await expect(page.locator('h1')).toBeVisible();
  const action=await page.locator('#custom-project-inquiry').getAttribute('action');
  expect(new URL(action).origin).toBe('https://formsubmit.co');
  const baseBefore=await page.evaluate(()=>document.baseURI);
  await page.evaluate(()=>{
    window.__policyViolations=[];
    document.addEventListener('securitypolicyviolation',event=>window.__policyViolations.push(event.violatedDirective));
    const base=document.createElement('base');base.href='https://example.invalid/';document.head.append(base);
  });
  await expect.poll(()=>page.evaluate(()=>window.__policyViolations)).toContain('base-uri');
  expect(await page.evaluate(()=>document.baseURI)).toBe(baseBefore);
  await expect(page.locator('#custom-project-inquiry textarea[name="message"]')).toBeEnabled();
});
