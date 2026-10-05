#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ ! -f "$root/coverage.json" ]]; then
  echo 'missing required source inventory: coverage.json' >&2
  exit 1
fi
pin="$(cat "$root/validator-revision")"
if [[ ! "$pin" =~ ^[0-9a-f]{40}$ ]]; then
  echo 'validator-revision must contain one full Chord commit SHA' >&2
  exit 1
fi
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
chord="${1:-}"
if [[ -z "$chord" ]]; then
  chord="$tmp/chord"
  git init -q "$chord"
  git -C "$chord" remote add origin https://github.com/keakon/chord.git
  git -C "$chord" fetch -q --depth 1 origin "$pin"
  git -C "$chord" checkout -q --detach FETCH_HEAD
else
  chord="$(cd "$chord" && pwd)"
fi
set -- -dir "$root" -out "$tmp/catalog.json"
if [[ -n "${CATALOG_REVISION:-}" ]]; then
  set -- "$@" -revision "$CATALOG_REVISION"
fi
(
  cd "$chord"
  go run ./cmd/modelcatalog-gen "$@"
)
python3 -m unittest discover -s "$root/scripts" -p 'test_*.py'
python3 "$root/scripts/catalog_coverage.py" --catalog "$tmp/catalog.json" --as-of "$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["as_of"])' "$root/coverage.json")"
if [[ -n "${CATALOG_REPORT_PATH:-}" ]]; then
  cp "$tmp/catalog.json" "$CATALOG_REPORT_PATH"
fi
