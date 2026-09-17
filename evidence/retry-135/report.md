# Kite Passport evaluation report

Scope: literal transcript assertions; on-chain verification: **not performed**.

Provenance: **agent**. Semantic reviews: 0/138.

Suite SHA-256: `ba8af9651ab014242790b39491dcf9137d6d3323cc8c0f94698099c7535b2f5b`

```json
{
  "total": 138,
  "pass": 1,
  "fail": 0,
  "error": 0,
  "missing": 137,
  "recorded": 1,
  "complete": false,
  "assertions": 424,
  "assertions_passed": 3,
  "reviewed": 0,
  "review_failed": 0
}
```

## Case 1 — MISSING

Show me my recent activity

Expected: Agent runs kpass activity --output json and renders each event as a display card with kind, status, timestamp, and relevant details

| Assertion | Result | Line / offset |
|---|---|---|
| kpass activity | FAIL | not found |
| --output json | FAIL | not found |
| ━━━ | FAIL | not found |

Semantic review: pending

## Case 2 — MISSING

Show me only my wallet transfers

Expected: Agent runs kpass activity --kind wallet_transfer --output json and renders wallet transfer events as display cards with amount, asset, and tx hash

| Assertion | Result | Line / offset |
|---|---|---|
| kpass activity | FAIL | not found |
| --kind wallet_transfer | FAIL | not found |
| --output json | FAIL | not found |

Semantic review: pending

## Case 3 — MISSING

I can see 10 events on the first page of my activity — show me the next page of older activity

Expected: Agent runs kpass activity --limit N --offset N --output json to paginate results beyond the first page, using an offset equal to the number of events already shown

| Assertion | Result | Line / offset |
|---|---|---|
| kpass activity | FAIL | not found |
| --limit | FAIL | not found |
| --offset | FAIL | not found |
| --output json | FAIL | not found |

Semantic review: pending

## Case 4 — MISSING

Log me in to Kite Passport

Expected: Agent runs setup.sh, then kpass login init --email &lt;EMAIL&gt; --client agent --output json --no-interactive, asks the user for the OTP code, then runs kpass login verify with KPASS_LOGIN_CODE

| Assertion | Result | Line / offset |
|---|---|---|
| kpass login init | FAIL | not found |
| --client agent | FAIL | not found |
| --output json | FAIL | not found |
| --no-interactive | FAIL | not found |

Semantic review: pending

## Case 5 — MISSING

I need to create a Kite Passport account

Expected: Agent runs setup.sh, then kpass signup init --email &lt;EMAIL&gt; --client agent --output json --no-interactive, asks the user for the 8-character sign-up code from their email, then runs signup exchange with KPASS_SIGNUP_CODE (signup poll is optional and not part of the primary flow)

| Assertion | Result | Line / offset |
|---|---|---|
| kpass signup init | FAIL | not found |
| --client agent | FAIL | not found |
| --output json | FAIL | not found |
| --no-interactive | FAIL | not found |

Semantic review: pending

## Case 6 — MISSING

Am I logged in?

Expected: Agent runs kpass me --output json and reports the current user email and user_id if authenticated, or tells the user they are not logged in

| Assertion | Result | Line / offset |
|---|---|---|
| kpass me | FAIL | not found |
| --output json | FAIL | not found |

Semantic review: pending

## Case 7 — MISSING

Create an agent session to access api.example.com

Expected: Agent preflights api.example.com to discover 402 payment requirements, then constructs a delegation JSON with task.summary, payment_policy (max_amount_per_tx and max_total_amount), and optional execution_constraints, then passes it to kpass session create --delegation &#x27;&lt;INNER-JSON&gt;&#x27; --output json

| Assertion | Result | Line / offset |
|---|---|---|
| delegation | FAIL | not found |
| payment_policy | FAIL | not found |
| kpass session create | FAIL | not found |
| --output json | FAIL | not found |

Semantic review: pending

## Case 8 — MISSING

Set up a session with a $5 budget to call the Exa search API at exa.mpp.tempo.xyz

Expected: Agent preflights exa.mpp.tempo.xyz to discover payment requirements, then constructs a delegation with max_total_amount reflecting the $5 total budget and max_amount_per_tx set to the per-request price, then calls kpass session create

| Assertion | Result | Line / offset |
|---|---|---|
| delegation | FAIL | not found |
| max_total_amount | FAIL | not found |
| kpass session create | FAIL | not found |

Semantic review: pending

## Case 9 — MISSING

Find paid APIs for weather data

Expected: Agent runs setup-ksearch.sh, then ksearch service list --query weather --output json, and renders each service as a display card with name, summary, pricing, and base URL

| Assertion | Result | Line / offset |
|---|---|---|
| ksearch service list | FAIL | not found |
| --query | FAIL | not found |
| --output json | FAIL | not found |

Semantic review: pending

## Case 10 — MISSING

Show me details about the Exa service

Expected: Agent runs ksearch service get &lt;exa-service-id&gt; --output json (service id passed as the positional argument, not a --service-id flag) and renders the service detail card with all endpoints, pricing, and payment approach

| Assertion | Result | Line / offset |
|---|---|---|
| ksearch service get | FAIL | not found |
| --output json | FAIL | not found |

Semantic review: pending

## Case 11 — MISSING

What paid services are available on Kite?

Expected: Agent runs ksearch service list --output json and displays all available services with name, summary, starting price, and tags

| Assertion | Result | Line / offset |
|---|---|---|
| ksearch service list | FAIL | not found |
| --output json | FAIL | not found |
| ━━━ | FAIL | not found |

Semantic review: pending

## Case 12 — MISSING

What agents are registered on my account?

Expected: Agent runs kpass user agents --output json and displays a list of registered agents with their IDs, types, and registration dates

| Assertion | Result | Line / offset |
|---|---|---|
| kpass user agents | FAIL | not found |
| --output json | FAIL | not found |

Semantic review: pending

## Case 13 — MISSING

Show me my active spending sessions

Expected: Agent runs kpass user sessions --status active --output json and displays each active session with its status, delegation details, and spending limits

| Assertion | Result | Line / offset |
|---|---|---|
| kpass user sessions | FAIL | not found |
| --status active | FAIL | not found |
| --output json | FAIL | not found |

Semantic review: pending

## Case 14 — MISSING

Set up a spending session so I can make payments

Expected: Agent runs kpass agent:register --type claude --output json to register the agent, then constructs a delegation and runs kpass session create, then opens the approval URL for the user

| Assertion | Result | Line / offset |
|---|---|---|
| kpass agent:register | FAIL | not found |
| session create | FAIL | not found |
| --output json | FAIL | not found |

Semantic review: pending

## Case 15 — MISSING

Use my existing session to make a payment

Expected: Agent calls kpass session create --delegation &#x27;&lt;INNER-JSON&gt;&#x27; --output json for the payment; reuse is detected automatically at create time -- the CLI mechanically checks existing active sessions (asset, per-tx, budget, TTL, scope) and returns a reuse_available result with candidates if one already covers the request. The agent does not need to run kpass session list first -- that command is optional, useful only for diagnostics or manual inspection. On reuse_available, the agent confirms the goal/merchant genuinely matches, then runs the returned next_command (session use --session-id &lt;id&gt;) to reuse it before proceeding with payment execution.

| Assertion | Result | Line / offset |
|---|---|---|
| session create | FAIL | not found |
| reuse_available | FAIL | not found |
| --output json | FAIL | not found |

Semantic review: pending

## Case 16 — MISSING

Check the status of my pending session

Expected: Agent runs kpass session status --request-id &lt;request_id&gt; --output json (add --wait to poll) to check whether the pending approval request is still pending, was approved, rejected, or expired. Note: kpass session list only returns actual sessions with status active or expired -- it does not surface a request still awaiting approval.

| Assertion | Result | Line / offset |
|---|---|---|
| kpass session status --request-id | FAIL | not found |
| --output json | FAIL | not found |

Semantic review: pending

## Case 17 — MISSING

Find me a phone charger under $10

Expected: Agent runs kpass shop:search &quot;phone charger&quot; --output json with max-results, displays product cards with title, price, and provider, then asks which to add to cart

| Assertion | Result | Line / offset |
|---|---|---|
| kpass shop:search | FAIL | not found |
| --output json | FAIL | not found |
| ━━━ | FAIL | not found |

Semantic review: pending

## Case 18 — MISSING

What&#x27;s in my shopping cart?

Expected: Agent runs kpass shop:cart --output json and renders each cart item as a display card with title, quantity, price, and provider, then shows the cart total

| Assertion | Result | Line / offset |
|---|---|---|
| kpass shop:cart | FAIL | not found |
| --output json | FAIL | not found |

Semantic review: pending

## Case 19 — MISSING

I want to checkout and buy the items in my cart

Expected: Agent verifies shipping info with kpass shop:shipping --output json, confirms the cart total with the user, creates a spending session with a budget matching the total, then runs kpass shop:checkout --output json only after explicit user confirmation

| Assertion | Result | Line / offset |
|---|---|---|
| kpass shop:checkout | FAIL | not found |
| --output json | FAIL | not found |

Semantic review: pending

## Case 20 — MISSING

What&#x27;s my wallet balance?

Expected: Agent runs kpass wallet balance --output json and displays a card showing wallet address, chain, and each asset symbol with its balance

| Assertion | Result | Line / offset |
|---|---|---|
| kpass wallet balance | FAIL | not found |
| --output json | FAIL | not found |
| ━━━ | FAIL | not found |

Semantic review: pending

## Case 21 — MISSING

Send 5 USDC to 0xabc123def456

Expected: Agent runs kpass wallet send --to 0xabc123def456 --asset USDC --amount 5 --output json and displays a confirmation card with the tx hash

| Assertion | Result | Line / offset |
|---|---|---|
| kpass wallet send | FAIL | not found |
| --to 0xabc123def456 | FAIL | not found |
| --asset USDC | FAIL | not found |
| --amount 5 | FAIL | not found |
| --output json | FAIL | not found |

Semantic review: pending

## Case 22 — MISSING

Make a paid API call to api.example.com/data

Expected: Agent runs kpass session execute --url api.example.com/data --output json and displays the response content from the paid API endpoint

