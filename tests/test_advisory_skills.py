import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SKILLS = {
    "measurement-readiness": (
        "absence of telemetry does not prove a defect",
        "Span status is not task success",
        "Never recommend logging raw prompts",
        "Do not hash sensitive payloads",
        "propose thresholds for approval, not as requirements",
        "Cost per successful task includes costs of failed requests",
        "the auditor never runs it",
    ),
    "efficiency-budget-review": (
        "Missing approval means proposed thresholds, not accepted requirements",
        "Missing policy or input prevents independent confirmation",
        "user attestations, not a causal experiment",
        "Budget violations are observations, not proof of safely avoidable work",
        "Passing budgets is not finding resolution",
        "No CI configuration, policy edits, JSON files or gate execution",
    ),
    "change-impact-review": (
        "A PR URL or revision label alone is not review evidence",
        "Do not fetch a PR, run Git, check out revisions",
        "Do not apply the diff",
        "Reject outside-workspace, traversal and ambiguous diff paths",
        "a deleted-line number is not a candidate-source location",
        "A diff hunk is supplied evidence, not independently verified source",
        "Candidate-only defects have introduction unknown",
        "Do not call an existing mechanism a new regression",
        "No finding means no demonstrated regression in inspected scope",
        "not proof that the PR is safe or the application is efficient",
        "Incomplete hunks or missing dependencies mean partial coverage",
        "Fewer calls alone do not prove improved quality",
        "Do not load other skills unless the user explicitly requests their modes",
        "one shared budget and one report pair",
    ),
    "recommendation-planning": (
        "do not discover an application, inspect source, or open referenced traces",
        "From supplied report; not reverified",
        "Not provided in supplied report",
        "unknown prerequisites block implementation readiness",
        "Unproven changes remain unranked",
        "effort is a separate scheduling aid",
        "proposals requiring approval, not approved thresholds",
        "Never label work implemented, resolved or validated from a plan alone",
        "Do not load other skills unless the user explicitly requests their modes",
        "share one budget and one report pair",
        "not stable across audits",
        "Do not create task files, patches, JSON, extra per-card reports or tickets",
    ),
    "audit-comparison": (
        "two separate profiles with no improvement verdict or causal delta",
        "A zero baseline yields N/A percentage",
        "missing values yield unknown delta/percentage, not zero",
        "absence from the candidate report is not proof",
        "Static source comparisons yield conditional bounds, not measured savings",
        "one comparison report pair",
        "overall improvement inconclusive",
    ),
    "context-retrieval-review": (
        "Characters/bytes are not tokens",
        "Selected-but-unconsumed",
        "Same document ID across versions",
        "A document absent from the final answer was never used",
        "same content/version",
        "Token-only recommendations have zero call reduction only when demonstrated",
        "no quality-preservation or improvement claim without comparative evidence",
    ),
    "orchestration-efficiency-review": (
        "Attempts / initiated logical operations at one named layer",
        "Product of total-attempt limits only on a proven nested branch",
        "half-open intervals [start,end)",
        "Valid usable hits / eligible lookups",
        "Missing ancestry means bounds/unknown",
        "necessary cleanup or durable jobs are not automatically waste",
        "failure/timeout alone does not mean the write did not happen",
    ),
}


