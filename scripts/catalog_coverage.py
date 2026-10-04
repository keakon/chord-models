#!/usr/bin/env python3
"""Validate the inventory and report six calendar months of discovery gaps.

Only reads sources. Never promotes a discovery record into runtime defaults.
Python 3.11+; no third-party dependencies.
"""
import argparse
import calendar
import collections
import datetime as dt
import json
from pathlib import Path
import re
import tomllib


def window_start(day, months=6):
    month_index = day.year * 12 + day.month - 1 - months
    year, month = divmod(month_index, 12)
    month += 1
    return dt.date(year, month, min(day.day, calendar.monthrange(year, month)[1]))


def date(value):
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        raise ValueError(f"invalid calendar date: {value!r}")
    return dt.date.fromisoformat(value)


def validate(root, catalog, inventory, as_of):
    if inventory['schema_version'] != 1 or inventory['window_months'] != 6:
        raise ValueError('unsupported inventory schema or maintenance window')
    reviewed = date(inventory['as_of'])
    if reviewed > as_of:
        raise ValueError('inventory review cannot be in the future')
    models = {m['id']: m for m in catalog['models']}
    seen, candidates = set(), set()
    for e in inventory['entries']:
        mid = e['id']
        if mid in seen or not re.fullmatch(r'[A-Za-z0-9._-]+/[A-Za-z0-9._-]+', mid):
            raise ValueError(f'invalid or duplicate identity: {mid}')
        seen.add(mid)
        vendor = mid.split('/')[0]
        if vendor not in inventory['watchlist']:
            raise ValueError(f'no vendor watch entry: {vendor}')
        if date(e['checked']) > reviewed or not e['reason'].strip():
            raise ValueError(f'invalid check date or missing decision reason: {mid}')
        for key in ('released', 'reported_release'):
            if e.get(key) and date(e[key]) > reviewed:
                raise ValueError(f'future release in reviewed inventory: {mid}')
        if not e['sources'] or any(not s['url'].startswith('https://') or date(s['checked']) > reviewed for s in e['sources']):
            raise ValueError(f'invalid evidence: {mid}')
        if e['state'] == 'model':
            if mid not in models or e.get('released') != models[mid].get('released'):
                raise ValueError(f'model missing or official release differs: {mid}')
        elif e['state'] == 'candidate':
            expected = 'candidates/' + mid.replace('/', '--') + '.yaml'
            if e['candidate'] != expected or not (root / expected).is_file():
                raise ValueError(f'candidate missing or identity differs: {mid}')
            candidates.add(expected)
        elif e['state'] != 'excluded':
            raise ValueError(f'unknown inventory state: {mid}')
    missing = set(models) - seen
    files = {p.relative_to(root).as_posix() for p in (root / 'candidates').glob('*.yaml')}
    if missing or files != candidates:
        raise ValueError(f'untracked model facts: {sorted(missing)}; candidate inventory differs: {sorted(files ^ candidates)}')


def discoveries(registry, as_of):
    start = window_start(as_of)
    for f in sorted((registry / 'models').glob('*/*.toml')):
        d = tomllib.loads(f.read_text())
        released = str(d.get('release_date', ''))
        # A missing date is also a gap: do not silently claim an entire family
        # was covered because its newest model has no registry release date.
        if d.get('tool_call') and 'text' in d.get('modalities', {}).get('output', []):
            if not released or start <= date(released) <= as_of:
                yield {'id': f.parent.name + '/' + f.stem, 'reported_release': released or None}


def report(inventory, catalog, as_of, registry=None):
    start = window_start(as_of)
    entries = inventory['entries']
    counts = collections.Counter(e['state'] for e in entries)
    unresolved = [e['id'] for e in entries if e['state'] != 'excluded' and not e.get('released')]
    known = {e['id'] for e in entries}
    new = [d for d in discoveries(registry, as_of) if d['id'] not in known] if registry else []
    ready = [m['id'] for m in catalog['models'] if m.get('connection') or any(b['model_id'] == m['id'] for b in catalog['bindings'])]
    return {'as_of': str(as_of), 'window_start': str(start), 'inventory_reviewed': inventory['as_of'],
            'review_age_days': (as_of - date(inventory['as_of'])).days,
            'counts': dict(counts), 'one_command_models': ready,
            'official_release_dates_missing': unresolved, 'new_discoveries': new,
            'complete': not unresolved and not new and all(w['review'] == 'complete' for w in inventory['watchlist'].values())}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--catalog', type=Path, required=True, help='validated JSON from chord modelcatalog-gen')
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parent.parent)
    parser.add_argument('--as-of', type=date, default=dt.datetime.now(dt.timezone.utc).date())
    parser.add_argument('--models-dev', type=Path, help='optional models.dev checkout for broad discovery hints')
    parser.add_argument('--max-review-age', type=int, help='fail if the inventory has not been reviewed within this many days')
    args = parser.parse_args()
    inventory = json.loads((args.root / 'coverage.json').read_text())
    catalog = json.loads(args.catalog.read_text())
    try:
        validate(args.root, catalog, inventory, args.as_of)
        result = report(inventory, catalog, args.as_of, args.models_dev)
        print(json.dumps(result, indent=2))
        if args.max_review_age is not None and result['review_age_days'] > args.max_review_age:
            parser.exit(1, 'Inventory review is overdue; review official releases and discovery gaps.\n')
    except (ValueError, KeyError) as exc:
        parser.exit(1, f'Coverage validation failed: {exc}\n')


if __name__ == '__main__':
    main()
