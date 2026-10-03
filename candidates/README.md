# Candidates

Community-submitted model entries that are discovered but not yet fully
verified. A candidate never becomes a runtime default: chord shows candidates
in its discovery lists with their scope and sources, and adopting one is
always an explicit user choice.

Move an entry up to the verified files at the repository root once its PR
carries the full evidence: official docs checked (with dates), a recorded
endpoint binding, and a request-behavior smoke run.

## File format

One YAML file per sighting under `candidates/` (any file name, `.yaml`
suffix). Unknown fields are rejected, and every fact must be something that
was actually observed — missing facts stay missing:

```yaml
# The wire model name exactly as the endpoint serves it. Must not contain '@'.
wire_model_id: gpt-6.1-sol-messages
# The provider side the name was observed on: a managed preset ID (openai,
# anthropic, gemini, codex) or a gateway identifier. chord uses it to prefer
# the sighting that matches the endpoint being configured; it never picks a
# scope silently.
scope: some-gateway
# Optional: the verified catalog model this sighting is known to resemble.
# Borrowing that model is the verified adoption path in `chord config add`.
model_id: openai/gpt-6.1-sol
# Optional observed facts. Zero/absent means "not observed", never a default.
context: 400000
input: 200000
output: 128000
input_modalities: [text, image]
# Required: at least one source with an https URL and a real calendar day.
sources:
  - url: https://example.invalid/docs/gpt-6.1-sol-messages
    checked: 2026-10-02
# Optional free text: what was checked, how, and what stayed unverified.
notes: |
  Context and modalities read off the gateway's model list; request behavior
  not yet exercised.
```

Rules:

- `wire_model_id`, `scope`, and at least one `sources` entry are required;
  a candidate without observed facts must reference a `model_id`.
- `model_id` must name a model in the verified catalog.
- `input_modalities` accepts `text`, `image`, `pdf`, `audio`, `video`.
- One wire name may appear several times with different scopes; chord shows
  the sightings side by side and never chooses between them.
