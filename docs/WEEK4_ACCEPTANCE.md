# Week 4 Kite Open Source Bounty — acceptance evidence

**Period:** 2026-10-05 through 2026-10-11 (Beijing time).
**Direction:** Passport Skills Eval Runner (official [direction 04](https://kiteai-bounty-dashboard.vercel.app/directions)).
**Author and public repository:** Rick / GitHub [@veithly](https://github.com/veithly) · [kite-passport-eval](https://github.com/veithly/kite-passport-eval).

Version 1.2 is a **new, original Week 4 code contribution**, built on the already-reviewed Week 1 runner and Week 2 comparator. Week 3 is not represented as a completed contribution; no late submission is invented.

| Acceptance requirement | Verifiable evidence |
|---|---|
| Execute the entire unchanged official suite | Retained [138 real agent captures](../evidence/recovered/transcripts.jsonl), source-pinned at `1ff7739...`, scored with 424 literal assertions |
| Return case- and assertion-level evidence | Existing [evaluation report](../evidence/recovered/report.json); new [auditor](../kite_eval/audit.py) independently checks every case request hash, skill document hash, response and score |
| Reproduce known failures, do not hide model failures | Existing deterministic fixture tests of cases 4/9/76 and case 31 semantic blind spot; unchanged real 81 pass / 57 fail; [verification](../evidence/week4/verification.json) |
| CI execution and reproducibility | [GitHub Actions workflow](../.github/workflows/ci.yml) now has a mandatory offline evidence-audit step for Ubuntu Python 3.9/3.13 and macOS Python 3.13 |
| Week 4 original features | [New `kite-eval audit` CLI](../kite_eval/__main__.py), [release pins and provenance checker](../kite_eval/audit.py), [negative security tests](../tests/test_audit.py), [complete audit specification](EVIDENCE_AUDIT.md) |
| Evidence of release integrity | [644-pass audit report](../evidence/week4/audit/audit.json), [checksums](../evidence/week4/audit/checksums.json), static HTML, Markdown, and JUnit XML |
| Local acceptance | **54 passing tests, 0 errors/skips; 424/424 mutation cases detected; 138 preserved model responses; 0 score regressions; 644/644 audit invariants passed** |

The tests deliberately change copies of evidence to prove that altered hashes, forged requests, bogus success cases, duplicate JSON entries, invalid recovery merges and hostile report text are detected. **No paid model was called and no wallet/chain action was performed this week** to manufacture new success figures.

Claims not made: semantic certification, signed provider attestation, independent on-chain verification, an upstream-merged PR, Electric Capital approval, platform administrator acceptance, or a guaranteed USDC reward. Platform submission records are kept locally in the separate `submission/` directory outside this public repository.
