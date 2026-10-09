# chord-models

[中文](README_CN.md)

A model catalog for [Chord](https://github.com/keakon/chord): choose a coding
model and configure it without copying API URLs or token limits by hand.
The maintenance target is **all frontier models suitable for coding released
in the last six calendar months**, including official APIs, hosted open
weights, and self-hosted deployments.

## Use in Chord

```bash
chord config add
chord config add openai/gpt-6.1-sol
```

In an interactive terminal, run `chord config add` to browse managed providers
and their verified models, or pass an exact catalog ID to add a model directly.
Chord creates your first config if needed, fills the documented connection,
and tells you which API key variable to set. For example:

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
and adding are offline. Use `chord doctor config` to see the active catalog
version and source. See [`models.yaml`](models.yaml) for model facts, sources,
release dates and pricing scope, and [`coverage.json`](coverage.json) and
[`candidates/`](candidates/) for discoveries and remaining checks.
These commands require a Chord build supporting the schema pinned in
[`validator-revision`](validator-revision).
Input budgets reserve the requested output from the total context window unless
the provider documents a separate input cap. Compaction thresholds instead use
a fixed baseline: a documented input cap if present, otherwise
`context - output`, otherwise the whole window. They do not move with a
request's planned output. Prices include scope notes; for example, long-context
requests can cost more than the listed base rate.
Qwen3.8-Max documents 991,808 input tokens in ordinary mode and 983,616 in
thinking mode. Its catalog entry uses the smaller cap across modes.

For guided gateway setup, run:

```bash
chord config add mygw/gpt-6-sol
```

In an interactive terminal, press a number to select a suggested verified model without Enter (`m` enters a full catalog ID), fill any missing provider URL and API-key environment variable, choose an existing pool or create one, and optionally configure the reasoning variant and request compression. Review and confirm before saving. Existing providers reuse their URL and credentials. Numbered menus and `y/n` respond immediately; text input still needs Enter. Press Esc, `q` or `0` in menus, enter `q` in text prompts, or decline saving to cancel without changing configuration or credential files. YAML anchors and `<<` merges are supported; editing shared settings leaves other references unchanged.

For scripts, pass `--no-interactive` with explicit arguments. Redirecting stdin or stdout also disables prompts; an unmatched model shows suggestions and returns an error without adopting one automatically.

Custom endpoints selected with `--catalog` inherit model behavior and compat
when they expose the same protocol as the official connection. Limits,
modalities and context compaction hints also transfer across protocols.
Request-body compression is disabled by default. After confirming endpoint support, choose `gzip` or `zstd` in the guide, pass `--compress gzip` / `--compress zstd`, or set provider `compress: gzip` / `compress: zstd` manually. Adding models preserves compression settings unless you explicitly change them.

The Opus 5.5 profile starts at its documented default effort, `medium`.
Compaction thresholds are adjustable Chord starting recommendations; tune them
for task quality, latency and cache reuse. Documented reasoning capabilities
can be broader than the variants verified on a particular managed endpoint.

## Coverage and evidence

The 2026-10-08 review contains **32 model fact records** and **99 discovery
candidates**, with a release inventory across **33 vendors**. This is a
starting coverage audit, **not a claim that every eligible model is already
verified**. [`coverage.json`](coverage.json) records each model, candidate,
exclusion, reported release date, and remaining checks. Official release
proof is still missing for many entries; registry dates are discovery hints.
The 2026-10-09 update rechecks selected configuration profiles, input limits
and pricing scopes; it does not repeat the full vendor inventory review.

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
# Local Chord checkout; offline with cached Go dependencies. Does not alter embedded data.
./scripts/validate.sh ../chord
```

Without a checkout argument the script resolves the fixed Chord validator
commit through the Go module proxy. CI runs the same schema/candidate checks, verifies version bumps on
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
| `validator-revision` | Full Chord commit SHA used by validation (resolved via the Go module proxy) |
