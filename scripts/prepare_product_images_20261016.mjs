// Encode the already-generated assets for the website; do not redraw products.
import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import { createRequire } from 'node:module';
import { fileURLToPath } from 'node:url';

const require = createRequire(import.meta.url);
let sharp;
try { sharp = require('sharp'); }
catch { sharp = require(path.join(process.env.CODEX_PRIMARY_RUNTIME_NODE_MODULES, 'sharp')); }
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const [planPath, uploadDir] = process.argv.slice(2);
if (!planPath || !uploadDir) throw new Error('Usage: prepare_product_images_20261012.mjs PLAN_JSON SOURCE_IMAGE_DIRECTORY');
const plans = JSON.parse(await fs.readFile(planPath, 'utf8'));

function removeExifAndText(buffer, format) {
  if (format === 'png') {
    const chunks = [buffer.subarray(0, 8)];
    for (let pos = 8; pos < buffer.length;) {
      const length = buffer.readUInt32BE(pos);
      const type = buffer.toString('ascii', pos + 4, pos + 8);
      const end = pos + length + 12;
      if (!['eXIf', 'tEXt', 'zTXt', 'iTXt'].includes(type)) chunks.push(buffer.subarray(pos, end));
      pos = end;
    }
    return Buffer.concat(chunks);
  }
  // Keep a 72 PPI JFIF resolution record without retaining EXIF/GPS.
  const jfif = Buffer.from([0xff,0xe0,0x00,0x10,0x4a,0x46,0x49,0x46,0x00,0x01,0x01,0x01,0x00,0x48,0x00,0x48,0x00,0x00]);
  const chunks = [buffer.subarray(0, 2), jfif];
  let pos = 2;
  while (pos < buffer.length) {
    if (buffer[pos] !== 0xff) throw new Error('Invalid JPEG metadata stream');
    const marker = buffer[pos + 1];
    if (marker === 0xda || marker === 0xd9) { chunks.push(buffer.subarray(pos)); break; }
    const end = pos + 2 + buffer.readUInt16BE(pos + 2);
    // APP1 holds EXIF/XMP, while APP2 ICC and APP0 resolution are retained.
    if (marker !== 0xe1 && marker !== 0xe0) chunks.push(buffer.subarray(pos, end));
    pos = end;
  }
  return Buffer.concat(chunks);
}

for (const plan of plans) {
  const dir = path.join(root, 'assets/images/pdp', plan.key);
  await fs.mkdir(dir, { recursive: true });
  plan.imagesLocal = [];
  const source = path.join(uploadDir, plan.source);
  plan.sourceImageSha256 = crypto.createHash('sha256').update(await fs.readFile(source)).digest('hex');
  for (const role of [1, 2, 3]) {
    const input = plan.generatedPaths[String(role)] || (role === 1 ? source : null);
    if (!input) throw new Error(`${plan.sku}: missing generated image ${role}`);
    const metadata = await sharp(input).metadata();
    const width = Math.min(1000, metadata.width);
    const stats = role === 1 && metadata.hasAlpha ? await sharp(input).stats() : null;
    const transparent = stats && stats.channels[metadata.channels - 1].min < 255;
    const format = role === 1 && transparent ? 'png' : 'jpeg';
    const name = `${plan.key}-${role}-${plan.keywords}${role === 1 ? '' : role === 2 ? '-scene' : '-detail'}.${format === 'png' ? 'png' : 'jpg'}`;
    let pipeline = sharp(input).resize({ width, withoutEnlargement: true }).withIccProfile('srgb').withMetadata({ density: 72 });
    pipeline = format === 'png' ? pipeline.png({ compressionLevel: 9, palette: true, quality: 90, effort: 9 }) : pipeline.flatten({ background: '#ffffff' }).jpeg({ quality: 85, mozjpeg: true });
    const buffer = removeExifAndText(await pipeline.toBuffer(), format);
    const output = path.join(dir, name);
    await fs.writeFile(output, buffer);
    const saved = await sharp(output).metadata();
    if (saved.width !== width || saved.height !== Math.round(metadata.height * width / metadata.width)) throw new Error(`${plan.sku}: unexpected image dimensions`);
    if (saved.exif) throw new Error(`${plan.sku}: EXIF was not removed`);
    plan.imagesLocal.push(path.relative(root, output).replaceAll(path.sep, '/'));
    console.log(`${plan.sku} image ${role}: ${saved.width}x${saved.height}, ${Math.round(buffer.length / 1024)} KB`);
  }
}
await fs.writeFile(planPath, JSON.stringify(plans, null, 2) + '\n');
