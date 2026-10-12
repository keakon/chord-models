#!/usr/bin/env python3
"""Notify new watch-listed model discoveries via a single tracking issue.

Reads the discovery report's `new_discoveries` (already narrowed to the
notification watch list) and diffs it against the ids already recorded in the
tracking issue body. Only unseen models are appended; the issue itself is the
persistent seen-state, so the workflow never re-notifies the same model.

Notification failures must not fail the CI job: discovery is best-effort
signal, not a release gate. Any gh problem is logged and the process exits 0.
Python 3.11+; depends only on the `gh` CLI being on PATH and authenticated.
"""
import argparse
import json
import re
import subprocess
import sys
from datetime import date

ISSUE_TITLE = 'Model discovery feed'
MARKER_RE = re.compile(r'<!-- seen: (.*?) -->')


def gh(args):
    proc = subprocess.run(['gh'] + args, capture_output=True, text=True)
    return proc


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report', required=True, help='coverage-report.json from catalog_coverage.py')
    parser.add_argument('--repo', required=True, help='owner/name of the GitHub repository')
    args = parser.parse_args()

    report = json.load(open(args.report))
    new = report.get('new_discoveries') or []
    if not new:
        print('no new discoveries; nothing to notify')
        return

    # Locate the existing tracking issue (if any).
    proc = gh(['issue', 'list', '--repo', args.repo, '--state', 'open',
               '--search', ISSUE_TITLE, '--limit', '1', '--json', 'number,body'])
    issue_number = None
    seen = set()
    body = ''
    if proc.returncode == 0:
        issues = json.loads(proc.stdout or '[]')
        if issues:
            issue_number = issues[0]['number']
            body = issues[0].get('body') or ''
            m = MARKER_RE.search(body)
            if m and m.group(1).strip():
                seen = set(m.group(1).split())

    unseen = [d for d in new if d['id'] not in seen]
    if not unseen:
        print('all discoveries already notified')
        return

    today = date.today().isoformat()
    lines = [f"- `{d['id']}`" + (f" (reported {d['reported_release']})" if d.get('reported_release') else '')
             for d in sorted(unseen, key=lambda d: d['id'])]
    addition = '\n'.join(lines)
    updated_seen = ' '.join(sorted(seen | {d['id'] for d in unseen}))
    new_marker = f'<!-- seen: {updated_seen} -->'

    if issue_number is None:
        body = (
            "New coding-model releases to review, surfaced from the catalog "
            "discovery workflow against `notification_watchlist`. This issue is "
            "also the seen-state: ids listed under the marker are not re-notified.\n\n"
            f"### {today}\n{addition}\n\n{new_marker}"
        )
        proc = gh(['issue', 'create', '--repo', args.repo, '--title', ISSUE_TITLE,
                   '--body', body])
        if proc.returncode != 0:
            print(f'failed to create issue: {proc.stderr.strip()}', file=sys.stderr)
            return
        print(f'created issue with {len(unseen)} new discovery(ies)')
        return

    updated_body = MARKER_RE.sub(new_marker, body) if MARKER_RE.search(body) else body + '\n' + new_marker
    updated_body += f"\n\n### {today}\n{addition}"
    proc = gh(['issue', 'edit', '--repo', args.repo, str(issue_number), '--body', updated_body])
    if proc.returncode != 0:
        print(f'failed to update issue #{issue_number}: {proc.stderr.strip()}', file=sys.stderr)
        return
    print(f'updated issue #{issue_number} with {len(unseen)} new discovery(ies)')


if __name__ == '__main__':
    main()
