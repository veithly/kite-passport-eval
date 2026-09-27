# Week 2 acceptance evidence

Target contribution: **Passport Skills Eval Runner** from the [Kite Bounty contribution directions](https://kiteai-bounty-dashboard.vercel.app/directions).

The dashboard currently defines **Week 1 as 14–20 September 2026** and **Week 2 as 21–27 September 2026** (Beijing time). The original 1.0 runner was committed on 17 September and now belongs to Week 1. The **Week 2 original contribution** is the 1.1 regression-gate extension created on 27 September: fail-closed report comparison, new export formats, CI enforcement, validation and tests.

| Requirement | Implementation and evidence |
|---|---|
| Execute all existing cases | [138 real captures](../evidence/recovered/transcripts.jsonl); [full report](../evidence/recovered/report.json); [first pass retained](../evidence/live/report.json) |
| Per-assertion outcomes | All 424 checks include exact literal, boolean outcome, character offset and line; [report generator](../kite_eval/report.py) and [grader](../kite_eval/core.py) |
| Reproduce known failures | [Four unchanged-format cases](../evidence/verification/known-failures-suite.json), [reconstructed fixtures](../evidence/verification/known-failures.jsonl), [failure report](../evidence/verification/known-failures/report.json), [analysis](FAILURE_ANALYSIS.md) |
| GitHub Actions integration | [Pinned workflow](../.github/workflows/ci.yml); Linux/macOS matrix now includes a frozen-baseline regression gate; [workflow runs](https://github.com/veithly/kite-passport-eval/actions/workflows/ci.yml) |
| Preserve existing format | Official suite hash checked, no upstream file modifications; strict four-field loader and 138-case compatibility tests |
| Week 2 regression safety | [Comparator implementation](../kite_eval/compare.py) rejects suite/case/assertion drift, fails on lost literals/status/review downgrades, and writes HTML/JSON/Markdown/JUnit/checksums; [138-case zero-regression evidence](../evidence/week2/regression-gate/comparison.json); [design](REGRESSION_GATE.md) |
| Usable deliverable | Offline responsive evaluation report plus offline regression ledger, CLI, JSON/JUnit/Markdown, installation metadata and English/Chinese instructions |
| Test quality | [Week 2 verification](../evidence/week2/verification.json): 41 unit tests, 424 assertion-deletion mutants, malicious comparison HTML escaping, malformed/incomparable report rejection, and CLI exit-code tests |
| Provenance | [Recovery manifest](../evidence/recovered/recovery.json), [artifact checksums](../evidence/recovered/checksums.json), [capture inventory](../evidence/capture-inventory.json) |

The original corpus remains pinned to `1ff773981566ac1755ccf23e98983cd76c81bf08`, SHA-256 `ba8af9651ab014242790b39491dcf9137d6d3323cc8c0f94698099c7535b2f5b`.

## Claims intentionally not made

This is not an all-green model benchmark, on-chain execution proof, automatic skill-routing evaluation, exhaustive semantic review, upstream-merged PR, Electric Capital registration approval or a guaranteed bounty award. All recorded model failures remain visible. Any required external review or repository registration is still the responsibility of the corresponding reviewing organization.
