#!/usr/bin/env python3
"""Require a strictly newer identity for every catalog/coverage data change."""
import re
import subprocess
import sys

base = sys.argv[1]
paths = ['catalog.yaml', 'models.yaml', 'endpoints.yaml', 'bindings.yaml', ':(glob)candidates/*.yaml', 'coverage.json']
changed = subprocess.check_output(['git', 'diff', '--name-only', base, 'HEAD', '--', *paths], text=True).strip()
if changed:
    previous = subprocess.check_output(['git', 'show', base + ':catalog.yaml'], text=True)
    current = subprocess.check_output(['git', 'show', 'HEAD:catalog.yaml'], text=True)
    def identity(text):
        match = re.search(r'^version:\s*["\']?(\d{4}-\d{2}-\d{2})\.(\d+)', text, re.M)
        if not match:
            raise ValueError('invalid catalog identity')
        return match[1], int(match[2])
    if identity(current) <= identity(previous):
        sys.exit('Catalog data changed without a strictly newer version in catalog.yaml.')
