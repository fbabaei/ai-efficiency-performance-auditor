# Copilot + Scout Workflow

## 1) Objective
Use GitHub Copilot for implementation speed, and Microsoft Scout for orchestration, M365 actions, and operational reporting.

---

## 2) Tool split (who does what)

### GitHub Copilot (VS Code/Codespaces)
- Write/refactor code
- Generate tests
- Explain code inline
- Suggest fixes during development

### Scout
- Calendar/email/Teams tasks
- Progress/status reports
- Cross-tool orchestration
- Scheduled automations
- Summaries grounded in retrieved artifacts

---

## 3) Working agreement

- Preserve existing architecture and coding conventions.
- Prefer minimal, safe changes over broad rewrites.
- Never invent facts; cite source artifacts (code, logs, calendar, mail).
- For outbound communication, keep sensitive details private.
- "Done" means: requested output delivered, no unresolved blockers.

---

## 4) Standard task flow

1. **Plan**
   - Define scope, files, constraints, acceptance criteria.
2. **Implement (Copilot)**
   - Apply focused code changes.
3. **Validate**
   - Run targeted checks/tests.
4. **Orchestrate (Scout)**
   - Send summaries, notify stakeholders, update task trackers.
5. **Close**
   - Provide concise final status + next required action (if any).

---

## 5) Prompt templates

### A) Copilot coding prompt
Task: \<feature/fix\>  
Scope: \<files/modules\>  
Constraints: \<performance/security/style\>  
Acceptance criteria:
- \<criterion 1\>
- \<criterion 2\>

### B) Scout orchestration prompt
Context: \<what changed\>  
Audience: \<who needs update\>  
Output needed: \<email/teams/report\>  
Rules:
- Use only verified artifacts
- Keep message concise
- Include risks/blockers and owner

### C) Daily status prompt
Summarize today's progress from:
- commits/PRs
- test/build output
- open blockers

Format:
- Completed
- In progress
- Risks
- Next action

---

## 6) Suggested weekly cadence

- **Daily**: coding + validation + short stakeholder update
- **Weekly**: architecture/risk review, backlog cleanup, automation tuning
- **Monthly**: workflow retro (what to automate next)

---

## 7) Optional extensions

- Add MCP tools for internal APIs/dashboards
- Add scheduled Scout automations for recurring reports
- Add PR checklist enforcing acceptance criteria

---

## 8) Example workflow in this repo

See `docs/WORKFLOW-COPILOT-SCOUT-EXAMPLE.md` for a filled end-to-end example (task definition, Copilot prompt, Scout prompt, and done checklist).

For Scout-led audit execution and outbound delivery (email + Teams), see:
`docs/SCOUT-AUDIT-DELIVERY-WORKFLOW.md`.
