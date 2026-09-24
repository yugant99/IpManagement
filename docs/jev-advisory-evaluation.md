# Jev advisory evaluation record

**Date:** 2026-09-23. **Scope:** a small, synthetic advisory pilot, separate from IPAM product source. No IPAM product files, live trial, customer records, workbook contents, existing databases or credentials were sent. Jev's typed results below are advisory, not acceptance evidence.

## Setup and actual requests

The reusable local harness is outside this repository at `~/.codex/ipam-jev-eval-20260923/evaluate.mjs`, with `ai@7.0.112` and `@ai-sdk/gateway` installed there. It reads the authorized Gateway key directly from a mode-0600 protected local file into process memory; the key is not embedded in source, command arguments, logs, Git or browser state. The harness keeps its raw sanitized-result record in its mode-0600 local directory. The input cases are four short synthetic/public summaries: simulated ServiceNow label, ambiguous tenant boundary, unproved 50-million-active scale claim, and ticket-versus-provisioning distinction. Typed questions request evidence class, unresolved business decision, ordinal impact and a conditional executor route. The script stops on the first service error to bound use.

Vercel's current [Jev model page](https://vercel.com/ai-gateway/models/jev) identifies `typesafe-ai/jev` as a typed evaluator. Its [AI SDK guide](https://vercel.com/kb/guide/typesafe-jev-and-ai-sdk) requires `ai >= 7.0.105` for `experimental_evaluate`, supports choice/score/boolean questions, and says OpenAI-compatible chat endpoints do not support Jev evaluation. [Gateway authentication](https://vercel.com/docs/ai-gateway/authentication-and-byok) supports `AI_GATEWAY_API_KEY` locally. The harness uses `gateway.evaluationModel('typesafe-ai/jev')` with `experimental_evaluate`.

| Observation | Actual result |
|---|---|
| Gateway authentication check | Authenticated `GET /v1/models` returned HTTP **200**. This confirms the key reaches the Gateway; it does not imply inference entitlement. |
| First typed evaluation, `simulated_ticket_label` | HTTP **403**, surfaced by AI SDK as `GatewayInternalServerError` after **461 ms**; one diagnostic retry returned the same HTTP **403** after **566 ms**. Gateway message: “AI Gateway requires a valid credit card on file to service requests.” |
| Remaining three bounded cases | **Not sent** after the first failure. |
| Typed choices/scores/probabilities, usage, model quality | **None returned; unavailable.** No Jev recommendation or agreement statistic exists. |

