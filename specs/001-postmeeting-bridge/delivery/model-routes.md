# Active model routes —2026-09-22

The user suggested the simpler native Codex route for Terra after interactive OpenCode
inspection; the lead explicitly selected it. This does not change the Astra lead model.

| Role | Selected exact route | Observed state |
|---|---|---|
| Main Lead4 | Codex gpt-6-astra | Active lead |
| Terra implementation | Codex gpt-5.6-terra, high | Actual native worker /root/terra_schema; T003 source preparation complete |
| Grok4.7 integration | opencode-go/grok-4.7#high | Actual T002 source review invoked |
| Grok4.6 scout | opencode-go/grok-4.6#medium | Actual T002 completed; session ses_f350eb239ffeK1SvUzC4X8fQlY |
| DeepSeek backend/UI | opencode-go/deepseek-v4.1-flash#high | Listed by active service; not yet invoked |
| Luna independent QA | opencode-go/gpt-5.6-luna#medium | Listed by active service; prerequisite held, not invoked |
| Sol escalation | Codex gpt-5.6-sol | Native route available; user-approved escalation, not invoked |
| Fable advisory | Claude Code claude-fable-5-1[1m], high | One actual FABLE-DESIGN response completed through existing Max |

OpenCode /opt/homebrew/bin/opencode v2.0.14; Claude Code v2.1.278. Safe active-service
metadata showed37 models, providers opencode/opencode-go, one Go connection and zero
OpenAI connections. Interactive CLI /models was also inspected: terra gave no results;
gpt showed GPT-5.6 Luna — OpenCode Go. No OpenCode Terra route was available. Cached
OpenAI catalog entries did not establish a working connection. No ChatGPT auth was changed.

The existing Go connection served T002 successfully; no newly supplied key was needed,
installed or copied to commands/logs/repository. Pin exact routes; do not use the service
or UI default. No OpenRouter connection was configured or inferred from an OpenCode key.

Existing-account use is user-directed. No purchase, top-up, extra-usage activation, model
fallback or cloud spend is permitted. Stop on quota/payment requirements. Catalog/list
cost telemetry is not an actual billing receipt; remaining account allowance is unknown.

Fable is not repeatedly invoked autonomously. Provide the user an exact-candidate prompt
before substantial further advice and continue independent work. Fable has no acceptance
authority and is not an implementation dependency. Supplemental Astra preflight advisers
are accurately labeled source advisers, not impersonated requested-model executions.
