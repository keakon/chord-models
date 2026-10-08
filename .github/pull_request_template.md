# Summary

<!-- What changed and why. -->

## Checklist

- [ ] `./scripts/validate.sh` passes locally (pass a Chord checkout for
      offline runs).
- [ ] Data or coverage changes bump the `catalog.yaml` version.
- [ ] Schema changes: the Chord consumer is implemented and tested first,
      `validator-revision` names that full commit SHA, and the commit is
      published before this change relies on it.
- [ ] State which smoke checks actually ran (see CONTRIBUTING.md); local
      validation is not a live provider check.
