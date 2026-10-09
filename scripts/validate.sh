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
validation_failed() {
  {
    echo
    echo "Validator check failed (pin $pin)."
    echo "Unknown field? Fix the typo, or bump validator-revision to the published"
    echo "Chord commit that implements the new schema (see CONTRIBUTING.md)."
    echo "Could not resolve the pin? Check GOPROXY/GOSUMDB and that the commit is"
    echo "published, or pass a local checkout: ./scripts/validate.sh /path/to/chord"
  } >&2
  exit 1
}
chord="${1:-}"
if [[ -n "$chord" ]]; then
  # A local checkout deliberately uses that checkout's current code; the pin
  # still names the published validator identity for release purposes.
  chord="$(cd "$chord" && pwd)" || validation_failed
elif (cd "$tmp" && mkdir -p probe && cd probe && go mod init validator-probe >/dev/null 2>&1 && go mod download "github.com/keakon/chord@$pin" >/dev/null 2>&1); then
  # Prefer the module cache; resolving a raw SHA still requires a published
  # commit or a proxy that can resolve that SHA to its cached module version.
  :
else
  # Mirrors can lag on checksums for fresh pseudo-versions; a shallow fetch of
  # the same commit is content-addressed and needs no checksum service.
  echo "note: the pin did not resolve through the module proxy; using a shallow git fetch" >&2
  chord="$tmp/chord"
  if ! {
    git init -q "$chord" &&
      git -C "$chord" remote add origin https://github.com/keakon/chord.git &&
      git -C "$chord" fetch -q --depth 1 origin "$pin" &&
      git -C "$chord" checkout -q --detach FETCH_HEAD
  }; then
    validation_failed
  fi
fi
set -- -dir "$root" -out "$tmp/catalog.json"
if [[ -n "${CATALOG_REVISION:-}" ]]; then
  set -- "$@" -revision "$CATALOG_REVISION"
fi
generate() {
  if [[ -n "$chord" ]]; then
    (cd "$chord" && go run ./cmd/modelcatalog-gen "$@")
  else
    (cd "$tmp" && go run "github.com/keakon/chord/cmd/modelcatalog-gen@$pin" "$@")
  fi
}
if ! generate "$@"; then
  validation_failed
fi
python3 -m unittest discover -s "$root/scripts" -p 'test_*.py'
python3 "$root/scripts/catalog_coverage.py" --catalog "$tmp/catalog.json" --as-of "$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["as_of"])' "$root/coverage.json")"
if [[ -n "${CATALOG_REPORT_PATH:-}" ]]; then
  cp "$tmp/catalog.json" "$CATALOG_REPORT_PATH"
fi