The [Gateway pricing page](https://vercel.com/docs/ai-gateway/pricing) describes free credits, but this account's actual response requires a valid card before serving requests. No card was added, credit purchased or reset consumed. A card/account decision belongs to the user; this lane cannot clear it. If access changes, run only the same bounded synthetic pilot, inspect the typed distributions and compare against the human rubric before any routing automation. Jev's confidence would remain a judgment about supplied state, not proof of IPAM behavior.

**Follow-up, 2026-09-23:** after the user reported adding card information, the original protected key still returned the same 403. A newly supplied credential was then placed in the protected local key file without echo and used for one bounded retry. AI Gateway returned **401 `GatewayAuthenticationError`: invalid API key or token**, after 379 ms; no typed answer or usage was returned, and the remaining cases were not sent. The unusable local copy was removed afterward. Vercel's [authentication guide](https://vercel.com/docs/ai-gateway/authentication-and-byok) directs local users to create a key under **AI Gateway → API Keys**. This follow-up does not establish that the card update failed: the new attempt failed at authentication before billing entitlement could be assessed.

## Successful bounded evaluation

After the user supplied an AI Gateway API key, the same harness completed its four synthetic cases with `typesafe-ai/jev`; no further cases or model routes were called. The four requests took **4,504 / 769 / 1,352 / 302 ms** respectively. Reported usage totals were **3,518 input + 608 output = 4,126 tokens**. The SDK returned no monetary charge. The case state and typed-question definitions remain in the local harness; no key is in this repository.

`evidence` is a choice distribution; `needs_business_decision` is a Boolean probability; `inherent_impact` is a zero-based score distribution whose displayed mean below is **score + 1** on the packet's 1–5 rubric. That mean is not an ordinal category or a measured security risk. `executor` is a conditional choice from only the supplied allowed routes.

| Synthetic case | Jev typed result | Sol adjudication |
|---|---|---|
| RFP-042 simulated ticket label | `evidence=local_only` **0.99**; business-decision probability **0.74**; impact mean **1.27**; `executor=defer` **1.00** | Evidence classification and deferral agree. The **1.27** impact undercalls a future external ticket write under the packet rubric (**3**); do not use this score for prioritization. Current local simulator remains local only. |
| RFP-008 tenant boundary | `evidence=local_only` **0.93**; business-decision probability **0.92**; impact mean **3.61**; `executor=defer` **1.00** | Business decision and missing independent-customer isolation agree. A cross-customer authorization failure is rubric **5** when that boundary is selected; Jev's mean does not replace it. |
| RFP-093 scale claim | `evidence=local_only` **0.99**; business-decision probability **0.70**; impact mean **2.02**; `executor=defer` **1.00** | The evidence label is correct: the >50-million-active-IPv4 requirement has no qualifying workload proof. The integration security-impact rubric is a poor fit for a performance claim; ignore this impact score. |
| RFP-098 ticket is not provisioning | `evidence=local_only` **0.96**; business-decision probability **0.72**; impact mean **4.00**; `executor=defer` **1.00** | A hypothetical external ticket cannot prove subscriber identity, allocation or provisioning. Actual subscriber-facing writes are rubric **5**; the case also mixes a false claim with a future operation, so the impact mean is not actionable. |

Jev's returned choice confidence was **0.90–0.98** for evidence and **1.00** for `defer`; score confidence was **0.15–0.78**. These values describe answer concentration for the supplied synthetic prompts, not calibration or truth. Four cases are too few to automate routing, and the impact disagreements require revised atomic questions and a larger human-labeled sample before using scores. Sol's source/evidence judgments above remain separate from Jev's actual outputs. The [requirements packet](next-phase-integration-requirements.md) gives the controlling rows and acceptance gates.

## Economical executor evidence and limits

`opencode v2.0.14` listed exact IDs `opencode-go/muse-spark-1.3-contributor` and `opencode-go/deepseek-v4.1-flash`. A single `opencode run --standalone --model opencode-go/muse-spark-1.3-contributor#xhigh --format json` synthetic text-only probe, run from an empty local directory, returned exactly `ROUTE_OK` in **4.52 s**. It used no IPAM files and no tool action. That establishes one working Muse xhigh request at this time; it is not a current quota balance, long-task availability or quality benchmark. DeepSeek V4.1 Flash was **listed but not probed in this lane**; [the prior lead handoff](handoffs/main-lead-6.0.md) records a dated `#high` preflight, which does not verify present access or `#xhigh` support. Do not silently change versions or variants. The probe JSON did not supply token usage or monetary charge.

OpenCode's [current Go documentation](https://dev.opencode.ai/docs/go/) lists Muse Spark 1.3 Contributor at **$0.10 input / $0.20 output per million tokens**, with a **$60 monthly model limit**; it lists DeepSeek V4.1 Flash at **$0.15/$0.60 off-peak** and **$0.30/$1.20 peak**, with a temporary **$60 monthly limit through September 27, 2026**. The same page says each model's 5-hour limit is 20% of its monthly limit, weekly 50%, and that limits can change. These are published rates/limits, not this account's remaining quota. Contributor allows prompts/completions to train future Meta models and is not zero-retention; DeepSeek V4.1 Flash is listed as not used for model training with a time-limited zero-retention agreement. Refresh both before dispatch. Only allowlisted tracked public/synthetic relative paths may reach Contributor. Never provide private workbook, untracked outputs, customer data, credentials, databases or private chat history to either route.

No excluded model was invoked. Muse xhigh remains the preferred later executor only after the user chooses a bounded product slice and the lead assigns it; DeepSeek V4.1 Flash remains a conditional fallback. Jev would evaluate minimized supplied candidate facts, not discover model entitlement, price, privacy policy or available quota independently.

## Bounded communication protocol

1. Sol/proposer writes one short requirement, candidate contract and evidence packet with exact RFP rows and allowed synthetic/public inputs.
2. Jev, only when entitlement works, returns typed advisory labels/scores and a route from the supplied allowed candidates. Code enforces exclusions, data policy and available quota independently.
3. A reasoning reviewer challenges source facts and failed gates. Proposer and reviewer may reconcile **once** in a recorded decision row.
4. Main Lead 6.0 accepts or rejects the technical proposal; Pooyan/user decides unresolved business scope. No model grants external writes, merge, status promotion or business approval.

This bounded Jev check is complete. Further calls require a concrete review question and the same sanitized-input boundary; no continuous model router or alternate provider is authorized. The earlier 403/401 attempts remain recorded as historical access failures, not results from the successful key.
