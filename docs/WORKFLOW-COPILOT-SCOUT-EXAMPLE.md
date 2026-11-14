# Copilot + Scout Workflow Example (ai-efficiency-performance-auditor)

## 1) Filled task definition

**Task:** Improve audit summary clarity without changing audit logic  
**Scope:**
- `IDA-TOOL-CALL-PATH-AUDIT.md`
- `WORKFLOW-COPILOT-SCOUT.md` (reference only)

**Constraints:**
- No code changes
- Keep claims evidence-based
- Keep wording concise and executive-friendly

**Acceptance criteria:**
1. Add a plain-language summary section near the top.
2. Keep technical findings intact.
3. Add no unsupported performance claims.

---

## 2) Copilot prompt (implementation)

```text
Update IDA-TOOL-CALL-PATH-AUDIT.md to add a short plain-language summary near the top for exec readers.
Constraints:
- Documentation-only change
- Keep all existing technical sections and references intact
- Do not introduce new unverified claims
Acceptance:
- New section explains what is proven, what is unproven, and recommended next step
```

---

## 3) Scout prompt (orchestration/status)

```text
Create a stakeholder-ready status update for this documentation change.
Include:
- What changed
- Why it matters
- Risks/limitations
- Next step
Keep it brief and grounded only in the updated file content.
```

---

## 4) Done checklist

- [ ] Plain-language section added
- [ ] No technical content removed
- [ ] No speculative claims introduced
- [ ] Stakeholder summary produced

---

## 5) Reuse pattern for future tasks

1. Copy this file section-by-section for a new task.
2. Replace task/scope/constraints/criteria with the new request.
3. For Scout-led audits, you can provide either a local repo path or a GitHub repo URL (Scout resolves URL inputs by cloning locally first).
4. Keep the same separation of responsibilities:
   - Copilot for implementation.
   - Scout for orchestration and communications.