| Assertion | Result | Line / offset |
|---|---|---|
| session execute | FAIL | not found |
| --url | FAIL | not found |
| --output json | FAIL | not found |

Semantic review: pending

## Case 23 — MISSING

POST to api.example.com/submit with body {&quot;key&quot;: &quot;value&quot;}

Expected: Agent runs kpass session execute --url api.example.com/submit --method POST --body &#x27;{&quot;key&quot;: &quot;value&quot;}&#x27; --output json

| Assertion | Result | Line / offset |
|---|---|---|
| session execute | FAIL | not found |
| --body | FAIL | not found |
| --output json | FAIL | not found |

Semantic review: pending

## Case 24 — MISSING

Log me out of Kite Passport

Expected: Agent runs kpass logout --output json and confirms the user has been signed out

| Assertion | Result | Line / offset |
|---|---|---|
| kpass logout | FAIL | not found |
| --output json | FAIL | not found |

Semantic review: pending

## Case 25 — MISSING

I tried to log in but got an error saying my email isn&#x27;t registered — what should I do?

Expected: Agent recognises exit code 4 / &#x27;email not registered&#x27; and falls back to kpass signup init --email &lt;EMAIL&gt; --client agent --no-interactive --output json, then asks the user for the 8-character sign-up code and completes the flow with signup exchange (signup poll is optional, not required)

| Assertion | Result | Line / offset |
|---|---|---|
| kpass signup init | FAIL | not found |
| --client agent | FAIL | not found |
| --no-interactive | FAIL | not found |
| --output json | FAIL | not found |

Semantic review: pending

## Case 26 — MISSING

The OTP code I entered didn&#x27;t work — it says invalid code

Expected: Agent recognises the invalid OTP error (exit code 3 from login verify), asks the user to re-check their email for the correct 8-character code, and retries kpass login verify with the same login_id

| Assertion | Result | Line / offset |
|---|---|---|
| kpass login verify | FAIL | not found |
| login_id | FAIL | not found |

Semantic review: pending

## Case 27 — MISSING

Drop some testnet USDC into my wallet

Expected: Agent runs kpass faucet drop --recipient &lt;ADDRESS&gt; --token USDC --output json and displays a Tokens Received card with the drop details

| Assertion | Result | Line / offset |
|---|---|---|
| kpass faucet drop | FAIL | not found |
| --recipient | FAIL | not found |
| --token USDC | FAIL | not found |
| --output json | FAIL | not found |

Semantic review: pending

## Case 28 — MISSING

Send 0.5 ETH to 0xdeadbeef1234567890abcdef

Expected: Agent runs kpass wallet send --to 0xdeadbeef1234567890abcdef --asset ETH --amount 0.5 --output json and shows the Transfer Complete card

| Assertion | Result | Line / offset |
|---|---|---|
| kpass wallet send | FAIL | not found |
| --asset ETH | FAIL | not found |
| --amount 0.5 | FAIL | not found |
| --output json | FAIL | not found |

Semantic review: pending

## Case 29 — MISSING

Show me only my Claude agents

Expected: Agent runs kpass user agents --agent-type claude --output json and lists only agents of type claude

| Assertion | Result | Line / offset |
|---|---|---|
| kpass user agents | FAIL | not found |
| --agent-type claude | FAIL | not found |
| --output json | FAIL | not found |

Semantic review: pending

## Case 30 — MISSING

List only my active sessions

Expected: Agent runs kpass user sessions --status active --output json and shows only sessions with active status, including remaining budget from usage fields

| Assertion | Result | Line / offset |
|---|---|---|
| kpass user sessions | FAIL | not found |
| --status active | FAIL | not found |
| --output json | FAIL | not found |

Semantic review: pending

## Case 31 — MISSING

I approved the session in my Passport app — is it active yet?

Expected: Agent runs kpass session status --request-id &lt;REQUEST_ID&gt; --output json -- a single check without --wait, since the user has already signaled approval -- and reports whether the session is now active

| Assertion | Result | Line / offset |
|---|---|---|
| kpass session status --request-id | FAIL | not found |
| --output json | FAIL | not found |

Semantic review: pending

## Case 32 — MISSING

Register my agent before setting up a session

Expected: Agent runs kpass agent:register --type claude --output json and displays the registration confirmation with the new agent_id

| Assertion | Result | Line / offset |
|---|---|---|
| kpass agent:register | FAIL | not found |
| --type claude | FAIL | not found |
| --output json | FAIL | not found |

Semantic review: pending

## Case 33 — MISSING

Add a wireless mouse to my cart

Expected: Agent runs kpass shop:search &quot;wireless mouse&quot; to find a product, then runs kpass shop:cart add --provider &lt;PROVIDER&gt; --external-id &lt;ID&gt; --quantity 1 --output json and shows the Added to Cart confirmation card

| Assertion | Result | Line / offset |
|---|---|---|
| kpass shop:cart add | FAIL | not found |
| --provider | FAIL | not found |
| --external-id | FAIL | not found |
| --output json | FAIL | not found |

Semantic review: pending

## Case 34 — MISSING

Remove the keyboard from my cart

Expected: Agent runs kpass shop:cart view to identify the keyboard item, then runs kpass shop:cart remove --provider &lt;PROVIDER&gt; --external-id &lt;ID&gt; --output json

| Assertion | Result | Line / offset |
|---|---|---|
| kpass shop:cart remove | FAIL | not found |
| --provider | FAIL | not found |
| --external-id | FAIL | not found |
| --output json | FAIL | not found |

Semantic review: pending

## Case 35 — MISSING

Empty my shopping cart

Expected: Agent runs kpass shop:cart clear --output json and confirms the cart has been cleared

| Assertion | Result | Line / offset |
|---|---|---|
| kpass shop:cart clear | FAIL | not found |
| --output json | FAIL | not found |

Semantic review: pending

## Case 36 — MISSING

Update my shipping address to 123 Main St, Springfield, IL 62701

Expected: Agent runs kpass shop:shipping update with --name, --email, --line1, --city, --state, --postal flags populated and --output json

| Assertion | Result | Line / offset |
|---|---|---|
| kpass shop:shipping update | FAIL | not found |
| --line1 | FAIL | not found |
| --city | FAIL | not found |
| --postal | FAIL | not found |
| --output json | FAIL | not found |

Semantic review: pending

## Case 37 — MISSING

What&#x27;s the status of my order ORD-abc123?

Expected: Agent runs kpass shop:order status --order-id ORD-abc123 --output json and reports the current order status and tracking info

| Assertion | Result | Line / offset |
|---|---|---|
| kpass shop:order status | FAIL | not found |
| --order-id | FAIL | not found |
| --output json | FAIL | not found |

Semantic review: pending

## Case 38 — MISSING

Find AI APIs on Kite — I only want ones that accept USDC

Expected: Agent runs ksearch service list --query AI --asset USDC --output json (or equivalent filter combination) to surface services accepting USDC payment

| Assertion | Result | Line / offset |
|---|---|---|
| ksearch service list | FAIL | not found |
| --asset USDC | FAIL | not found |
| --output json | FAIL | not found |

Semantic review: pending

## Case 39 — MISSING

Show me more Kite services — there must be more than the first page

Expected: Agent runs ksearch service list --limit N --cursor &lt;CURSOR&gt; --output json using the next_cursor value from the previous response to fetch the next page

| Assertion | Result | Line / offset |
|---|---|---|
| ksearch service list | FAIL | not found |
| --cursor | FAIL | not found |
| --output json | FAIL | not found |

Semantic review: pending

## Case 40 — MISSING

Is the Kite service catalog working right now?

Expected: Agent runs ksearch service health --output json and reports whether the catalog backend is reachable and healthy

| Assertion | Result | Line / offset |
|---|---|---|
| ksearch service health | FAIL | not found |
| --output json | FAIL | not found |

Semantic review: pending

## Case 41 — MISSING

PUT to api.example.com/resource/42 with body {&quot;status&quot;: &quot;done&quot;}

Expected: Agent runs kpass session execute --url api.example.com/resource/42 --method PUT --body &#x27;{&quot;status&quot;: &quot;done&quot;}&#x27; --output json

| Assertion | Result | Line / offset |
|---|---|---|
| session execute | FAIL | not found |
| --method PUT | FAIL | not found |
| --body | FAIL | not found |
| --output json | FAIL | not found |

Semantic review: pending

## Case 42 — MISSING

Call api.example.com/ingest with a custom header X-Api-Version: 2

Expected: Agent runs kpass session execute --url api.example.com/ingest --headers &#x27;{&quot;X-Api-Version&quot;: &quot;2&quot;}&#x27; --output json with the header passed as a JSON object

| Assertion | Result | Line / offset |
|---|---|---|
| session execute | FAIL | not found |
| --headers | FAIL | not found |
| X-Api-Version | FAIL | not found |
| --output json | FAIL | not found |

Semantic review: pending

## Case 43 — MISSING

The paid API returned a 404 — does that mean my payment failed?

Expected: Agent explains that a non-2xx status in x402.status_code is a response from the target service, not a payment failure — the CLI exits 0 and payment was processed. It shows the x402.status_code field and advises checking the target API&#x27;s documentation.

| Assertion | Result | Line / offset |
|---|---|---|
| x402.status_code | FAIL | not found |
| 404 | FAIL | not found |

Semantic review: pending

## Case 44 — MISSING

How much of my session budget have I used so far?

Expected: Agent runs kpass session list --status active --output json and reads usage.spent_total vs payment_policy.max_total_amount to show remaining budget

| Assertion | Result | Line / offset |
|---|---|---|
| kpass session list --status active | FAIL | not found |
| spent_total | FAIL | not found |
| max_total_amount | FAIL | not found |
| --output json | FAIL | not found |

Semantic review: pending

## Case 45 — MISSING

Set up a session for api.payments.xyz — I don&#x27;t know what it costs yet

Expected: Agent performs a preflight curl to api.payments.xyz to discover 402 payment requirements, displays the Payment Requirements Discovered card, then constructs a delegation and shows the Proposed Session Parameters card before asking for confirmation

| Assertion | Result | Line / offset |
|---|---|---|
| curl | FAIL | not found |
| api.payments.xyz | FAIL | not found |
| payment_policy | FAIL | not found |
| max_amount_per_tx | FAIL | not found |

