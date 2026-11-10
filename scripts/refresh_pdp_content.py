"""Update reviewed content without rebuilding existing PDP shells or links."""
import html
import json
import re
from pathlib import Path

from pdp_content import buying_copy, product_summary, render_buying_guide
from pdp_public_copy import CONTENT_REVIEWS, is_generic_occasion_list, public_specs

ROOT = Path(__file__).resolve().parents[1]


def refresh():
    entries = json.loads((ROOT / 'assets/data/pdp-data.json').read_text())
    copies = json.loads((ROOT / 'assets/data/pdp-copy.json').read_text())
    catalog = json.loads((ROOT / 'assets/data/product-catalog.json').read_text())
    public = {p['pdp'] for c in catalog['categories'] for p in c['products']}
    changes = {}
    for entry in entries:
        key = entry['assetKey']
        path = ROOT / f'p-{key}.html'
        if path.name not in public:
            continue
        original = path.read_text()
        text = original
        reasons = []
        copy = copies[key]
        summary = product_summary(entry, copy)
        existing = re.search(r'<p class="pdp-summary">(.*?)</p>', text, re.S)
        old = html.unescape(existing.group(1)) if existing else ''
        if summary and summary != old:
            paragraph = '<p class="pdp-summary">' + html.escape(summary, quote=True) + '</p>'
            if existing:
                text = text[:existing.start()] + paragraph + text[existing.end():]
            else:
                text = re.sub(r'(<h1[^>]*>.*?</h1>)', lambda m: m.group(1) + '\n  ' + paragraph, text, count=1, flags=re.S)
            reasons.append('unique_intro' if key in CONTENT_REVIEWS else 'deduplicate_intro')
        advice = buying_copy(entry, copy)
        if key in CONTENT_REVIEWS or any(advice[k] != copy.get(k, '') for k in advice):
            section = render_buying_guide(entry, copy)
            pattern = r'<section class="section" data-product-buying-guide="[^"]+">.*?</section>'
            match = re.search(pattern, text, re.S)
            if match:
                if match.group(0) != section:
                    text = text[:match.start()] + section + text[match.end():]
                    reasons.append('deduplicate_or_review_advice')
            else:
                marker = '<section class="section section-soft">'
                assert marker in text, key
                text = text.replace(marker, section + '\n' + marker, 1)
                reasons.append('reviewed_buying_advice')
        published_specs = public_specs(entry)
        for name in ('Application', *CONTENT_REVIEWS.get(key, {}).get('specOverrides', {})):
            pattern = r'<tr><td><b>' + re.escape(name) + r'</b></td><td>.*?</td></tr>'
            row = re.search(pattern, text, re.S)
            if not row:
                continue
            replacement = ('<tr><td><b>' + name + '</b></td><td>' + html.escape(str(published_specs[name]), quote=True) + '</td></tr>') if name in published_specs else ''
            # Only the catch-all Application field and explicitly reviewed facts change.
            if name == 'Application' and not is_generic_occasion_list(html.unescape(re.sub('<[^>]+>', '', row.group(0)))):
                continue
            if row.group(0) != replacement:
                text = text[:row.start()] + replacement + text[row.end():]
                reasons.append('remove_generic_occasions' if name == 'Application' else 'owner_confirmed_material')
        def schema_update(match):
            data = json.loads(match.group(1))
            if data.get('@type') != 'Product':
                return match.group(0)
            old_data = json.dumps(data, sort_keys=True)
            data['additionalProperty'] = [p for p in data.get('additionalProperty', []) if not (p.get('name') == 'Application' and is_generic_occasion_list(p.get('value', '')))]
            overrides = CONTENT_REVIEWS.get(key, {}).get('specOverrides', {})
            if 'Material' in overrides:
                data['material'] = overrides['Material']
            if json.dumps(data, sort_keys=True) == old_data:
                return match.group(0)
            return '<script type="application/ld+json">' + json.dumps(data, ensure_ascii=False, separators=(',', ':')) + '</script>'
        text = re.sub(r'<script type="application/ld\+json">(.*?)</script>', schema_update, text, flags=re.S)
        if text != original:
            assert reasons, key
            path.write_text(text)
            changes[path.name] = reasons
    return changes


if __name__ == '__main__':
    changed = refresh()
    print(json.dumps({'changed_pages': len(changed), 'reasons': {reason: sum(reason in reasons for reasons in changed.values()) for reason in sorted({r for reasons in changed.values() for r in reasons})}, 'pages': changed}, indent=2))
