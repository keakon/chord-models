# chord-models

Upstream source of [Chord](https://github.com/keakon/chord)'s built-in model
catalog: verified endpoint contracts, model facts, and endpoint bindings.
This repository exists so catalog data can move faster than chord releases —
a new model lands here by PR, and users pick it up through `chord
config add` and catalog refresh instead of waiting for a binary update.

## Layout

| File            | Contents                                                                 |
| --------------- | ------------------------------------------------------------------------ |
| `catalog.yaml`  | Catalog identity: the version, bumped on every data change                |
| `endpoints.yaml`| Verified endpoint contracts: protocol, request URL, auth method, credential env var, sources |
| `models.yaml`   | Verified model facts: context/input/output budgets, modalities, reasoning options, pricing, sources |
| `bindings.yaml` | Verified endpoint bindings: wire model IDs, reasoning variants, Responses field send defaults |
| `candidates/`   | Community-submitted discovery entries (inert: never become defaults until verified and moved up) |

Entries live in one of two states:

- **verified** — official docs checked, binding recorded, request behavior
  validated. Verified entries ship in chord's embedded snapshot and provide
  runtime defaults.
- **candidate** — discovered and proposed, facts not yet fully verified.
  Candidates are displayed with their sources but never fill defaults
  automatically; adopting one is always an explicit user choice.

## Tags

Every merged data change bumps `version` in `catalog.yaml`; a maintainer
ships the new state as a tag named `v<version>` (for example
`v2026-10-01.1`). Tags are the only thing chord's catalog refresh pulls —
it never follows a branch head.

## Contributing

1. Fork, edit the YAML files, bump `version` in `catalog.yaml`.
2. Every fact carries its evidence: `sources` entries with an https URL and a
   real calendar-day `checked` date. Missing facts stay missing — never encode
   a guess as zero or as a copied neighbor value.
3. `verified` additions additionally need a recorded request-behavior check
   against the endpoint (a smoke run through `chord doctor models` on the
   preset, noted in the PR).
4. Open a PR. CI validates the schema and references; a maintainer reviews the
   evidence, merges, and tags `v<version>`.

## How chord consumes this repository

- **Release snapshot**: each chord release embeds a snapshot of a pinned tag
  as its built-in catalog (generated, byte-stable, guarded by a golden test in
  the chord repository). Chord records the pinned tag in its
  `internal/modelcatalog/data/snapshot.yaml`, and
  `scripts/sync_model_catalog.sh <tag>` performs the pin → copy → regenerate
  → verify round trip.
- **Catalog refresh**: `chord config refresh-catalog` (or
  `chord config add --refresh-catalog`) pulls the newest `v<version>` tag
  into a local cache. Refreshed verified data supersedes the embedded
  snapshot as a whole by catalog version — never merged entry by entry — and
  any failure (network, corrupt snapshot, incompatible schema) falls back to
  the embedded snapshot. Refreshed candidates join chord's discovery lists
  with their scope and sources; they never fill defaults.
- chord owns the schema and the presentation; this repository owns the data.

## Validating locally

From a chord checkout, run the catalog generator against this directory:

```bash
go run ./cmd/modelcatalog-gen -dir /path/to/chord-models
```

It fails on unknown fields, duplicate identities, dangling bindings,
non-https sources, non-calendar check dates, and zero-priced entries, and it
validates every entry under `candidates/` the same way.
