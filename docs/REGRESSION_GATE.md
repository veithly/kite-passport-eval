# Regression gate

Proofroom 1.1 adds a **fail-closed report comparator** so a new model capture, runner change, or semantic-review pass can be checked against a known baseline before it is merged or published.

The command compares two complete Proofroom `report.json` files:

```bash
python -m kite_eval compare \
  --baseline evidence/recovered/report.json \
  --candidate runs/candidate/report.json \
  --out runs/regression-gate
```

The gate returns `0` when no case regresses, `1` when at least one case regresses, and `2` when the input is malformed or incomparable. The output directory contains an offline HTML ledger, JSON, Markdown, JUnit XML and SHA-256 checksums.

## What counts as a regression

A case is marked `regressed` when **any** of these happens:

- an exact assertion that passed in the baseline no longer passes;
- the literal case status gets worse (`pass` → `fail/error/missing`, `fail` → `error/missing`, or `error` → `missing`);
- the semantic-review state gets worse (`pass` → `pending/fail`, or `pending` → `fail`).

Gains never cancel a loss. If one assertion improves while another previously passing assertion disappears, the case still fails the gate. A changed response SHA-256 is recorded, but is not by itself a failure when all evidence stays at least as strong.

The comparator refuses to compare reports with different suite hashes, case IDs, assertion lists, malformed status/check combinations, duplicate IDs, duplicate literals, or invalid semantic-review states. It derives its own comparison summary instead of trusting the source report's summary counters.

## CI use

The repository's GitHub Actions workflow first replays the preserved 138-case capture, then runs the comparator against the frozen published baseline:

```bash
python -m kite_eval compare \
  --baseline evidence/recovered/report.json \
  --candidate runs/ci/live-replay/report.json \
  --out runs/ci/regression-gate
```

This does **not** call a model. It proves that a code change cannot silently turn previously observed evidence into a weaker result without making CI red. The existing 424 assertion-deletion mutants still test the literal grader itself; the regression gate tests report-to-report stability and review-state preservation.

## Security and provenance

Comparison inputs are treated as untrusted artifacts. JSON is decoded with the same duplicate-key and non-finite-value rejection used by the runner, file size is bounded, generated HTML escapes assertion text, JUnit strips invalid XML control characters, and output files are created without overwriting existing evidence.

The comparison JSON records both capture hashes when present. The CLI additionally records SHA-256 hashes of the complete baseline and candidate report files, while the output bundle has its own checksum manifest.
