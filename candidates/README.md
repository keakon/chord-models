# Discovery candidates

Each YAML file records one observed wire model ID on a vendor/provider scope.
The filename is `<vendor>--<wire-model-id>.yaml`; `coverage.json` records its
release screening and missing checks. Candidates are delivered by catalog
refresh and can appear in suggestions when `chord config add` cannot match a
model. They are not selectable as verified models in the interactive guide
and never fill runtime defaults. Read their complete evidence in this directory
and [`coverage.json`](../coverage.json).

The initial broad discovery set came from a pinned models.dev commit. Context
values are secondary observations until official evidence confirms them.
A listed tool-capable text model is not automatically a frontier coding
recommendation. Notes identify missing coding, lifecycle, release, output or
serving evidence. Some entries already have official partial evidence.

Supported fields: `wire_model_id`, `scope`, optional existing `model_id`,
`context`, `input`, `output`, `input_modalities`, official `released`,
`coding_sources`, required `sources`, and `notes`. Omit unobserved fields;
never complete a candidate by guessing. Each source needs an HTTPS URL and
calendar `checked` date. See [CONTRIBUTING.md](../CONTRIBUTING.md).
