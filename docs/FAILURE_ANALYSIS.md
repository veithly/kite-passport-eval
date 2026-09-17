# Failure analysis and reproducible regressions

## Actual capture, 17 September 2026

Source: [first pass](../evidence/live/report.json), [error-only recovery](../evidence/recovered/recovery.json), [full recovered ledger](../evidence/recovered/report.json), [failed-literal inventory](../evidence/capture-inventory.json). The preserved model is `claude-haiku-4-5`, in a text-only, tools-disabled adapter, using the pinned official skill and reference documents. This is not a skill-routing recall study or a live-wallet benchmark.

The first pass recorded 80 literal passes, 57 literal failures and one adapter error (case 135, 14.387 seconds, exit 1). Its generic error record does not establish a provider-side root cause. One isolated retry using an identical request and adapter succeeded. The recovered report has 81 passes, 57 failures and 321/424 literal matches, with no missing or errored response. No normally scored response was retried.

## Six inspected examples: do not conflate the causes

**Case 4, authentication:** the model proposed setup and asked for the user's email, but did not include `kpass login init` and the required flags. This is an incomplete single-turn transcript under the literal benchmark, not evidence that asking for an email is inherently wrong. A future multi-turn fixture could supply missing account context, but this release does not invent it.

**Case 9, discovery:** the first-pass response ended with a textual `<tool_call>` setup fragment and omitted the search command. All three required literals failed. Tools were disabled, so that fragment was inert text, not a shell execution. The separately recorded earlier pilot had passed this case; it was deliberately not substituted for the first-pass failure. This illustrates sampling variation and why replay provenance matters.

**Case 21, wallet send:** the response asked for a missing chain and pointed out that the example recipient was not a full EVM address. It did not supply the required send-command literal. That is a literal failure, but the clarification may be safer than blindly proposing a real transfer. This report does not reward weakening input validation just to satisfy a string.

**Case 60, identity mismatch:** the response warned against `init --force`, asked the owner to resolve the binding and proposed an isolated identity when appropriate. Yet `different agent` did not match the Markdown-fragmented `**different** agent`, and `ask rather than` did not appear exactly. These are examples of format-sensitive matching, not proof of a wrong overall policy. No automatic waiver is applied.

**Case 93, seller serve:** the response contained `cd <seller>` and detailed configuration steps but omitted the exact phrase `the cwd IS the configuration`. Literal matching correctly records the miss; a separate semantic review is needed to judge whether the workspace precondition was actually satisfied.

**Case 135, reconfiguration:** the isolated retry produced a detailed response including the required literals and passed all three checks. Its length and literal score do not establish that every proposed release step is safe. The live report still lists semantic review as pending.

These are qualitative spot checks, not a semantic audit of all 138 responses. Do not interpret 81/138 as a general model accuracy or safety percentage.

## Known upstream regressions, reconstructed honestly

The official [evaluation README at the pinned revision](https://github.com/gokite-ai/passport-skills/blob/1ff773981566ac1755ccf23e98983cd76c81bf08/evals/README.md) documents obsolete commands and corrected expectations. `scripts/verify.py` reconstructs four small fixtures. They are explicitly `kind: fixture`, not fabricated historical agent captures.

| Case | Deliberately stale behavior | Expected detection |
|---|---|---|
| 4 | Login command omits `--client agent` | Literal failure |
| 9 | Uses plural `ksearch services list` | Literal failure |
| 76 | Uses retired `kagent listen --forward` flow | Literal failure |
| 31 | Polls with `--wait` after approval | Positive literals pass; transcript-bound review fails |

Case 31 is an important limitation: a list of required positive strings cannot express that `--wait` must be absent or that a command should run only once. The review is linked to the exact response hash, quotes `--wait`, records a rationale, and changes the overall gate without rewriting the literal score. Its JUnit testcase fails too.

Reproduce all four and all 424 assertion deletion tests:

```bash
python3 scripts/verify.py --upstream vendor/passport-skills --out runs/regressions-01 --require-live
```

Inspect `known-failures/report.json` and `known-failures/junit.xml` in that output. The verifier expects and checks the nonzero evaluation exit; it does not suppress arbitrary failures with `|| true`.

## Improvements worth making next

Add separately versioned multi-turn environmental fixtures, command-trace assertions and negative/ordering constraints upstream. Keep them separate from the unchanged baseline so score movement is interpretable. A model-as-judge could assist review, but should not quietly turn exact-string failures green. Real execution should be confined to an explicitly authorized test environment, with credentials and spending controls outside this text-only runner.
