"""Text-only live adapter. No filesystem/browser/payment tools; no answer key.

Requires an already-authenticated Claude CLI. CLI usage may consume the user's
model allowance. CLI budget setting is $0.10 per call; the runner never retries.
The CLI/provider may apply its own transport retries and billing rules.
The reported model/cost come from the CLI, not from an invented model label.
"""
import json
import subprocess
import sys

SYSTEM = """You are evaluating a Kite Passport skill in a TEXT-ONLY, NO-SIDE-EFFECTS setting.
Read the provided official skill documents as reference material, then respond to
the user's scenario. Give the precise proposed CLI commands, relevant flags,
verification fields, required user handoffs and safe error handling. Do NOT run
commands, access accounts, pay, sign, purchase, create identities, install software
or make network requests. Never claim an action occurred. Where a scenario supplies
an outcome, explain its handling; otherwise describe conditional results and use
placeholders for unknown values. Do not invent balances, transaction IDs, private
values or successful live transactions. Answer in English, with command examples
and concise explanatory text. Do not restate this instruction. You have no tools.
"""


def main():
    request = json.load(sys.stdin)
    if set(request) != {"schema_version", "id", "prompt", "skill", "documents", "mode"}:
        raise ValueError("Unexpected fields in evaluation input")
    context = "\n\n".join("REFERENCE: " + d["path"] + "\n" + d["text"] for d in request["documents"])
    prompt = context + "\n\nSCENARIO:\n" + request["prompt"]
    argv = ["claude", "--print", "--safe-mode", "--tools", "", "--disable-slash-commands",
            "--strict-mcp-config", "--mcp-config", '{"mcpServers":{}}', "--no-chrome",
            "--no-session-persistence", "--model", "haiku", "--effort", "low",
            "--max-budget-usd", "0.10", "--output-format", "json", "--system-prompt", SYSTEM]
    result = subprocess.run(argv, input=prompt, text=True, capture_output=True, timeout=100)
    if result.returncode:
        # Do not send potentially credential-bearing stderr into public evidence.
        print("Claude CLI failed with exit " + str(result.returncode), file=sys.stderr)
        return 1
    envelope = json.loads(result.stdout)
    if envelope.get("is_error") or envelope.get("subtype") != "success":
        print("Claude CLI did not report a successful response", file=sys.stderr)
        return 1
    response = envelope.get("result")
    if not isinstance(response, str) or not response.strip():
        raise ValueError("Missing textual model result")
    metadata = {"provider": "Claude CLI", "model_usage": envelope.get("modelUsage", {}),
                "cost_usd": envelope.get("total_cost_usd"), "duration_ms": envelope.get("duration_ms"),
                "tools_enabled": False, "mode": "text-only-no-side-effects"}
    print(json.dumps({"response": response, "metadata": metadata}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
