# Reproducibility and adapter protocol

## Input and output boundaries

An adapter receives one UTF-8 JSON object with exactly `schema_version`, `id`, `prompt`, `skill`, `documents`, and `mode`. Each document contains a relative `path`, `sha256`, and `text`. The runner provides the selected official `SKILL.md`, that skill's Markdown references and `docs/reference.md`. It does not include `evals/`, expected answers or assertion strings. Context over 1 MiB is rejected rather than silently cut.

An adapter returns one JSON object: `{"response":"the complete text","metadata":{}}`. stdout and stderr share a configurable output limit (default 1 MiB). Deadline failures, nonzero exits, invalid JSON and malformed envelopes are error records, never partially scored successes. Only trusted local adapters should run; `shell=False` is not an operating-system sandbox.

The supplied Claude adapter uses the system prompt in its source, safe mode, empty tools, empty strict MCP configuration, no Chrome integration and no session persistence. It is one call per case, without automatic retries. The model can still emit strings resembling tool calls; they remain text.

## Recorded provenance

Each transcript records its prompt, request, response, adapter-config and document hashes; selected model/usage metadata; duration; exit status; and UTC capture time. `kind` distinguishes actual agent output from a fixture, but is a declared provenance label, not a cryptographic proof of model identity. A third party can inspect the adapter and repeat the call; no claim of trusted remote attestation is made.

The adapter used for the captured release is SHA-256 `89e4a186e15bfdb68123ad00b5523329d1276dad73a296efc33b9c68e3120416`. The CLI version observed on the capture host was 2.1.202. Claude's reported model identifier was `claude-haiku-4-5` in all 138 successful captures. Request hashes cover the request JSON, not executable source; the separately recorded adapter-source hash closes that documentation gap for this release.

The first-pass journal SHA-256 is `9c68df39da103b4bfa4968b2dc1f77433e9e9568e6478208441b67203af899e6`. The recovered journal SHA-256 is `fdb076c886d8f1025d48042016db0330dbd10822eceaa3d06a371ee314e06a13`. The recovery manifest binds the original and retry journals and names the replaced error ID. No scored response may be replaced by `scripts/recover.py`.

Exact replay produces identical per-assertion booleans, offsets and case statuses across the supported test matrix. Run timestamps and environment metadata may differ, so regenerated HTML/JSON file hashes need not be identical. Fresh cloud model calls are not deterministic, even when request hashes match.

## Reviews

```json
[
  {
    "id": 31,
    "response_sha256": "the actual response SHA-256",
    "verdict": "fail",
    "reviewer": "reviewer name and review method",
    "rationale": "Explain the violation of expected behavior.",
    "quote": "an exact nonempty substring of that response"
  }
]
```

Only `pass` or `fail` is accepted; unknown, duplicate, stale or unquoted reviews are rejected. A review does not alter a literal assertion. With `--require-review`, every case needs a review and pending review creates a nonzero process result and a failing JUnit testcase. The release live run has no such reviews; the known-failure fixture includes an explicitly labeled fixture review.

## Scope and extension

The live adapter is POSIX-only because it uses process groups and pipe selectors. Pure replay and reporting use portable Python, but this release's executed CI matrix is Linux/macOS, not a claim of Windows validation. Custom suites use the original four-field schema through `validate`/`replay`. Live skill-context mapping is explicit and pinned, so accepting a new official revision requires updating the commit, suite hash and group mapping together.

The runner verifies only tracked upstream changes and the pinned suite. Do not add untrusted extra reference files to the upstream checkout: context files can influence model output. Use a fresh pinned clone for published runs. Review any new adapter's network/filesystem behavior separately.
