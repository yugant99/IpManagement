# Active model routes —2026-09-22

## Latest user-directed replacements

The user now explicitly assigns **GPT-6 Luna** to all work previously assigned to Terra,
and **GPT-6 Sol** to the Grok4.7 review role and difficult implementation escalations.
Native routes are `gpt-6-luna` and `gpt-6-sol`; Astra remains lead. Completed runs below
retain their actual original model identities. These changes do not turn prior source
review into runtime evidence. Independent QA remains a separate worker and gate from
the Luna implementation lane.

The attempted T004 review on `opencode-go/grok-4.7#high` stopped with
`provider.quota`, HTTP429, `Go usage limit exceeded`, before returning source findings
(session `ses_f34ea7951ffeaWltEiAHeydGdI`). No more Go calls are dispatched while that
account limit is unresolved; no purchase, extra-usage activation or new credential is
used. GPT-6 Sol replaces this review and any blocked leaf that needs escalation.

## Earlier route history


After interactive inspection and a routing correction, the user explicitly accepts native
Codex Terra. An equally or more capable OpenCode fallback is authorized for actual limits
or subpar performance; the lead records the evidence and exact route before replacement. This does not change the Astra lead model.

| Role | Selected exact route | Observed state |
|---|---|---|
| Main Lead4 | Codex gpt-6-astra | Active lead |
| Terra implementation | Codex gpt-5.6-terra, high | Actual native worker /root/terra_schema; T003 implementation resumed |
| Grok4.7 integration | opencode-go/grok-4.7#high | Actual T002 source review invoked |
| Grok4.6 scout | opencode-go/grok-4.6#medium | T002 authored; correction run stopped on Go quota429, no edits |
| DeepSeek backend/UI | opencode-go/deepseek-v4.1-flash#high | Listed by active service; not yet invoked |
| Luna independent QA | opencode-go/gpt-5.6-luna#medium | Actual T003 supplemental source review completed; T007/T025 remain held |
| Sol escalation | Codex gpt-5.6-sol | Actual Sol fallback /root/sol_t002_fix replacing stopped Grok4.6 for bounded T002 corrections |
| Fable advisory | Claude Code claude-fable-5-1[1m], high | One actual FABLE-DESIGN response completed through existing Max |

OpenCode /opt/homebrew/bin/opencode v2.0.14; Claude Code v2.1.278. Safe active-service
metadata showed37 models, providers opencode/opencode-go, one Go connection and zero
OpenAI connections. Interactive CLI /models was also inspected: terra gave no results;
gpt showed GPT-5.6 Luna — OpenCode Go. No OpenCode Terra route was available. Cached
OpenAI catalog entries did not establish a working connection. An OpenCode ChatGPT login was started then canceled before authorization completed; no new connection was established.

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

Official Go list inspected2026-09-22: https://opencode.ai/docs/go/ includes GPT5.6 Luna, Grok4.7/4.6 and DeepSeekV4.1 Flash, but no Terra. This corroborates the active CLI menu, not a model-quality comparison.

First quota event: Grok4.6 correction run returned provider.quota /429 /Go usage limit exceeded. It was stopped; Sol takes the exact bounded correction lease. No new Go credential or balance fallback was installed or activated.
