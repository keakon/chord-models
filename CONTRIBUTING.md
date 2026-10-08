# Maintaining a six-month coding catalog

## Scope and inclusion

Review every newly released flagship/general frontier model, coding specialist,
and competitive efficient variant during the last six calendar months.
Include previews with explicit availability restrictions, official APIs,
third-party hosted weights and self-hosted weights. Do not equate tool calling
with coding quality: require official software-engineering capabilities or
model-specific coding evaluations before treating a discovery as suitable.
Exclude embeddings, rerankers, image/audio generators, research-agent wrappers,
roleplay-only models and retired routes. Keep an exclusion reason and evidence.
Do not multiply one underlying model into records for every quantization or
alias; route limits and costs belong to the actual serving scope.

`coverage.json` is the review inventory, not another runtime catalog. Use
`released` only for a cited official calendar date. `reported_release` is a
secondary discovery hint and is never copied into model defaults. Vendor
reviews remain `partial` or `pending` until their official release inventory
has actually been audited. A report must say `complete: false` while unknown
dates or coverage gaps remain. Retain older facts needed by existing users;
do not remove a model solely because the window advanced.
Every model in `models.yaml` must have an inventory decision of `model`;
`candidate` and `excluded` decisions cannot also appear as runtime model facts.
The inventory is a required, committed source file, not a generated coverage
report. The repository's ignore exception keeps global `coverage.*` rules
from hiding it.

## Review discoveries weekly

1. Inspect the scheduled `catalog-discovery` artifact: it records the exact
   models.dev commit used and all new tool-capable text models in the window,
   including records whose release date is unknown. This is a broad screening
   list, not a recommendation. Also read official release/model/deprecation
   pages: an external registry cannot guarantee exhaustive coverage.
2. For each item, record a decision in `coverage.json`: `model`, `candidate`,
   or `excluded`. Candidates use `<vendor>--<wire-id>.yaml` filenames.
3. Verify release date, coding evidence, context versus independent input
   limits, **hard** output maximum, modalities, lifecycle, account/region
   restrictions and current standard pricing. Defaults and benchmark
   `max_tokens` settings do not prove a hard model maximum. Never copy a
   neighboring model's limits. Unknown pricing is absent, not zero/free.
4. Add complete model facts to `models.yaml`; partial observations stay in
   `candidates/`. Add `coding_sources`, and `released` when supported by a
   cited official release. `sources` need HTTPS URLs and real `checked` dates.
   Record all new evidence dates and update the inventory review date.
5. If the official API uses a supported protocol and a general URL, add a
   `connection` with the full request URL, exact `wire_model_id`, `env_var`,
   and `sources`. Do not insert a guessed region, workspace or entitlement.
   A connection is not a managed preset or smoke-tested binding.
6. Bump `catalog.yaml`, validate, and submit the evidence for review.

You can generate the same report locally, without API keys:

```bash
CATALOG_REPORT_PATH=/tmp/chord-catalog.json ./scripts/validate.sh ../chord
python3 scripts/catalog_coverage.py --catalog /tmp/chord-catalog.json \
  --models-dev /path/to/models.dev > /tmp/chord-coverage-report.json
```

The script is read-only and needs Python 3.11+. It subtracts six calendar
months with end-of-month clamping. `--as-of YYYY-MM-DD` makes historical
reports reproducible. `--max-review-age 7` enables the freshness gate.

## Route behavior and pricing

A managed endpoint change needs protocol/auth documentation and a recorded
`chord doctor models` run in the PR (date, endpoint/preset, wire ID, variants
checked, outcome; redact secrets). Bindings support `limit` overrides and
`input_modalities`: they must describe this route, not the model family in
isolation. `limit.input: 0` explicitly clears an inherited separate input cap.
Ordinary explicit config always wins over catalog defaults.
Model `reasoning_options` lists documented capabilities; binding `variants`
lists the subset verified on that route. Do not copy public API capabilities
into Codex OAuth bindings without route evidence and the required smoke check.

Use `cost.notes` for uncached/peak standard rates, region, long-context tiers,
promotions or account restrictions. Never present a promotional rate as an
unqualified permanent price. Store only the supported base price plus scope;
do not pretend this schema models every billing tier. Record subscription or
self-hosting restrictions in candidate notes/coverage reasons and cited docs.

Model output capacity can equal the total window. Chord reserves the effective
requested output budget when deriving input from a total window; an explicit
independent input limit still wins. Preserve real model capabilities instead
of lowering them to work around a budgeting bug.
In particular, do not store `context - output` as an independent `input` cap.
Omit `input` when no separate provider limit is documented.
Compaction thresholds use a fixed baseline instead of a request's output
budget: a documented independent `input` cap when present, otherwise
`context - output` while output is smaller than the window, otherwise the
whole window. Changing recorded `input`/`output` limits therefore moves every
compaction trigger for that model; re-check the `config_profile.compaction`
hints when you change them.

Configuration profiles are Chord starting recommendations, not additional
provider limits or proven performance optima. Prefer documented provider
defaults for effort; record a reason and workload evidence for deviations.
Compaction thresholds trade retained context against request cost, cache reuse
and latency. Tune them with representative tasks rather than treating a fixed
percentage as optimal for every endpoint.

## Validation and immutable releases

```bash
./scripts/validate.sh ../chord             # local checkout; uses that checkout's current code
./scripts/validate.sh                     # resolve the pinned commit via the Go module proxy
# On a checked-out release tag, verify tag/version identity as well:
catalog_tag="$(git describe --tags --exact-match)" && \
  CATALOG_REVISION="$catalog_tag" ./scripts/validate.sh ../chord
```

The generator validates all candidates as well as the four runtime sources.
It rejects unknown fields, missing references, malformed versions/dates,
invalid connection recipes, invalid route overrides and invented zero prices.
The inventory checker catches missing models/candidate files and inconsistent decisions.
Validation writes only a temporary artifact, never Chord's embedded snapshot.
The validator pin must be a full 40-character SHA even with a local checkout;
the local checkout argument deliberately uses that checkout's current code.
Without a checkout argument, validation resolves `github.com/keakon/chord` at
the pin through the Go module proxy, so the resolved module version is
immutable and proxy-cached even if Chord's history is rewritten. In a
restricted network, configure `GOPROXY`/`GOSUMDB` or pass a local checkout.

Every data or coverage change must increase `YYYY-MM-DD.N` in `catalog.yaml`.
A release tag is exactly `v<version>` and must point at that data version.
Never move/delete a published tag or reuse a version. Protect tags on the
hosting service. Fix bad data by releasing a **higher** version (revert the
facts in that new release); version-based refresh cannot roll back to an
older tag. Failed refresh leaves the last valid catalog in use.

When adding schema fields, implement and test the Chord consumer first; pin
its full commit SHA in `validator-revision`. **Publish that Chord commit before
publishing the upstream data/tag**, so remote CI can fetch the validator.
Then publish the reviewed catalog tag and sync Chord's embedded snapshot with
`scripts/sync_model_catalog.sh <tag> /path/to/chord-models`. Older Chord builds
reject unknown fields and retain their supported embedded catalog.
If validation fails with an unknown field, either fix the typo or bump the pin
to the published Chord commit that implements the field; never relax
validation to accept data the pinned consumer cannot read.
Release order: publish the Chord commit first, then push `main` and the tag
here, then run Chord's `Model catalog integration` workflow to compare the
published tag against Chord's embedded snapshot.

Schema and source evidence checks are not live provider checks. Contributions
must state which smoke checks actually ran; do not imply a published tag or
GitHub workflow succeeded merely because local validation passed.
