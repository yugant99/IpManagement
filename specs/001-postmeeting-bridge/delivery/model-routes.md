# CLI model routes — 2026-09-22

User-selected routing: Astra control plane in Codex; Terra, Grok 4.7/4.6, DeepSeek V4.1
Flash and Luna in OpenCode; Sol escalation in Codex; Fable advisory in Claude Code CLI.
The later user clarification supersedes any blanket inference that Fable/Sol need OpenCode.

| Role | Exact selected route | Observed status |
|---|---|---|
| Main Lead 4.0 | Codex GPT-6 Astra, current task | Active control plane |
| Terra implementation sublead | Intended OpenCode openai/gpt-5.6-terra | Catalog ID confirmed, active service lacks OpenAI connection; dispatch held |
| Grok 4.7 contracts | opencode-go/grok-4.7#high | Active repo-scoped model list; inference not probed |
| Grok 4.6 scout | opencode-go/grok-4.6#medium | Active repo-scoped model list; inference not probed |
| DeepSeek backend/UI | opencode-go/deepseek-v4.1-flash#high | Active repo-scoped model list; inference not probed |
| Luna independent QA | opencode-go/gpt-5.6-luna#medium | Active repo-scoped model list; inference not probed |
| Sol escalation | Codex gpt-5.6-sol | Available in this task's native model-routing metadata; user explicitly selects Codex |
| Fable advisory | Claude Code claude-fable-5-1[1m], high | CLI configured, authenticated through existing Claude Max; no inference probe |

OpenCode executable `/opt/homebrew/bin/opencode`, version 2.0.14. Claude executable
`/Users/yuganthareshsoni/.local/bin/claude`, version 2.1.278. Safe local reads: `opencode
models`, CLI help, repo-scoped `/api/model`, `/api/provider`, `/api/integration`; Claude
settings model only and `claude auth status --json` sanitized to login/auth/provider/plan.
No credential values/account identifiers copied into evidence. Only metadata is retained.

The active OpenCode service reports 37 models, providers opencode and opencode-go, one Go
credential connection and zero OpenAI connections. The OpenAI integration supports
ChatGPT Pro/Plus methods chatgpt-browser and chatgpt-headless, but neither is connected.
This is an active service observation beyond the cached catalog. The user expects Terra
in OpenCode; retain that conflict rather than silently replacing it. Resolution is to use
an existing authorized OpenCode ChatGPT connection once established, or obtain explicit
approval to route the same Terra model through Codex. No model/account change was made.

Explicitly pin provider/model and reasoning variant on every dispatch. Service default
is opencode/mimo-v2.6-flash-free; recent UI selection is Grok 4.7. Neither is an acceptable
implicit Terra substitute. Existing-account use is user-directed; no top-up, subscription
purchase, extra-usage activation or cloud charge is allowed. Allowance/overage state is
not established by catalog token-cost fields; stop on quota/payment requirements.

Inference latency, runtime success and remaining allowance are unverified. No unnecessary
paid probe ran. The supplementary Astra preflight advisers were local Codex source
reviewers, not impersonated executions of the requested Grok/Luna/Fable workers.
