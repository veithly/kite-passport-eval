# Security boundaries

Proofroom is a text evaluation tool, not a wallet, execution sandbox or model safety certification.

The included live adapter disables Claude tools, customizations and integrations. It must never be modified to run payment, signing or deployment commands merely to improve a score. Model text can contain commands, placeholders, false claims or malformed tool-call markup; reports display it as untrusted escaped text and never execute it.

Only run adapters you trust. The process runner avoids shell interpolation, caps time/output, and kills its own POSIX process group. It does not restrict filesystem access, network access, inherited environment or deliberately detached processes. Use an isolated container/account with minimal credentials for untrusted executable code. Do not use a production wallet environment for evaluation.

The supplied adapter reads public prompts and skill documents and uses the user's existing model CLI authentication. No model key is embedded in this repository or required in CI. Raw stderr is hashed rather than published because provider diagnostics may contain secrets. Hashes detect accidental drift, not a malicious party who replaces both artifacts and their hashes.

HTML output escapes prompts, expected outputs, assertions, responses and review text; no remote assets, analytics or model-generated HTML are loaded. Content Security Policy disallows network/resource loading except the trusted inline CSS/JavaScript. External review of the generated report is still advisable before publishing private corpora.

A conservative release pattern scan checks for private-key headers, common GitHub/provider token patterns and local user paths. Passing that scan does not prove absence of sensitive information. Never publish raw captures from private user prompts without authorization. Public evidence here is derived from the MIT-licensed upstream scenarios, not from the operator's inbox, browser history, account balances or filesystem.

For a suspected vulnerability, use GitHub private vulnerability reporting where available, or contact the maintainer privately. Do not paste credentials into a public issue. Include a minimal redacted fixture and the affected runner version.
