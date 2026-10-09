# Offline evidence audit / v1.2

**Week 4 (5–11 October 2026, Beijing time)** introduces an independent, zero-third-party-dependency provenance auditor for the official Kite Passport Skills suite. The audit never invokes a model, blockchain, wallet, extension, or production credential. It independently reconstructs all captured adapter requests and the recorded scoring decisions.

## Run against the original release

Use the frozen official Passport Skills checkout at commit `1ff773981566ac1755ccf23e98983cd76c81bf08`, Python 3.9+, and an entirely new output directory:

```bash
python3 -m kite_eval audit \
  --upstream ../upstream/passport-skills \
  --adapter adapters/claude-safe.json \
  --original evidence/live \
  --retry evidence/retry-135 \
  --recovered evidence/recovered \
  --release-pins \
  --out runs/audit-01
```

Exit status is `0` when every invariant holds, `1` for invalid or manipulated evidence (an audit ledger is still written), and `2` for malformed essential inputs or filesystem/infrastructure errors. Output: `audit.json`, `audit.md`, `junit.xml`, `index.html` and `checksums.json`. Files are exclusive-created and never overwrite evidence. The rendered report is entirely offline; its only styling is inline CSS, and all evidence is HTML-escaped.

## What the auditor proves

The complete captured release currently passes **644 / 644** deterministic checks:

| Layer | Checks | Procedure |
|---|---:|---|
| Inputs | 23 | Official upstream commit, pinned suite digest, 138 cases / 424 assertions, trusted adapter schema, 19 complete skill contexts |
| Files | 32 | Strict UTF-8 JSON, bounded regular files, symlink refusal, expected file layout |
| Artifact checksums | 16 | SHA-256 for every report and transcript in original, retry and recovered bundles |
| Release trust anchors | 4 | Original/retry/recovered transcript SHA-256 and original release report SHA-256 against code-reviewed constants |
| Transcripts | 4 | Independent schema/prompt/response hash validation for each transcript set; full release coverage |
| Per-case reconstruction | 552 | For each of 138 cases: hash the prompt+official skill document request, verify document list/hashes, adapter configuration and real-agent text-only provenance fields |
| Reconstructed report | 6 | Recompute all literal statuses, every match's position and line, all 424 assertions, semantic-review bindings, capture digest and no-on-chain claim |
| Recovery lineage | 7 | Verify first pass, single error-only retry, original summary, matching request+adapter hashes, exact restored 138 records and canonical journal |

Unlike a replay which grades whatever is in a transcript, this independently verifies that the request hash really matches the correct source skill documents for that exact prompt. It also verifies that the published recovered report is a deterministic consequence of the original journal plus its **single legitimate infrastructure retry**, not a cherry-picked higher-scoring answer.

## Mutation and tampering tests

The auditor has tests which deliberately alter **only private temporary copies**, not the public historical captures. They cover:

- Forged request SHA-256 and official document digest mismatch;
- Changed response while recomputing the local checksum manifest;
- Falsified report totals, with rewritten artifact hashes;
- A retry that attempts to replace an already-scored successful response;
- Changed tools-disabled metadata;
- Symlink substitution, missing artifacts, duplicate JSON keys, and path-traversal checksum entries;
- Tampered untrusted text in HTML/JUnit, no overwriting, deterministic independent outputs and CLI exit codes.

These are explicitly negative **harness tests**, not new model invocations or claims that an attacker altered the actual Kite infrastructure. The original **81 literal passes / 57 literal fails** remain unchanged. The live semantic audit remains pending.

## What it does NOT prove

**Hash consistency is not cryptographic provenance.** A coordinated attacker able to change the code-reviewed release-pin constants, published content, and Git history can make arbitrary fake data self-consistent. The release pins provide a separate anchor within reviewed source control; they are not digital signatures, hardware attestation, independent provider invoices or signed statements from Kite.

The recorded metadata stating “tools disabled” is a claim present in the stored adapter output; the auditor verifies that claim has not changed, but cannot independently confirm the model provider's internal behavior. Text-only literal tests cannot establish correct tool routing, semantic safety, wallet consent, actual x402 settlement, on-chain events, or an activity reward. No wallet transaction or model call occurs during the audit.

For real security review, retain a trusted source checkout, review commits and CI runs, verify the releases from separate hosts, and use independent provider/on-chain evidence for external claims. Never run untrusted adapters with a production wallet.

## CI and public evidence

The three-job GitHub Actions OS/Python matrix now runs the **offline evidence audit as a hard gate**, after the existing scorer tests and baseline regression gate. Failure stops publication. The main-branch Pages workflow publishes the static audit to [Evidence Audit](https://veithly.github.io/kite-passport-eval/evidence-audit/), alongside the original model report and Week 2 regression gate.

The committed audit report and its manifest are in [`evidence/week4/audit/`](../evidence/week4/audit/). Its results, CI logs and release SHA pin checks remain independently inspectable without the author's browser or credentials.