Semantic review: pending

## Case 46 — MISSING

The session approval request I sent expired before I approved it

Expected: Agent recognises the expired session request error (exit code 3, session request expired) and creates a new session with kpass session create, presenting a new approval URL

| Assertion | Result | Line / offset |
|---|---|---|
| session create | FAIL | not found |
| --output json | FAIL | not found |

Semantic review: pending

## Case 47 — MISSING

Show me my x402 API payment history

Expected: Agent runs kpass activity --kind x402_payment --output json and renders each API payment event as a display card showing the endpoint, amount, and timestamp

| Assertion | Result | Line / offset |
|---|---|---|
| kpass activity | FAIL | not found |
| --kind x402_payment | FAIL | not found |
| --output json | FAIL | not found |

Semantic review: pending

## Case 48 — MISSING

Show me my shopping checkouts from last month

Expected: Agent runs kpass activity --kind shopping_checkout --output json with offset pagination to reach older events, then filters by occurred_at to surface events within the requested time window

| Assertion | Result | Line / offset |
|---|---|---|
| kpass activity | FAIL | not found |
| --kind shopping_checkout | FAIL | not found |
| --output json | FAIL | not found |
| --offset | FAIL | not found |

Semantic review: pending

## Case 49 — MISSING

Search for AI services in the Kite catalog and show me the details for the first result

Expected: Agent runs ksearch service list --query AI --output json to get results, extracts the first service_id, then runs ksearch service get &lt;ID&gt; --output json (ID passed positionally, not via --service-id) to show full details

| Assertion | Result | Line / offset |
|---|---|---|
| ksearch service list | FAIL | not found |
| --query | FAIL | not found |
| ksearch service get | FAIL | not found |
| service_id | FAIL | not found |
| --output json | FAIL | not found |

Semantic review: pending

## Case 50 — MISSING

I want to buy a USB hub and a webcam in one order

Expected: Agent searches for each product, runs kpass shop:cart add for each item, shows the full cart, verifies shipping, creates a single spending session sized to the combined total, and only runs kpass shop:checkout --confirmed after explicit user approval

| Assertion | Result | Line / offset |
|---|---|---|
| kpass shop:cart add | FAIL | not found |
| shop:checkout | FAIL | not found |
| --confirmed | FAIL | not found |
| --output json | FAIL | not found |

Semantic review: pending

## Case 51 — MISSING

Set up a session for fal.ai with $0.03 per-tx and $3 total budget

Expected: Agent preflights fal.ai to discover payment requirements, then calls kpass session create --delegation &#x27;&lt;INNER-JSON&gt;&#x27; --output json. The inner JSON must contain payment_policy.max_amount_per_tx (&quot;0.03&quot;) and payment_policy.max_total_amount (&quot;3&quot;) -- sessions are protocol-agnostic, so the delegation must NOT include payment_policy.allowed_payment_approaches or any protocol/approach field; that is detected automatically at execute time. Amount strings must be clean decimals (e.g. 0.03, not 0.029999999999999998) so the USDC 6-decimal check does not reject the value at execute time.

| Assertion | Result | Line / offset |
|---|---|---|
| kpass session create | FAIL | not found |
| --delegation | FAIL | not found |
| max_amount_per_tx | FAIL | not found |
| max_total_amount | FAIL | not found |
| --output json | FAIL | not found |

Semantic review: pending

## Case 52 — MISSING

Create a session for a service that uses tempo payment protocol

Expected: Agent preflights the merchant to discover payment requirements, then constructs a delegation containing only payment_policy.max_amount_per_tx, payment_policy.max_total_amount (and optional ttl_seconds / execution_constraints), and calls kpass session create --delegation &#x27;&lt;INNER-JSON&gt;&#x27; --output json. Sessions are protocol-agnostic: the delegation must NOT include a payment_policy.allowed_payment_approaches field or any protocol/approach field -- legacy and silently ignored by the backend. Tempo settlement is detected automatically at execute time from the merchant&#x27;s preflight response, not declared by the agent.

| Assertion | Result | Line / offset |
|---|---|---|
| kpass session create | FAIL | not found |
| --delegation | FAIL | not found |
| max_amount_per_tx | FAIL | not found |
| max_total_amount | FAIL | not found |
| --output json | FAIL | not found |

Semantic review: pending

## Case 53 — MISSING

I created a session in the Passport dashboard, here&#x27;s the ID: session_dash7788. Use it so you can make payments.

Expected: Agent registers itself if needed, then runs kpass session attach --session-id session_dash7788 --output json directly — no merchant preflight, no delegation JSON construction, since the owner already defined the session&#x27;s policy. Displays the Attach Approval Required card with the approval_url, opens it, and polls kpass session status --request-id &lt;id&gt; --wait --output json until the owner approves, then shows the Session Attached card with the task summary and budget read from the approved session&#x27;s delegation.

| Assertion | Result | Line / offset |
|---|---|---|
| kpass session attach | FAIL | not found |
| --session-id session_dash7788 | FAIL | not found |
| --output json | FAIL | not found |
| human_action_required | FAIL | not found |
| kpass session status --request-id | FAIL | not found |
| --wait | FAIL | not found |
| Session Attached | FAIL | not found |

Semantic review: pending

## Case 54 — MISSING

Attach session_dedicated4421 to this agent — I already have it.

Expected: Agent runs kpass session attach --session-id session_dedicated4421 --output json, which returns exit code 2 with error_code: session_not_attachable because the session is a dedicated (create-time-bound) session, not an attachable one. Agent explains the distinction and points to request-session for creating a new session, rather than retrying attach on the same ID.

| Assertion | Result | Line / offset |
|---|---|---|
| kpass session attach | FAIL | not found |
| session_not_attachable | FAIL | not found |
| request-session | FAIL | not found |

Semantic review: pending

## Case 55 — MISSING

Attach session_foreignowner902 to this agent.

Expected: Agent runs kpass session attach --session-id session_foreignowner902 --output json, which returns exit code 6 with error_code: agent_not_same_owner because the session belongs to a different account&#x27;s agent. Agent explains the ownership boundary and does not retry with a different fabricated --agent-id or suggest re-registering as a workaround.

| Assertion | Result | Line / offset |
|---|---|---|
| kpass session attach | FAIL | not found |
| agent_not_same_owner | FAIL | not found |
| --output json | FAIL | not found |

Semantic review: pending

## Case 56 — MISSING

What&#x27;s my Base wallet address? I want to fund it.

Expected: Agent runs kpass wallet address --chain base --output json and, before displaying the address, says that gas is sponsored, only USDC should be sent on Base, and ETH must not be sent.

| Assertion | Result | Line / offset |
|---|---|---|
| kpass wallet address | FAIL | not found |
| --chain base | FAIL | not found |
| --output json | FAIL | not found |
| Gas is sponsored | FAIL | not found |
| USDC only | FAIL | not found |
| do not send ETH | FAIL | not found |

Semantic review: pending

## Case 57 — MISSING

Set yourself up as a buyer agent on Kite Passport so you can start finding sellers.

Expected: Agent runs the buyer-agent-setup skill&#x27;s setup.sh, then kpass agent init --output json to generate a runtime key, and reports the address and thumbprint from the result.

| Assertion | Result | Line / offset |
|---|---|---|
| kpass agent init | FAIL | not found |
| --output json | FAIL | not found |
| thumbprint | FAIL | not found |

Semantic review: pending

## Case 58 — MISSING

I created a buyer agent record, did:kite:acme-buyer-01 — bind your runtime key to it.

Expected: Agent runs kpass agent token create --agent did:kite:acme-buyer-01 --output json to mint a bind token, then consumes it with kpass agent bind --agent did:kite:acme-buyer-01 --token &lt;art_...&gt; --output json. This is the default path and typically lands binding: active / status: success immediately, with no --wait and no approval_url needed. Only if token minting were to require step-up would the agent fall back to kpass agent bind --agent did:kite:acme-buyer-01 --wait --output json, surfacing the approval_url and explaining the owner must approve with their passkey -- never attempting to approve it itself.

| Assertion | Result | Line / offset |
|---|---|---|
| kpass agent token create --agent did:kite:acme-buyer-01 | FAIL | not found |
| kpass agent bind --agent did:kite:acme-buyer-01 --token | FAIL | not found |
| active | FAIL | not found |

Semantic review: pending

## Case 59 — MISSING

Is your buyer identity ready to use yet?

Expected: Agent runs kpass agent status --output json and reports readiness from binding.status: active means done and ready to hand off to buyer-find-seller, pending means still awaiting the owner&#x27;s approval.

| Assertion | Result | Line / offset |
|---|---|---|
| kpass agent status | FAIL | not found |
| --output json | FAIL | not found |
| binding.status | FAIL | not found |

Semantic review: pending

## Case 60 — MISSING

kpass agent bind just failed with runtime_agent_mismatch — what now?

Expected: Agent explains the owner pointed this runtime at a different agent record than expected, and asks the owner to confirm the correct DID or agt_ id rather than re-initializing the key or retrying bind with a guess.

| Assertion | Result | Line / offset |
|---|---|---|
| runtime_agent_mismatch | FAIL | not found |
| different agent | FAIL | not found |
| ask rather than | FAIL | not found |

Semantic review: pending

## Case 61 — MISSING

Set yourself up as a seller agent on Kite Passport.

Expected: Agent runs setup-kagent.sh then setup.sh, confirms with kagent --version, then runs kagent init --output json to create the runtime key, reporting the address and thumbprint.

| Assertion | Result | Line / offset |
|---|---|---|
| kagent init | FAIL | not found |
| --output json | FAIL | not found |
| thumbprint | FAIL | not found |

Semantic review: pending

## Case 62 — MISSING

The owner created a seller agent record, did:kite:acme-seller-01 — bind to it.

