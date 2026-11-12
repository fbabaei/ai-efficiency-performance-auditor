# Finding-level optimization verification

Load only for an explicitly requested finding-verification task within
audit-comparison. It extends comparison, not tools, budgets or application scope.
Retain the comparison contract's matched inputs, safety inventory, measurement
rules and report-only provenance. Do not execute evaluation or load other modes.

## Identity and evidence

Use `Finding ID | Scenario and mechanism | Baseline evidence | Candidate
evidence | Preserved contract | Quality/safety result | Status | Remaining gap`.
Preserve supplied IDs. IDs or similar prose alone do not prove the same
mechanism; match affected operations, scope, versions and consumers.
New IDs are audit-local, not a persistent issue database.

Verification needs both-side evidence and declared inspection coverage for
every affected site. Missing candidate findings, fewer inspected files, a
recommendation card or code deletion alone never proves resolution.
Supplied reports support attributed status only, not independent verification.
Trace-only evidence cannot establish source changes without mapping.

## Status decision

- **verified-fixed:** direct candidate evidence removes the full demonstrated
  mechanism at all relevant sites, preserves applicable contracts, and supplied
  matched evaluation satisfies approved quality/safety criteria. State whether
  runtime efficiency benefits are measured or remain conditional.
- **partially-addressed:** evidence establishes removal/reduction at some sites
  but a supported part remains. Cite both and retain remaining impact; no full
  resolution or overlapping partial/complete savings.
- **persistent:** the same demonstrated mechanism remains under comparable
  scope; no evidence-backed removal is established.
- **regressed:** matched evidence shows amplified avoidable work, or an approved
  quality/safety criterion fails after the candidate change. State which
  dimension regressed; do not infer causal attribution from confounded inputs.
- **inconclusive:** identity, candidate coverage, preserved contracts, matching
  conditions or evaluation criteria/results are missing or conflicting.

Unknowns take precedence over verified-fixed. A cheaper candidate that fails
quality is not fixed. Proposed acceptance margins are not approved thresholds.
Report source mechanism status separately from measured benefit: a static
correction may be demonstrated while overall verification remains inconclusive.
Use core sampling minima and uncertainty rules; passing point thresholds alone
does not establish statistical non-inferiority.

## Reporting

Put the status table beside comparison findings, with both-side citations and
remaining gaps in Validation plan. Map verified-fixed to the existing comparison
label resolved-with-evidence only when all required evidence is satisfied.
Retain new/persistent/not-verifiable for ordinary comparison; the expanded
statuses do not rewrite historical report/checker schemas.
One comparison still produces one report pair, not per-finding artifacts.
