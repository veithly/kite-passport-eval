# Browser and installation acceptance

Performed on 17 September 2026 using Ego Lite against the generated `evidence/recovered` report, served on a loopback-only HTTP server. These are observed results, not planned checks.

| Check | Observed result |
|---|---|
| Desktop viewport | 1460 × 826; document width 1445, no horizontal overflow |
| Mobile emulation | 390 × 844; document width 390, no horizontal overflow |
| Full case presence | 138 detail records and 138 matrix links |
| External JavaScript | 0 scripts with external `src`; no CDN dependency |
| Failed-case filter | 57 visible records |
| Passed-case filter | 81 visible records |
| Skill filter: activity | 3 visible records |
| No-match search | 0 visible records; empty-state message visible |
| Reset | All 138 records restored |
| Matrix navigation: case 9 | Correct case expanded |
| Visual inspection | Desktop and mobile screenshots inspected; headings, provenance, controls and evidence readable |
| Isolated package build | Wheel built and installed into project-local `.venv`; `kite-eval --version` returned `1.0.0` |
| Installed CLI | Pinned suite validated as 138 cases / 424 assertions and the recorded official SHA-256 |

Screenshots: [desktop](../evidence/ui/desktop.png) · [mobile](../evidence/ui/mobile.png).

Mobile emulation is not a claim of exhaustive physical-device testing. The report has no browser-backend submission flow. This browser QA says nothing about acceptance by the external bounty platform.

## Week 2 regression-gate QA

Performed on 27 September 2026 using Ego Lite against `evidence/week2/regression-gate`, again served only on `127.0.0.1`.

| Check | Observed result |
|---|---|
| Desktop viewport | 1920 CSS px; document width 1905, no horizontal overflow |
| Mobile emulation | 390 × 844; document width 390, no horizontal overflow |
| Comparison rows | 138 rows |
| Frozen-baseline result | 0 regressions, 0 lost assertions, all 138 cases unchanged |
| External JavaScript | 0 external scripts |
| Responsive table | Table remains inside an overflow container; document itself does not overflow at 390 px |
| Package install | Fresh isolated venv installed 1.1.0 successfully |
| Installed CLI | `kite-eval --version` returned `1.1.0`; pinned suite validated as 138 cases / 424 assertions |

Screenshots: [regression desktop](../evidence/week2/regression-desktop.png) · [regression mobile](../evidence/week2/regression-mobile.png).