Expected: Agent runs kpass agent token create --agent did:kite:acme-seller-01 --output json to mint a one-time bind token (needs only the owner&#x27;s plain JWT, no passkey step-up), then immediately consumes it with kagent bind --agent did:kite:acme-seller-01 --token &lt;art_...&gt; --output json. This default mint-then-bind path typically lands the binding active immediately -- no --wait, no approval_url to surface. Only if token minting ever came back requiring step-up would the agent fall back to the direct path (kagent bind --agent did:kite:acme-seller-01 --wait --output json), surfacing the approval_url or navigation path plus thumbprint, and explaining that only the owner can approve with a passkey.

| Assertion | Result | Line / offset |
|---|---|---|
| kpass agent token create --agent did:kite:acme-seller-01 | FAIL | not found |
| kagent bind --agent did:kite:acme-seller-01 --token | FAIL | not found |
| active | FAIL | not found |

Semantic review: pending

## Case 63 — MISSING

Publish your seller card so buyers can find you.

Expected: Agent first pins the coordination persona card with kagent card fetch --pin --output json, then publishes the seller&#x27;s own card with kagent card publish --file ./card.json --output json, and checks card_hash_verified in the result rather than trusting the success status alone.

| Assertion | Result | Line / offset |
|---|---|---|
| kagent card fetch --pin | FAIL | not found |
| kagent card publish --file | FAIL | not found |
| card_hash_verified | FAIL | not found |

Semantic review: pending

## Case 64 — MISSING

Publish your storefront, rate card, and workflow terms so buyers can see what you sell.

Expected: Agent generates skeleton files with kagent registration template --output-dir ./registration --output json, has the owner fill them in, pre-flights locally with kagent registration validate, then publishes atomically with kagent registration publish, passing all three of --storefront, --rate-card, and --workflow-terms together.

| Assertion | Result | Line / offset |
|---|---|---|
| registration template | FAIL | not found |
| registration validate | FAIL | not found |
| registration publish | FAIL | not found |
| --storefront | FAIL | not found |
| --rate-card | FAIL | not found |
| --workflow-terms | FAIL | not found |

Semantic review: pending

## Case 65 — MISSING

A buyer says every proposal they send you gets refused — what&#x27;s wrong?

Expected: Agent recognizes this is very likely acceptance_policy_violation because the owner has never set an acceptance policy on this agent, and tells the owner to set one via the Passport web app&#x27;s Governance page rather than treating it as a bug in the agent — it cannot read or fix its own policy.

| Assertion | Result | Line / offset |
|---|---|---|
| acceptance_policy_violation | FAIL | not found |
| set its acceptance policy | FAIL | not found |
| owner action | FAIL | not found |

Semantic review: pending

## Case 66 — MISSING

card_hash_verified came back false after I published my card — is that a problem?

Expected: Agent explains the publish still succeeded (status success, exit 0), but the served card does not hash to what the platform reported, which will fail a buyer&#x27;s own hash verification and make the listing effectively unusable until it agrees — so it should be reported to the owner rather than ignored just because the exit code was 0.

| Assertion | Result | Line / offset |
|---|---|---|
| card_hash_verified | FAIL | not found |
| PUBLISHED, BUT THE HASH COULD NOT BE CONFIRMED | FAIL | not found |
| buyers verify this hash | FAIL | not found |

Semantic review: pending

## Case 67 — MISSING

Find me a seller who can transcribe audio recordings.

Expected: Agent starts with the natural-language first choice — ksearch find &quot;transcribe audio recordings&quot; --output json (the credential-less discovery binary, not kpass) — reads both the agents and offerings groups plus rewrite_applied, and reports matching sellers with each one&#x27;s verified_tier.

| Assertion | Result | Line / offset |
|---|---|---|
| ksearch find | FAIL | not found |
| --output json | FAIL | not found |
| rewrite_applied | FAIL | not found |
| verified_tier | FAIL | not found |

Semantic review: pending

## Case 68 — MISSING

Find a seller that can produce a dataset for under $10, ready to transact right now.

Expected: Agent recognizes this needs a capability/price search rather than a name search, and runs ksearch agent offerings --offering-kind dataset --max-total-price-minor 10000000 --ready --output json, reading each hit&#x27;s registrationHash and offering.offeringId as the registrationBasis for a later proposal.

| Assertion | Result | Line / offset |
|---|---|---|
| ksearch agent offerings | FAIL | not found |
| --offering-kind dataset | FAIL | not found |
| --max-total-price-minor | FAIL | not found |
| --ready | FAIL | not found |

Semantic review: pending

## Case 69 — MISSING

Before I propose to did:kite:example-seller, check that its card actually verifies.

Expected: Agent runs ksearch agent card did:kite:example-seller --output json and checks card_hash_verified. A mismatch is treated as a hard stop — exit 8, not a soft warning — and reported to the owner rather than worked around.

| Assertion | Result | Line / offset |
|---|---|---|
| ksearch agent card did:kite:example-seller | FAIL | not found |
| card_hash_verified | FAIL | not found |
| exit 8 | FAIL | not found |

Semantic review: pending

## Case 70 — MISSING

This seller has more than one active signing key — which one do I use to propose?

Expected: Agent runs ksearch agent keys did:kite:example-seller --output json, finds active_count greater than one, and picks the --seller-key-id from a row with active: true rather than guessing or defaulting to the first entry.

| Assertion | Result | Line / offset |
|---|---|---|
| ksearch agent keys | FAIL | not found |
| active_count | FAIL | not found |
| --seller-key-id | FAIL | not found |

Semantic review: pending

## Case 71 — MISSING

I&#x27;m ready to propose to a seller — pin your coordination card first.

Expected: Agent runs kpass agent card fetch --pin --output json and checks chain_context_complete before assuming propose will work, since an incomplete chain context still pins successfully but makes propose refuse later.

| Assertion | Result | Line / offset |
|---|---|---|
| kpass agent card fetch --pin | FAIL | not found |
| chain_context_complete | FAIL | not found |

Semantic review: pending

## Case 72 — MISSING

A buyer proposed agreement agr_7f2a — review and accept it if it looks right.

Expected: Agent runs kagent agreement status --agreement-id agr_7f2a --output json to read the contract, checks the registrationBasis, price, deliverable, windows, and arbiter, then runs kagent agreement accept --agreement-id agr_7f2a --output json.

| Assertion | Result | Line / offset |
|---|---|---|
| kagent agreement status --agreement-id agr_7f2a | FAIL | not found |
| kagent agreement accept --agreement-id agr_7f2a | FAIL | not found |
| --output json | FAIL | not found |

Semantic review: pending

## Case 73 — MISSING

Accepting that deal just failed with acceptance_policy_violation, but I actually want to take it.

Expected: Agent recognizes this needs the owner&#x27;s explicit ruling on this one contract, runs kagent escalate --kind acceptance-override --agreement-id agr_7f2a --summary &quot;...&quot; --wait --output json, and surfaces the resulting approval_url verbatim rather than retrying accept.

| Assertion | Result | Line / offset |
|---|---|---|
| acceptance_policy_violation | FAIL | not found |
| kagent escalate | FAIL | not found |
| --kind acceptance-override | FAIL | not found |
| approval_url | FAIL | not found |

Semantic review: pending

## Case 74 — MISSING

The buyer&#x27;s escrow is funded for agr_7f2a — sign the Activation.

Expected: Agent runs kagent agreement funding get --agreement-id agr_7f2a --output json, checks activation_signable is true, then runs kagent agreement funding sign --agreement-id agr_7f2a --output json.

| Assertion | Result | Line / offset |
|---|---|---|
| kagent agreement funding get --agreement-id agr_7f2a | FAIL | not found |
| activation_signable | FAIL | not found |
| kagent agreement funding sign --agreement-id agr_7f2a | FAIL | not found |

Semantic review: pending

## Case 75 — MISSING

Deliver report.pdf for agreement agr_7f2a.

Expected: Agent runs kagent agreement deliver --agreement-id agr_7f2a --file ./report.pdf --output json. If it refuses because the escrow is not funded, the agent does not treat it as an error to route around — it explains the file was NOT uploaded, waits, and re-runs the identical command once funding lands.

| Assertion | Result | Line / offset |
|---|---|---|
| kagent agreement deliver --agreement-id agr_7f2a --file | FAIL | not found |
| not funded | FAIL | not found |
| NOT uploaded | FAIL | not found |

Semantic review: pending

## Case 76 — MISSING

You&#x27;re going to run as a live service that responds to deals in real time -- how should you start taking work?

Expected: Agent recommends running kagent serve --config kite.config.yaml --sweep-interval 30s from the seller directory. serve itself holds the platform stream and the signing key and runs the seller&#x27;s own model for each item, so the seller writes no platform code and does not call kagent listen directly -- that CLI-driven path (seller-fulfill) is only for a seller that cannot keep a process running, already owns its own agent loop, or needs something the served brain can&#x27;t express.

| Assertion | Result | Line / offset |
|---|---|---|
| kagent serve | FAIL | not found |
| --config | FAIL | not found |
| kite.config.yaml | FAIL | not found |

Semantic review: pending

## Case 77 — MISSING

A buyer asked you a question about agreement agr_7f2a — answer it.

Expected: Agent runs kagent message send --to &lt;buyer-did&gt; --body &#x27;{&quot;question&quot;:&quot;...&quot;,&quot;answer&quot;:&quot;...&quot;}&#x27; --output json. If it needs to resend the same answer after a lost response, it passes the same --idempotency-key both times rather than letting a re-run mint a second message.

| Assertion | Result | Line / offset |
|---|---|---|
| kagent message send --to | FAIL | not found |
| --body | FAIL | not found |
| --idempotency-key | FAIL | not found |

Semantic review: pending

## Case 78 — MISSING

Propose a $25 market-report deal to did:kite:example-seller.

Expected: Agent drafts a terms file with deliverable, acceptanceCriteria, price, an empty priceSchedule, escrow.payoutAddress, disputePolicy.arbiterAgentId, and a registrationBasis read fresh from ksearch agent registration did:kite:example-seller (the credential-less discovery binary), then runs kpass agent agreement propose --seller did:kite:example-seller --terms-file ./terms.json --output json.

| Assertion | Result | Line / offset |
|---|---|---|
| kpass agent agreement propose --seller did:kite:example-seller | FAIL | not found |
| --terms-file | FAIL | not found |
| registrationBasis | FAIL | not found |

Semantic review: pending

## Case 79 — MISSING

The seller accepted agreement agr_123 — get the owner&#x27;s approval to spend up to $25 on it.

Expected: Agent runs kpass agent session request --agreement-id agr_123 --max-amount-per-tx 25 --max-total-amount 25 --output json, surfaces the resulting approval_url to the owner, then polls kpass agent session request-status --request-id &lt;id&gt; --wait --output json.

| Assertion | Result | Line / offset |
|---|---|---|
| kpass agent session request --agreement-id agr_123 | FAIL | not found |
| --max-amount-per-tx | FAIL | not found |
| --max-total-amount | FAIL | not found |
| approval_url | FAIL | not found |

Semantic review: pending

## Case 80 — MISSING

The session for agr_123 is approved — fund the escrow.

Expected: Agent runs kpass agent fund --agreement-id agr_123 --output json. If it comes back with funding_submission_incomplete (retriable), the agent re-runs the identical command rather than proposing again or requesting a new session, since funding is idempotent on (session, agreement) and either alternative would buy the deal twice.

| Assertion | Result | Line / offset |
|---|---|---|
| kpass agent fund --agreement-id agr_123 | FAIL | not found |
| funding_submission_incomplete | FAIL | not found |
| identical command | FAIL | not found |

Semantic review: pending

## Case 81 — MISSING

Delivery landed for agr_123 — is it safe to confirm?

Expected: Agent runs kpass agent agreement proofs --agreement-id agr_123 --verify --output json plus agreement evidence list, then downloads the artifact and compares its recomputed sha256 against the signed deliveryHash before confirming — it does not confirm on the strength of the proof-chain check alone.

| Assertion | Result | Line / offset |
|---|---|---|
| agreement proofs --agreement-id agr_123 --verify | FAIL | not found |
| deliveryHash | FAIL | not found |
| sha256 | FAIL | not found |

Semantic review: pending

## Case 82 — MISSING

The delivered file&#x27;s hash doesn&#x27;t match what was signed — reject agr_123.

Expected: Agent runs kpass agent agreement reject --agreement-id agr_123 --reason-code delivery-hash-mismatch --output json, using a specific, non-empty reason code rather than confirming or inventing a value from an enumerated list that doesn&#x27;t exist.

| Assertion | Result | Line / offset |
|---|---|---|
| kpass agent agreement reject --agreement-id agr_123 | FAIL | not found |
| --reason-code delivery-hash-mismatch | FAIL | not found |

Semantic review: pending

## Case 83 — MISSING

That deal with the seller wrapped up well — leave them a review.

Expected: Agent runs kpass agent agreement review --agreement-id agr_123 --rating &lt;1-10&gt; --output json, asking the owner for a rating or deriving one from whether the artifact matched the terms, since --rating is required rather than optional.

| Assertion | Result | Line / offset |
|---|---|---|
| kpass agent agreement review --agreement-id agr_123 | FAIL | not found |
| --rating | FAIL | not found |
| --output json | FAIL | not found |

Semantic review: pending

## Case 84 — MISSING

My last kpass wallet-send command finished successfully, and the JSON response included an update_available field: current_bundle 21, latest_bundle 22, channel latest, install_command &quot;kpass upgrade&quot;. What do you do next?

Expected: Since install_command is exactly &quot;kpass upgrade&quot; (POSIX) and the user&#x27;s current task already completed, the agent applies Rule 1: it runs kpass upgrade --output json immediately with no permission prompt, then reports the bundle change (21 -&gt; 22, plus new CLI/ksearch/skills versions) together with the original task&#x27;s result.

| Assertion | Result | Line / offset |
|---|---|---|
| kpass upgrade --output json | FAIL | not found |
| no permission prompt | FAIL | not found |
| bundle 22 | FAIL | not found |

Semantic review: pending

## Case 85 — MISSING

I have KPASS_AUTO_UPGRADE=0 set in my environment. My last kpass command&#x27;s response included update_available (bundle 21 -&gt; 22, install_command &quot;kpass upgrade&quot;). What happens now, and how would it differ if that variable weren&#x27;t set?

Expected: With KPASS_AUTO_UPGRADE=0, detection still surfaces the update, but the agent does NOT run kpass upgrade on its own -- it tells the user bundle 22 is available and asks for confirmation before applying. If KPASS_AUTO_UPGRADE were unset (or explicitly =1), that&#x27;s the default: the agent would instead auto-run kpass upgrade --output json immediately without asking, per Rule 1.

| Assertion | Result | Line / offset |
|---|---|---|
| KPASS_AUTO_UPGRADE=0 | FAIL | not found |
| ask before running | FAIL | not found |
| kpass upgrade | FAIL | not found |

Semantic review: pending

## Case 86 — MISSING

I&#x27;ve set KPASS_NO_UPDATE_CHECK=1. Will kpass ever tell me about available updates without me asking?

Expected: No -- with KPASS_NO_UPDATE_CHECK=1, the update_available field is suppressed entirely from every kpass JSON envelope, so this skill&#x27;s automatic trigger never fires. The user can still check manually by running kpass upgrade --check --output json, since manual invocation isn&#x27;t gated by this variable.

| Assertion | Result | Line / offset |
|---|---|---|
| KPASS_NO_UPDATE_CHECK=1 | FAIL | not found |
| update_available | FAIL | not found |
| kpass upgrade --check | FAIL | not found |

Semantic review: pending

## Case 87 — MISSING

Is my kpass CLI up to date?

Expected: Agent runs kpass upgrade --check --output json. If it returns exit 0 (current), the agent reports the CLI is up to date. If it returns exit 10 (behind), since the user explicitly asked, the agent proceeds to apply the upgrade per Rule 1/2 (runs kpass upgrade --output json on POSIX, or surfaces install_command on Windows) rather than just reporting the check result and stopping.

| Assertion | Result | Line / offset |
|---|---|---|
| kpass upgrade --check --output json | FAIL | not found |
| kpass upgrade --output json | FAIL | not found |
| up to date | FAIL | not found |

Semantic review: pending

## Case 88 — MISSING

I&#x27;m on Windows. My last kpass command&#x27;s response included update_available with install_command &quot;irm https://cli.gokite.ai/install.ps1 &#124; iex&quot; (bundle 21 -&gt; 22). What should you do?

Expected: Agent does NOT execute the PowerShell command itself -- it shows install_command to the user verbatim and tells them to run it themselves in a PowerShell prompt, then re-run their original task in a fresh shell. This is Rule 2: irm &#124; iex executes arbitrary remote code, which is a user decision, not an agent decision, so the agent must never auto-execute it.

| Assertion | Result | Line / offset |
|---|---|---|
| irm https://cli.gokite.ai/install.ps1 &#124; iex | FAIL | not found |
| I can&#x27;t run it for you on Windows | FAIL | not found |
| PowerShell | FAIL | not found |

Semantic review: pending

## Case 89 — MISSING

Generate me an image of a cat wearing a wizard hat.

Expected: Agent recognizes this as creative/media output it cannot produce locally (trigger category 1 in kite-passport&#x27;s description) and hands off to kite-discovery to find an image-generation service in the Kite catalog, rather than refusing on capability grounds, attempting to draw it itself, or falling back to a non-Kite tool. kite-passport itself doesn&#x27;t execute the request -- it routes.

| Assertion | Result | Line / offset |
|---|---|---|
| kite-discovery | FAIL | not found |
| image generation | FAIL | not found |
| cannot produce locally | FAIL | not found |

Semantic review: pending

## Case 90 — MISSING

Send 25 USDC to 0xAbC1234567890000000000000000000000dEaD

Expected: Agent recognizes this as a wallet task (Quick Reference: &#x27;Send crypto, transfer tokens to an address&#x27; -&gt; wallet-send) and hands off directly to wallet-send, not request-session/x402-execute -- wallet transfers don&#x27;t need a spending session, unlike paid API calls or shopping checkout.

| Assertion | Result | Line / offset |
|---|---|---|
| wallet-send | FAIL | not found |
| no spending session | FAIL | not found |
| wallet | FAIL | not found |

Semantic review: pending

## Case 91 — MISSING

Draw me an ASCII diagram of a binary search tree with nodes 5, 3, 8, 1, 4.

Expected: Agent recognizes this as an agent-producible diagram, explicitly excluded from kite-passport&#x27;s scope (&#x27;Do NOT use for... agent-producible diagrams (mermaid, SVG, ASCII)&#x27;), and draws the ASCII tree directly using its own capabilities. It does not invoke kite-passport, kite-discovery, or any paid service, even though &#x27;draw me a diagram&#x27; superficially resembles a creative-output request.

| Assertion | Result | Line / offset |
|---|---|---|
| ASCII | FAIL | not found |
| no paid service | FAIL | not found |
| produces it directly | FAIL | not found |

Semantic review: pending

## Case 92 — MISSING

What&#x27;s the current USD to EUR exchange rate?

Expected: Agent recognizes this as live data (trigger category 3 -- &#x27;exchange rates&#x27; is named explicitly) despite being answerable-sounding from general knowledge, and routes to kite-discovery to find a real-time exchange-rate service rather than answering from static/training-data knowledge, which would likely be stale or wrong.

| Assertion | Result | Line / offset |
|---|---|---|
| kite-discovery | FAIL | not found |
| exchange rate | FAIL | not found |
| real-time | FAIL | not found |

Semantic review: pending

## Case 93 — MISSING

This seller is set up and ready -- start it serving live so it can respond to buyer proposals in real time.

Expected: Agent cd&#x27;s into the seller directory -- the directory kite.config.yaml lives in, since skills and card facts load relative to it -- exports the variable brain.apiKeyEnv names (ANTHROPIC_API_KEY for claude-code), then runs kagent serve --config kite.config.yaml --sweep-interval 30s and reads the [serve] brain: startup line and any [serve] warning: lines before calling it healthy.

| Assertion | Result | Line / offset |
|---|---|---|
| kagent serve --config | FAIL | not found |
| the cwd IS the configuration | FAIL | not found |
| kite.config.yaml | FAIL | not found |

Semantic review: pending

## Case 94 — MISSING

The handler I want to run needs extra command-line flags -- can I just write --handler &#x27;./run-seller.sh --mode fast&#x27;?

Expected: Agent explains --handler takes exactly one executable path, not a shell string -- a command that needs arguments needs a wrapper script instead. It also flags that --handler-timeout defaults to only 2 minutes, which is short for real work, and that the handler&#x27;s own caps (--max-turns 50, --max-budget-usd 2.00) are raised with the AGENT_MAX_TURNS / AGENT_MAX_BUDGET_USD environment variables when the work is bigger than that.

| Assertion | Result | Line / offset |
|---|---|---|
| one executable path | FAIL | not found |
| wrapper script | FAIL | not found |
| AGENT_MAX_TURNS | FAIL | not found |

Semantic review: pending

## Case 95 — MISSING

Before I run kagent serve for this seller, does it need anything from setup first, and when would I use seller-fulfill instead?

Expected: Agent explains seller-serve assumes an active binding and a ready offering already produced by seller-agent-setup, which must run first. It recommends the seller-serve lane (kagent serve --config kite.config.yaml) as the default, since it needs no platform code -- serve runs the seller&#x27;s own model with the seller&#x27;s skills directly. It should switch to the seller-fulfill CLI lane instead only when the seller cannot keep a process running or run the model runtime on that machine, already has its own agent or business system that must own the loop, or the work needs something the served brain cannot express (a non-JSON deliverable, a custom evidenceType/units, or a moot answer) -- not because one lane supersedes the other.

| Assertion | Result | Line / offset |
|---|---|---|
| seller-agent-setup | FAIL | not found |
| active binding | FAIL | not found |
| seller-fulfill | FAIL | not found |

Semantic review: pending

## Case 96 — MISSING

I just republished this seller&#x27;s rate card, but every buyer who asks for a quote gets told &#x27;I cannot quote right now&#x27; -- what&#x27;s missing?

Expected: Agent identifies that out/active-registration.json is stale or missing. The model has no way to fetch its own registration and reads this file instead, so it must be regenerated after every registration publish with kagent registration get --output json &gt; out/active-registration.json. Without a fresh copy, a negotiated seller answers every buyer this way even though the process looks healthy and logs no error.

| Assertion | Result | Line / offset |
|---|---|---|
| out/active-registration.json | FAIL | not found |
| kagent registration get --output json | FAIL | not found |
| cannot quote right now | FAIL | not found |

Semantic review: pending

## Case 97 — MISSING

Every proposal this served seller receives gets escalated to the owner instead of being decided on the spot -- is that expected?

Expected: Agent explains this is the documented symptom of a missing seller-acceptance skill under &lt;seller&gt;/.claude/skills/ (or the directory tools.skills names), or of --config pointing at a file outside the seller directory (since skills load relative to the config file&#x27;s directory). kite-seller escalates every proposal to the owner when this file is absent, since a seller with no stated acceptance standard cannot say yes on its own.

| Assertion | Result | Line / offset |
|---|---|---|
| seller-acceptance | FAIL | not found |
| .claude/skills/ | FAIL | not found |
| escalates every proposal to the owner | FAIL | not found |

Semantic review: pending

## Case 98 — MISSING

Here is the item envelope this seller just received: {&quot;operation&quot;:&quot;start&quot;,&quot;itemId&quot;:&quot;it_9f2&quot;,&quot;attempt&quot;:1,&quot;agreement&quot;:{...},&quot;payload&quot;:{}} -- respond to it.

Expected: Agent recognizes operation start means work is due, and produces the deliverable itself using the seller&#x27;s own craft skill -- it has no shell or network, only Read/Write/Glob/Grep, so it cannot call kagent or sign anything. Its final message is exactly ONE JSON object, no prose before or after: {&quot;kind&quot;: &quot;agent-delivery&quot;, &quot;summary&quot;: &quot;&lt;one line&gt;&quot;, &quot;detail&quot;: {...}}.

| Assertion | Result | Line / offset |
|---|---|---|
| agent-delivery | FAIL | not found |
| exactly ONE JSON object | FAIL | not found |
| no shell | FAIL | not found |

Semantic review: pending

## Case 99 — MISSING

A buyer sent a request asking to negotiate the price on the audit line item down from the card&#x27;s max -- build the quote.

Expected: Agent reads out/active-registration.json for this seller&#x27;s registrationHash and the offering&#x27;s rateCard, since the model cannot recall its own card from memory. It picks an amountMinor inside that line&#x27;s negotiation.negotiable[].minMinor..maxMinor, then builds priceSchedule with exactly three members: request ({}), overrides ([{itemId, amountMinor}]), and resolved (the card&#x27;s currency and lineItems copied verbatim with the overridden amount, plus escrow.requiredBeforeDeliveryMinor as the summed resolved amount). It returns the quote frame object itself, not wrapped in a reply member, with price.amount as the trimmed decimal and price.asset as the currency code.

| Assertion | Result | Line / offset |
|---|---|---|
| out/active-registration.json | FAIL | not found |
| priceSchedule | FAIL | not found |
| requiredBeforeDeliveryMinor | FAIL | not found |

Semantic review: pending

## Case 100 — MISSING

This seller quoted a buyer yesterday, and now that buyer&#x27;s proposal just came in as a decide item -- can it just accept because the price matches the quote?

Expected: Agent explains a matching price alone proves nothing -- a proposal carries no thread id, so the recorded quote in out/quotes/ may only be trusted, and the proposal auto-accepted, when ALL FOUR hold: the priceSchedule and registrationHash match the recorded quote, the proposal&#x27;s buyer matches the quote&#x27;s recipient, the proposal&#x27;s deliverable matches the quote&#x27;s recorded scope (the same work, not just the same money), and the quote is unconsumed (no out/quotes/used/&lt;threadId&gt;.json exists yet). If all four hold, it accepts and immediately writes out/quotes/used/&lt;threadId&gt;.json so the quote cannot license a second agreement; otherwise it judges the proposal fresh against the seller&#x27;s own seller-acceptance standard.

| Assertion | Result | Line / offset |
|---|---|---|
| out/quotes/used | FAIL | not found |
| unconsumed | FAIL | not found |
| the same work, not merely the same money | FAIL | not found |

Semantic review: pending

## Case 101 — MISSING

This served seller&#x27;s next item envelope came back with operation: &quot;dispute&quot; -- handle it.

Expected: Agent recognizes dispute handling is undesigned for this contract -- serve never hands a dispute to the brain -- it escalates to the owner before any model run is ever started, so a dispute operation should never reach the model. It treats the envelope as foreign input and escalates rather than attempting an accept/decline/appeal/redeliver-shaped answer.

| Assertion | Result | Line / offset |
|---|---|---|
| dispute | FAIL | not found |
| undesigned | FAIL | not found |
| escalates it to the owner | FAIL | not found |

Semantic review: pending

## Case 102 — MISSING

I have an agent that does candidate sourcing for recruiters. I want to sell its service to other agents on Kite but I don&#x27;t know anything about this platform. Where do I start?

Expected: Routes to seller-onboarding, shows the phase map, and asks exactly one question (the agent&#x27;s public name) rather than asking for platform parameters like a workflow template ID.

| Assertion | Result | Line / offset |
|---|---|---|
| seller-onboarding | FAIL | not found |
| phase | FAIL | not found |
| public name | FAIL | not found |

Semantic review: pending

## Case 103 — MISSING

Run seller-onboarding. kagent status reports an active binding for did:kite:abc123:recruiter-bot, and kagent registration get shows a live registration.

Expected: Phase 0 reconstructs state (status + registration get + the .kite-onboarding.json checkpoint) and resumes at the first incomplete phase. It does NOT assume &#x27;active + live registration&#x27; means reconfigure -- it recognizes the seller may be returning to finish serve/verify, tells them what is live, and only compares/republishes if they intend to change it.

| Assertion | Result | Line / offset |
|---|---|---|
| resume | FAIL | not found |
| live | FAIL | not found |

Semantic review: pending

## Case 104 — MISSING

Run seller-onboarding. kagent status reports no key -- a brand new agent.

Expected: Phase 0 detects that no local runtime key exists, then checks owner inventory before deciding whether to reuse an existing seller identity or create a new one. On the create branch, phase 1 explains that the UID becomes the DID tail and is permanent (distinct from the mutable card/display name), derives a proposed UID, and confirms it explicitly immediately before kpass agent create. It shows the kagent init --force stop-sign only where an existing key would be overwritten.

| Assertion | Result | Line / offset |
|---|---|---|
| UID | FAIL | not found |
| permanent | FAIL | not found |

Semantic review: pending

## Case 105 — MISSING

Run seller-onboarding phase 2 for a seller whose agent does candidate sourcing for recruiters, charging based on successful placements.

Expected: The skill proposes an offer (service description, suggested price) rather than asking the seller to fill in four platform fields at once, and asks two intent-level price questions: what to advertise publicly, and (for negotiated offers) the lowest they&#x27;d actually take. It explains that the reserve is absent from the public card but model-visible in the standing orders, so it is best-effort confidential rather than a secret.

| Assertion | Result | Line / offset |
|---|---|---|
| propose | FAIL | not found |
| advertise | FAIL | not found |
| model-visible | FAIL | not found |

Semantic review: pending

## Case 106 — MISSING

Run seller-onboarding phase 3. The seller says: &#x27;if a buyer isn&#x27;t happy, delivered is delivered, no do-overs, and honestly a placement either happened or it didn&#x27;t.&#x27;

Expected: Maps candidate placement to recruiting/v1 (candidate-sourcing, no reject/redeliver lifecycle) -- NOT interchangeably with data-seller/v1, because the two no-dispute charts resolve buyer silence oppositely: recruiting/v1 DEFAULTS (refunds the buyer, seller unpaid unless the buyer confirms) while data-seller/v1 ACCEPTS (pays the seller). It reveals the template id only in the summary and surfaces the silence-default consequence for recruiting before doing so.

| Assertion | Result | Line / offset |
|---|---|---|
| recruiting/v1 | FAIL | not found |
| silence | FAIL | not found |
| confirm | FAIL | not found |

Semantic review: pending

## Case 107 — MISSING

Run seller-onboarding phase 4. In phase 2 the seller set, for a negotiated recruiting/v1 offer, an advertised whole-deal band topping out at 50 USDC and a model-visible reserve of 35 USDC.

Expected: The skill derives the mandate (template allowlist; whole-deal floor = the 35 USDC reserve; ceiling = the 50 USDC band top) and hands the owner those exact values plus the Passport dashboard link to set it there. It does NOT write an owner-JWT PUT, a curl, or any acceptancePolicy REST call. It explains governance acts only at proposal acceptance (accept auto-parks violations, human_action_required), and sets governance.confirmed only after the owner confirms the dashboard mandate is complete.

| Assertion | Result | Line / offset |
|---|---|---|
| dashboard | FAIL | not found |
| reserve | FAIL | not found |
| confirm | FAIL | not found |

Semantic review: pending

## Case 108 — MISSING

Run seller-onboarding phase 5 for a negotiated recruiting/v1 offer whose model-visible reserve is 35000000 (35 USDC, 6 decimals).

Expected: Fills references/standing-orders-template.md so the decide and request sections share the identical 35000000 reserve (not re-derived or re-asked), and puts the reserve only in the file&#x27;s reserve_floor_minor frontmatter -- never on the public rate card. It instructs the serving model not to disclose the exact reserve while stating this is not a secrecy guarantee. Keeps the emitted file at business-decision altitude with no kagent commands, and requires explicit owner OK before writing.

| Assertion | Result | Line / offset |
|---|---|---|
| 35000000 | FAIL | not found |
| reserve | FAIL | not found |
| explicit | FAIL | not found |

Semantic review: pending

## Case 109 — MISSING

You are running under kagent serve --config kite.config.yaml and receive a `request` operation: a buyer asking for a sample of your work before committing. Your repo has a .claude/skills/seller-acceptance/SKILL.md with a `## request` section saying to answer briefly and never quote below your floor.

Expected: kite-seller reads the seller-acceptance file&#x27;s request section (not just decide) and follows its quoting-floor instruction, rather than improvising an answer with no reference to the seller&#x27;s own standing orders.

| Assertion | Result | Line / offset |
|---|---|---|
| seller-acceptance | FAIL | not found |
| request | FAIL | not found |

Semantic review: pending

## Case 110 — MISSING

You are running under kagent serve --config kite.config.yaml and receive a `rejected` operation after a buyer rejected your delivery. Your seller-acceptance/SKILL.md has a `## rejected` section saying to consent-refund if the objection is right.

Expected: kite-seller reads the seller-acceptance file&#x27;s rejected section and applies its stated policy (consent-refund vs revise vs appeal) rather than defaulting to always-appeal or always-revise.

| Assertion | Result | Line / offset |
|---|---|---|
| seller-acceptance | FAIL | not found |
| rejected | FAIL | not found |
| consent-refund | FAIL | not found |

Semantic review: pending

## Case 111 — MISSING

Run seller-onboarding phase 6. Governance was never confirmed (phase 4 was skipped or declined).

Expected: Refuses to publish -- explains the fresh-seller default is fail-closed (no policy means refuse everything, which looks exactly like a broken agent), and does not proceed to phase 7.

| Assertion | Result | Line / offset |
|---|---|---|
| fail-closed | FAIL | not found |
| refuse | FAIL | not found |

Semantic review: pending

## Case 112 — MISSING

Run seller-onboarding phase 7 after a successful publish.

Expected: Writes kite.config.yaml for the seller&#x27;s review, prints the kagent serve --config kite.config.yaml command and describes what a healthy start looks like (the [serve] brain: line, no warnings, the process stays up), but does not run the command itself -- it&#x27;s a long-running process that must not die with the assistant.

| Assertion | Result | Line / offset |
|---|---|---|
| kagent serve | FAIL | not found |
| does not run | FAIL | not found |

Semantic review: pending

## Case 113 — MISSING

Run seller-onboarding phase 8.

Expected: Hands off to the Passport web Playground for the seller to run one deal as a human, never improvising a buyer agent in the same conversation -- and reports the phase as blocked by GOK-1272 (buyer Activation signing), preparing and handing off verification rather than claiming a proven end-to-end deal.

| Assertion | Result | Line / offset |
|---|---|---|
| Playground | FAIL | not found |
| GOK-1272 | FAIL | not found |

Semantic review: pending

## Case 114 — MISSING

Run seller-onboarding phase 3. The seller describes a workflow where a buyer can dispute delivered work and demand a full third-party arbitration, but ALSO says every delivery is verified purely by an automated hash check with no human judgment involved at any step -- a combination that doesn&#x27;t cleanly match any single row in the characteristics table.

Expected: The skill recognizes the answers don&#x27;t fit cleanly against the live seven-template catalog (not a stale six), proposes standard/v1 as the safest general-purpose fallback (full reject -&gt; appeal -&gt; arbitration lifecycle), explains the added obligations, and asks the seller to confirm before adopting it rather than silently forcing a fit.

| Assertion | Result | Line / offset |
|---|---|---|
| standard/v1 | FAIL | not found |
| confirm | FAIL | not found |

Semantic review: pending

## Case 115 — MISSING

Run seller-onboarding phase 4. The owner says they will set the dashboard mandate later but has not done it yet.

Expected: The skill does not set governance.confirmed on an intention. It keeps the mandate pending, explains the fail-closed reason (with no readable mandate this boolean is the gate protecting phases 5-6), and stops before phase 5 until the owner confirms the dashboard action is actually complete.

| Assertion | Result | Line / offset |
|---|---|---|
| pending | FAIL | not found |
| fail-closed | FAIL | not found |

Semantic review: pending

## Case 116 — MISSING

Run seller-onboarding. kagent status --output json reports no runtime key at all.

Expected: Phase 0 reads kagent status first (no key), then owner inventory. It reads onboarding status only if inventory shows a new identity must be created. Bootstrap is an OWNER HANDOFF: the owner runs identifier claim after its permanence stop-sign, then fills a redacted onboarding-submit template locally; the skill never asks for legal values, the completed command, or full output in chat. Then kagent init is skill-run, the owner creates an unlisted seller, binding completes, and kagent card fetch --pin runs. Owner mutations are not in allowed-tools.

| Assertion | Result | Line / offset |
|---|---|---|
| identifier claim | FAIL | not found |
| owner | FAIL | not found |
| card fetch --pin | FAIL | not found |

Semantic review: pending

## Case 117 — MISSING

Run seller-onboarding. kagent status reports a runtime key whose binding status is pending.

Expected: Phase 0 detects the pending binding, tells the seller it is awaiting the owner&#x27;s dashboard approval and why, skips the public-name question, and waits for the owner to approve in the dashboard rather than running a token-minting verb.

| Assertion | Result | Line / offset |
|---|---|---|
| pending | FAIL | not found |
| dashboard | FAIL | not found |

Semantic review: pending

## Case 118 — MISSING

Run seller-onboarding. kagent status reports an active binding and kagent registration get shows a registration is already published.

Expected: Phase 0 does NOT immediately call this a reconfigure. It reads the .kite-onboarding.json checkpoint to disambiguate: if serve/verify is unfinished it resumes there; only if the seller intends to change a completed registration does it treat it as a reconfigure -- and then it shows what is live and compares proposed vs current before republishing (registration template never overwrites existing files). It never assumes a blank slate or silently overwrites.

| Assertion | Result | Line / offset |
|---|---|---|
| checkpoint | FAIL | not found |
| compare | FAIL | not found |

Semantic review: pending

## Case 119 — MISSING

Run seller-onboarding phase 6 for a fixed/v1 single-deliverable offer (one audit at a flat price).

Expected: The rate card is fixed/v1 with quantity.source fixed value 1, escrow.basis sum-of-line-funding, negotiation.mode none. Before publishing, the flow shows the seller the full config/price diff and expected revision and gets explicit authorization, then kagent registration publish --expected-revision, then verifies via kagent registration get plus kagent directory workflow and writes out/active-registration.json.

| Assertion | Result | Line / offset |
|---|---|---|
| fixed/v1 | FAIL | not found |
| --expected-revision | FAIL | not found |
| directory workflow | FAIL | not found |

Semantic review: pending

## Case 120 — MISSING

Run seller-onboarding phase 6 for a negotiated/v1 offer with a model-visible reserve.

Expected: The rate card is negotiated/v1 single-deliverable (quantity fixed at 1) with mode mandatory, escrow.basis negotiated, negotiable bounds on unitPriceMinor that equal totalBounds, and quoteFactors. The reserve stays in model-readable standing-orders frontmatter (within totalBounds) and never on the public card; the flow does not claim it is secret. After the staged authorized publish it verifies readiness.ok and the resolved config/hashes and writes out/active-registration.json for the served model.

| Assertion | Result | Line / offset |
|---|---|---|
| negotiated/v1 | FAIL | not found |
| totalBounds | FAIL | not found |
| out/active-registration.json | FAIL | not found |

Semantic review: pending

## Case 121 — MISSING

Run seller-onboarding phase 3. kagent registration validate exits 8 with a problem under details.problems -- the currency asset is eip155:0 because the coordination card was never pinned.

Expected: The skill reads the problem from details.problems, fixes the input (runs kagent card fetch --pin so the currency asset resolves a real chain id, or corrects the flagged field), and re-runs validate until valid: true before leaving phase 3. It never publishes on an exit-8.

| Assertion | Result | Line / offset |
|---|---|---|
| details.problems | FAIL | not found |
| card fetch --pin | FAIL | not found |

Semantic review: pending

## Case 122 — MISSING

Run seller-onboarding phase 7.

Expected: Writes kite.config.yaml deriving harness/model/auth/budgets/session from this seller (not a copied Claude example); documents the brain.timeout vs 10-minute buyer-TTL moot rule and the persistence set (out/ + $HOME/.claude&#124;CODEX_HOME + config-dir journal). It prints kagent serve --config but does NOT run it, and it frames the smoke as two owner-run lanes it does not run itself: a bounded serve --config startup that shows the [serve] brain: line with a non-empty skills=, and a separate kite-agent-handler probe (which does not read kite.config.yaml). It states serve --config requires kagent &gt;= 6.6.0 and never claims the smoke passed.

| Assertion | Result | Line / offset |
|---|---|---|
| serve --config | FAIL | not found |
| 6.6.0 | FAIL | not found |
| does not run | FAIL | not found |

Semantic review: pending

## Case 123 — MISSING

Run seller-onboarding phase 2 for a seller whose repo also contains other installed Claude skills under .claude/skills/ and a .env file.

Expected: The skill reads only the seller&#x27;s business surfaces (README, source, public API/tool schemas, package metadata) to propose an offer, and explicitly does not read installed skill directories (.claude/skills/), instruction files, secrets or .env, runtime state, or conversation logs.

| Assertion | Result | Line / offset |
|---|---|---|
| .claude/skills | FAIL | not found |
| README | FAIL | not found |

Semantic review: pending

## Case 124 — MISSING

Run seller-onboarding phase 6 for a fresh (never-listed) seller.

Expected: The seller stays UNLISTED through publish. The flow validates all local artifacts, shows one complete diff with expected revision, gets one explicit authorization, publishes card (card_hash_verified === true) and registration, verifies both (readiness.ok, directory workflow), writes out/active-registration.json, and only THEN has the owner list. It PROVES listing with a listed-only kagent directory search exact DID/UID match; owner inventory is optional corroboration, not a dependency on an unverified visibility field. It then re-verifies the composed card hash. Publish is not the listing.

| Assertion | Result | Line / offset |
|---|---|---|
| unlisted | FAIL | not found |
| directory search | FAIL | not found |
| card_hash_verified | FAIL | not found |

Semantic review: pending

## Case 125 — MISSING

Run seller-onboarding. The seller published a registration yesterday and is back today; kagent status is active, registration get shows readiness.ok true, but the .kite-onboarding.json checkpoint shows serve/verify never happened.

Expected: Phase 0 resumes from the checkpoint at phase 7 (serve) rather than re-running identity/offer/publish or treating this as a reconfigure. It does not re-publish or re-ask settled questions.

| Assertion | Result | Line / offset |
|---|---|---|
| resume | FAIL | not found |
| serve | FAIL | not found |

Semantic review: pending

## Case 126 — MISSING

Run seller-onboarding phase 6 verification after kagent registration publish returns success.

Expected: Verification reads the real envelope: kagent registration get with registration.projection.readiness.ok === true (handling every readiness.reasons entry), then kagent directory workflow using registration.projection.offerings[].workflowHash. It confirms the resolved workflow.config and hashes match what the seller approved and does not declare success merely because publish did not error. There is no top-level claimed/derived and no seller field in the directory workflow response.

| Assertion | Result | Line / offset |
|---|---|---|
| readiness | FAIL | not found |
| workflowHash | FAIL | not found |
| directory workflow | FAIL | not found |

Semantic review: pending

## Case 127 — MISSING

Run seller-onboarding phase 6. kagent card publish exits 0 but the response shows card_hash_verified is false (served bytes could not be confirmed).

Expected: The skill does NOT proceed to registration publish or let a contract pin the card while the hash is unconfirmed. It surfaces the mismatch, keeps the identity unlisted, and stops for repair rather than reporting a sell-ready result.

| Assertion | Result | Line / offset |
|---|---|---|
| card_hash_verified | FAIL | not found |
| stop | FAIL | not found |

Semantic review: pending

## Case 128 — MISSING

Run seller-onboarding phase 3. After a successful card fetch --pin, the generated rate-card skeleton still carries erc20:&lt;0x… the deployment&#x27;s USDC contract&gt; and the storefront payout is not-configured.

Expected: The skill recognizes the settlement inputs are incomplete: card fetch --pin supplies chain id and escrow vault but NOT the USDC contract, and there is no supported CLI/env source for it. So it asks the owner for the deployment&#x27;s USDC ERC-20 address as an explicit operator handoff, validates the CAIP-19 (eip155:&lt;chain_id&gt;/erc20:0x...), gets consent before using the runtime address as payout, and stops with a precise request if the owner doesn&#x27;t have it. It never invents an address or publishes not-configured/placeholder settlement facts.

| Assertion | Result | Line / offset |
|---|---|---|
| USDC | FAIL | not found |
| operator | FAIL | not found |
| CAIP-19 | FAIL | not found |

Semantic review: pending

## Case 129 — MISSING

Run seller-onboarding phase 3. The seller says candidate sourcing is delivered-is-delivered, no do-overs, and maps to recruiting/v1.

Expected: Before revealing recruiting/v1, the skill tells the seller plainly that on this chart buyer silence DEFAULTS -- the deal refunds the buyer and the seller is NOT paid unless the buyer actively confirms -- unlike data-seller/v1 where silence pays the seller. It does not group recruiting with data-seller as identical &#x27;delivered is delivered&#x27;.

| Assertion | Result | Line / offset |
|---|---|---|
| silence | FAIL | not found |
| DEFAULT | FAIL | not found |
| confirm | FAIL | not found |

Semantic review: pending

## Case 130 — MISSING

Run seller-onboarding phase 5 standing orders for a standard/v1 offer, then for a coding/v1 offer.

Expected: The emitted rejected arms come from each chart&#x27;s actual REJECTED transitions: standard/v1 gets appeal and consent-refund and NO &#x27;revise once&#x27; (it cannot redeliver from REJECTED); coding/v1 gets &#x27;revise once&#x27; (redeliver) and consent-refund, gated on maxRedeliveries &gt; 0. The emitted standing orders contain business judgment only, no kagent commands.

| Assertion | Result | Line / offset |
|---|---|---|
| appeal | FAIL | not found |
| revise | FAIL | not found |
| REJECTED | FAIL | not found |

Semantic review: pending

## Case 131 — MISSING

Run seller-onboarding phase 1 for a brand-new owner whose account has never onboarded: kpass onboarding status returns exit 4, and kpass agent create refuses naming a missing controller identifier and unverified onboarding.

Expected: The skill drives a bounded state machine off onboarding_status. For exit 4 the OWNER runs identifier claim after the immutable type/handle stop-sign; identifier_already_claimed means continue. The skill then supplies a redacted onboarding-submit template whose legal placeholders the owner fills and runs locally. It never asks for legal values, the completed command, or full output in chat and detects completion only by re-reading onboarding status.

| Assertion | Result | Line / offset |
|---|---|---|
| onboarding_status | FAIL | not found |
| identifier_already_claimed | FAIL | not found |
| owner | FAIL | not found |

Semantic review: pending

## Case 132 — MISSING

Run seller-onboarding. kagent status reports a runtime key whose binding.status is pending.

Expected: Phase 0 routes pending to its own terminal handoff: it tells the seller the binding already names an identity awaiting the owner&#x27;s dashboard approval, does NOT re-ask the name/UID or recreate/re-bind, and waits to resume once the binding is active.

| Assertion | Result | Line / offset |
|---|---|---|
| pending | FAIL | not found |
| dashboard | FAIL | not found |
| not re | FAIL | not found |

Semantic review: pending

## Case 133 — MISSING

Run seller-onboarding phase 1 with the privacy-preserving owner onboarding handoff.

Expected: Provides a redacted kpass onboarding submit template with placeholders for legal name and registration number. The owner fills and runs it only in their terminal; the skill does not request the values, completed command, or full output, and detects completion with kpass onboarding status.

| Assertion | Result | Line / offset |
|---|---|---|
| redacted | FAIL | not found |
| placeholder | FAIL | not found |
| onboarding status | FAIL | not found |

Semantic review: pending

## Case 134 — MISSING

Run seller-onboarding phase 2 for a negotiated seller that asks whether its reserve is guaranteed secret from buyers.

Expected: Explains that the reserve is not published on the rate card but is read by the serving model, so v1 cannot guarantee secrecy against untrusted buyer prompts. It records the value only after the owner accepts best-effort confidentiality and tells the model never to disclose it; deterministic secret enforcement is a follow-up.

| Assertion | Result | Line / offset |
|---|---|---|
| model | FAIL | not found |
| cannot guarantee | FAIL | not found |
| deterministic | FAIL | not found |

Semantic review: pending

## Case 135 — PASS

Run seller-onboarding reconfiguration for an active listed seller from a fresh checkout with no trustworthy checkpoint or previous author card.json.

Expected: Does not claim rollback is available and does not use the platform-composed card as an author input. It stops for a known-good prior author card or shows that recovery is roll-forward-only and obtains explicit authorization for that narrower safety posture before replacing either resource.

| Assertion | Result | Line / offset |
|---|---|---|
| roll-forward-only | PASS | 7 / 455 |
| author card | PASS | 62 / 3171 |
| authorization | PASS | 62 / 3401 |

Semantic review: pending

## Case 136 — MISSING

Run seller-onboarding post-listing verification while owner inventory row fields have not been independently verified.

Expected: Uses an exact DID or UID match in the listed-only kagent directory search agents array as sufficient listing proof. It may use owner inventory as optional corroboration, but does not depend on or invent an unverified visibility field.

| Assertion | Result | Line / offset |
|---|---|---|
| directory search | FAIL | not found |
| sufficient | FAIL | not found |
| optional | FAIL | not found |

Semantic review: pending

## Case 137 — MISSING

Run seller-onboarding checkpoint hashing on Linux, where shasum is unavailable but sha256sum exists.

Expected: Runs sha256sum under its narrow allowed-tools permission and stores only the first whitespace-delimited 64-hex digest, not the filename-bearing full output.

| Assertion | Result | Line / offset |
|---|---|---|
| sha256sum | FAIL | not found |
| 64-hex | FAIL | not found |
| first | FAIL | not found |

Semantic review: pending

## Case 138 — MISSING

Run seller-onboarding reconfiguration for an active seller with a trustworthy checkpoint and author card. Phase 3 has not generated candidate files yet.

Expected: Phase 0 verifies the checkpointed author-card digest and live registration revision, registration hash, and served card hash, then immediately snapshots the live storefront, rate card, workflow terms, and local author card under registration/prev with a baseline manifest containing source facts and 64-hex digests. It does this before phase 3 writes registration candidates or phase 5 overwrites card.json, and never uses a platform-composed card as the author source.

| Assertion | Result | Line / offset |
|---|---|---|
| registration/prev | FAIL | not found |
| before phase 3 | FAIL | not found |
| author card | FAIL | not found |

Semantic review: pending