class AdvisorySkillTests(unittest.TestCase):
    def test_explicit_opt_in_frontmatter_and_core_routing(self) -> None:
        agent = (ROOT / ".github" / "agents" / "ai-efficiency-performance-auditor.agent.md").read_text(
            encoding="utf-8"
        )
        for name in SKILLS:
            path = ROOT / ".github" / "skills" / name / "SKILL.md"
            text = path.read_text(encoding="utf-8")
            with self.subTest(skill=name):
                self.assertTrue(text.startswith("---\n"))
                header, _ = text[4:].split("\n---\n", 1)
                self.assertIn(f"name: {name}", header.splitlines())
                self.assertIn("disable-model-invocation: true", header.splitlines())
                description = next(
                    line.removeprefix("description: ") for line in header.splitlines()
                    if line.startswith("description: ")
                )
                self.assertIn("explicitly asked", json.loads(description))
                self.assertLessEqual(len(json.loads(description)), 1024)
                self.assertLessEqual(len(text.splitlines()), 130)
                self.assertIn(f"`{name}`", agent)
                self.assertNotIn("tools:", header)
                self.assertNotIn("scripts/", text)

    def test_skills_preserve_permissions_and_evidence_budgets(self) -> None:
        for name in SKILLS:
            body = " ".join(
                (ROOT / ".github" / "skills" / name / "SKILL.md")
                .read_text(encoding="utf-8").split()
            )
            for requirement in (
                "read-only", "Do not execute commands", "invoke other agents",
                "call external services", "only write exception",
                "sanitization gates", "per-file budgets", "no-overwrite",
                ".github/agents/ai-efficiency-performance-auditor.agent.md",
            ):
                with self.subTest(skill=name, requirement=requirement):
                    self.assertIn(requirement, body)

    def test_extension_behavior_and_false_positive_guards_are_declared(self) -> None:
        for name, requirements in SKILLS.items():
            body = " ".join(
                (ROOT / ".github" / "skills" / name / "SKILL.md")
                .read_text(encoding="utf-8").split()
            )
            for requirement in requirements:
                with self.subTest(skill=name, requirement=requirement):
                    self.assertIn(requirement.lower(), body.lower())

    def test_comparison_contract_has_private_entities_and_sanitized_graph_rules(self) -> None:
        reference = ROOT / ".github" / "skills" / "audit-comparison" / "references" / "comparison-contract.md"
        body = " ".join(reference.read_text(encoding="utf-8").split())
        for requirement in (
            "advisory-evidence/1", "advisory-markdown/1", "not a public JSON schema",
            "Audit/scenario", "Logical operation", "Attempt", "Downstream request",
            "Usage", "Consumption", "Finding", "lower bounds or unknowns",
            "baseline operation once", "metric-specific", "Zero baseline: N/A",
            "unknown topology", "never the Executive Summary", "Do not invoke renderers",
        ):
            with self.subTest(requirement=requirement):
                self.assertIn(requirement.lower(), body.lower())

    def test_modes_report_consistent_contract_versions(self) -> None:
        agent = (ROOT / ".github" / "agents" / "ai-efficiency-performance-auditor.agent.md").read_text(
            encoding="utf-8"
        )
        reference = (
            ROOT / ".github" / "skills" / "audit-comparison" / "references" / "comparison-contract.md"
        ).read_text(encoding="utf-8")
        for contract in ("advisory-evidence/1", "advisory-markdown/1"):
            self.assertIn(contract, agent)
            self.assertIn(contract, reference)
            for name in ("context-retrieval-review", "orchestration-efficiency-review"):
                with self.subTest(contract=contract, skill=name):
                    self.assertIn(
                        contract,
                        (ROOT / ".github" / "skills" / name / "SKILL.md").read_text(
                            encoding="utf-8"
                        ),
                    )

    def test_service_deadlines_preserve_independent_work(self) -> None:
        body = (
            ROOT / ".github" / "skills" / "service-performance-review" / "SKILL.md"
        ).read_text(encoding="utf-8")
        for requirement in (
            "Deadlines and cancellation", "remaining retry/backoff budget",
            "accepted durable jobs", "independently consumed results",
            "Missing timestamps/correlation",
        ):
            with self.subTest(requirement=requirement):
                self.assertIn(requirement, body)

    def test_finding_verification_requires_candidate_and_quality_evidence(self) -> None:
        body = " ".join(
            (ROOT / ".github" / "skills" / "audit-comparison" / "references" / "finding-verification.md")
            .read_text(encoding="utf-8").split()
        )
        for requirement in (
            "verified-fixed", "partially-addressed", "persistent", "regressed", "inconclusive",
            "Unknowns take precedence over verified-fixed",
            "a recommendation card or code deletion alone never proves resolution",
            "Supplied reports support attributed status only",
            "Proposed acceptance margins are not approved thresholds",
            "do not rewrite historical report/checker schemas",
        ):
            with self.subTest(requirement=requirement):
                self.assertIn(requirement, body)


if __name__ == "__main__":
    unittest.main()
