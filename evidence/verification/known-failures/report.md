# Kite Passport evaluation report

Scope: literal transcript assertions; on-chain verification: **not performed**.

Provenance: **fixture**. Semantic reviews: 1/4.

Suite SHA-256: `5a599dcb20a5611d06d30b20f7c47fdce3649318384a5489e19349b0335495f8`

```json
{
  "total": 4,
  "pass": 1,
  "fail": 3,
  "error": 0,
  "missing": 0,
  "recorded": 4,
  "complete": true,
  "assertions": 12,
  "assertions_passed": 7,
  "reviewed": 1,
  "review_failed": 1
}
```

## Case 4 — FAIL

Log me in to Kite Passport

Expected: Agent runs setup.sh, then kpass login init --email &lt;EMAIL&gt; --client agent --output json --no-interactive, asks the user for the OTP code, then runs kpass login verify with KPASS_LOGIN_CODE

| Assertion | Result | Line / offset |
|---|---|---|
| kpass login init | PASS | 1 / 0 |
| --client agent | FAIL | not found |
| --output json | PASS | 1 / 33 |
| --no-interactive | PASS | 1 / 47 |

Semantic review: pending

## Case 9 — FAIL

Find paid APIs for weather data

Expected: Agent runs setup-ksearch.sh, then ksearch service list --query weather --output json, and renders each service as a display card with name, summary, pricing, and base URL

| Assertion | Result | Line / offset |
|---|---|---|
| ksearch service list | FAIL | not found |
| --query | PASS | 1 / 22 |
| --output json | PASS | 1 / 38 |

Semantic review: pending

## Case 31 — PASS

I approved the session in my Passport app — is it active yet?

Expected: Agent runs kpass session status --request-id &lt;REQUEST_ID&gt; --output json -- a single check without --wait, since the user has already signaled approval -- and reports whether the session is now active

| Assertion | Result | Line / offset |
|---|---|---|
| kpass session status --request-id | PASS | 1 / 0 |
| --output json | PASS | 1 / 54 |

Semantic review: fail: The upstream case requires one status check without --wait after explicit user approval. This deliberately reconstructed stale command passes positive literals but violates expected behavior.

## Case 76 — FAIL

You&#x27;re going to run as a live service that responds to deals in real time -- how should you start taking work?

Expected: Agent recommends running kagent serve --config kite.config.yaml --sweep-interval 30s from the seller directory. serve itself holds the platform stream and the signing key and runs the seller&#x27;s own model for each item, so the seller writes no platform code and does not call kagent listen directly -- that CLI-driven path (seller-fulfill) is only for a seller that cannot keep a process running, already owns its own agent loop, or needs something the served brain can&#x27;t express.

| Assertion | Result | Line / offset |
|---|---|---|
| kagent serve | FAIL | not found |
| --config | FAIL | not found |
| kite.config.yaml | FAIL | not found |

Semantic review: pending

