import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SKILLS = {
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


if __name__ == "__main__":
    unittest.main()
