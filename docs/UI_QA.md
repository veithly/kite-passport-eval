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

## Week 4: integrity ledger browser acceptance

Performed on 9 October 2026 with Ego Lite against the new release's offline audit HTML, served on loopback at `http://127.0.0.1:8767/`. Results are direct DOM observations, not hypothetical checks.

| Check | Observed outcome |
|---|---|
| Desktop | 1920 CSS px, document width 1920 (no horizontal overflow) |
| Mobile emulation | 390 × 844 CSS px, document width 390 (no horizontal overflow) |
| Evidence groups | 8 collapsible details groups |
| Audited invariants | 644 complete evidence rows |
| Release integrity | 644 passed / 0 failed, release SHA pins enforced |
| Safety | 0 external script tags; page CSP disallows script execution and network resources |
| Narrow-screen table | Table width 680px, inner scroll region width 358px; scrolling is contained inside the table |
| Offline usability | Static HTML, no JavaScript or CDN required |

**Visual screenshot caveat:** Ego Lite returned a `Page.captureScreenshot` timeout on this browser session. DOM and responsive layout checks passed, but this run does **not** claim a completed manual screenshot inspection. The HTML ledger remains publicly viewable and can be inspected in any modern browser.
