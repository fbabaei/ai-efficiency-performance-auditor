# Scout-Assisted Audit and Delivery Workflow

Use this workflow when you want Scout to run an AI efficiency/performance audit and deliver a stakeholder-ready report by email and Teams.

## 1) Define the audit request

Provide:

- target repository path
- focus areas (for example: latency, token/tool-call efficiency, retries)
- output format preference (for example: prose/“format words”)
- delivery recipients (email and Teams)

Example prompt:

```text
Audit /workspace/retrieval-gateway; focus on latency, token/tool-call efficiency, retries; send report to fbabaei@microsoft.com and teams; format words.
```

## 2) Scout execution pattern

Scout should:

1. Read key runtime and orchestration files first (entrypoint, routing, orchestrator, retries, adapter/runtime config, relevant tests).
2. Ground findings in code evidence only (no invented behavior, no assumed measurements).
3. Produce a concise, prioritized report:
   - executive summary
   - findings and impact
   - recommendations (high/medium priority)
   - validation plan
4. Send the report by email to the requested recipient(s).
5. Send a short Teams completion notification.

## 3) Report structure (recommended)

Use this order:

1. Scope and method
2. Executive summary
3. What is working well
4. Findings and impact
5. Prioritized recommendations
6. Suggested validation plan

## 4) Guardrails

- Keep all claims tied to retrieved code/artifacts.
- Do not describe the work as “attended” activity unless actual attendance occurred.
- Avoid sharing private/sensitive context to anyone beyond the requested recipients.
- If delivery fails (auth/network), report failure status explicitly.

## 5) Reusable delivery template

Email subject template:

```text
<App/Repo> audit report - <focus areas> (<date>)
```

Teams notification template:

```text
<App/Repo> audit completed (<focus areas>). Full report emailed to <recipient>.
```

