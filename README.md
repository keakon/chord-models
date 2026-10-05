# chord-models

[中文](README_CN.md)

A model catalog for [Chord](https://github.com/keakon/chord): choose a coding
model and configure it without copying API URLs or token limits by hand.
The maintenance target is **all frontier models suitable for coding released
in the last six calendar months**, including official APIs, hosted open
weights, and self-hosted deployments.

## Use in Chord

```bash
chord config show --catalog
chord config add openai/gpt-6.1-sol
```

Copy an add command from the catalog. Chord creates your first config if
needed, fills the documented connection, and tells you which API key variable
to set. For example:

```bash
export OPENAI_API_KEY="your-api-key"
chord config add openai/gpt-6.1-sol
chord
```

Existing providers keep their URL and credentials. OAuth models also print
the login command. A workspace-specific or self-hosted connection needs your
own `--url`; a custom wire model name can borrow facts explicitly:

```bash
chord config add local/my-model \
  --url https://your-server.example/v1/chat/completions \
  --catalog cohere/north-mini-code-1-0 --api-key-env LOCAL_API_KEY
```

Fetch a published update with `chord config refresh-catalog`. Ordinary viewing
and adding are offline. Use `chord config show --catalog --json` for full
sources, release dates, pricing scope, and candidates delivered by refresh.
These commands require a Chord build supporting the schema pinned in
[`validator-revision`](validator-revision).

Custom endpoints selected with `--catalog` inherit model behavior and compat
when they expose the same protocol as the official connection. Limits,
modalities and context compaction hints also transfer across protocols.
Request-body compression is disabled by default; users can set provider
`compress: gzip` or `compress: zstd` after confirming support. Adding a model
preserves explicit compression settings.

## Coverage and evidence

The 2026-10-05 review contains **31 model fact records** and **98 discovery
candidates**, with a release inventory across **33 vendors**. This is a
starting coverage audit, **not a claim that every eligible model is already
verified**. [`coverage.json`](coverage.json) records each model, candidate,
exclusion, reported release date, and remaining checks. Official release
proof is still missing for many entries; registry dates are discovery hints.

- Model facts are checked against cited documentation and may exist without
  a managed binding. Unknown facts stay absent.
- A documented `connection` supplies an API URL, wire ID and credential
  variable after the user selects an exact catalog model. It is a setup
  recipe, not a live request test or a source of route send defaults.
- Managed endpoint bindings carry route-specific behavior. Changes require
  endpoint evidence and a recorded smoke test in the contribution.
- Candidates are unverified observations. They never become runtime defaults.
  Partial official evidence can be retained here while a hard output limit,
  access restriction, release date, or coding suitability remains unresolved.

Six months means calendar months, not 180 days. Older facts remain available
for existing configurations. Retired routes, duplicates, and unsuitable models
receive an explicit inventory decision rather than silently disappearing.

## Maintain the catalog

```bash
# Offline, using your local Chord checkout; does not alter its embedded data.
./scripts/validate.sh ../chord
```

Without a checkout argument the script fetches the fixed Chord validator
commit. CI runs the same schema/candidate checks, verifies version bumps on
PRs and tag/version identity on releases. Weekly discovery produces an
artifact listing possible omissions from models.dev and missing official
release evidence; it never silently promotes registry data. An inventory
review older than seven days fails the weekly check.

See [CONTRIBUTING.md](CONTRIBUTING.md) for scope, evidence, discovery review,
pricing and release instructions. Chord owns the schema; this repository owns
the data. Local validation does not establish that GitHub CI, published tags,
or live provider requests have succeeded.

| File | Purpose |
| --- | --- |
| `catalog.yaml` | Immutable release identity (`YYYY-MM-DD.N`) |
| `models.yaml` | Model facts, coding/release evidence, documented connections, pricing scope |
| `endpoints.yaml` | Managed API protocol, URL and authentication contracts |
| `bindings.yaml` | Exact wire IDs, route limits/modalities, variants and send rules |
| `candidates/` | Partial discoveries, never used as defaults |
| `coverage.json` | Rolling inventory, exclusions, unresolved evidence and vendor watch list |
| `validator-revision` | Full Chord commit SHA used by validation |
