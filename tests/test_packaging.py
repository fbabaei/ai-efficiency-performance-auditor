import json
from pathlib import Path
import re
import unittest
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[1]


class PackagingTests(unittest.TestCase):
    def test_agent_directory_contains_only_the_definition(self) -> None:
        directory = ROOT / ".github" / "agents"
        self.assertEqual(
            sorted(path.name for path in directory.iterdir()),
            ["ai-efficiency-performance-auditor.agent.md"],
        )
        agent = (directory / "ai-efficiency-performance-auditor.agent.md").read_text(encoding="utf-8")
        self.assertTrue(agent.startswith("---\n"))
        header, body = agent[4:].split("\n---\n", 1)
        self.assertIn("name: AI Efficiency & Performance Auditor", header.splitlines())
        self.assertIn(
            "tools: [read, search, edit, ask_user, appmod-preview-markdown]",
            header.splitlines(),
        )
        self.assertIn("agents: []", header.splitlines())
        self.assertIn("user-invocable: true", header.splitlines())
        self.assertIn("disable-model-invocation: true", header.splitlines())
        self.assertNotRegex(header, r"(?m)^target:")
        self.assertLessEqual(len(body), 29_000)
        self.assertLessEqual(len(agent.replace("\n", "\r\n")), 30_000)
        self.assertRegex(header, r"(?m)^description: \".+\"$")
        expected = (ROOT / "evaluations" / "expected.json").read_text(encoding="utf-8")
        version = json.loads(expected)["methodology_version"]
        self.assertIn(f"Audit methodology version: {version}.", body)
        self.assertIn(
            f"## {version} - Unreleased",
            (ROOT / "CHANGELOG.md").read_text(encoding="utf-8"),
        )
        self.assertIn(
            f"Candidate methodology version: **{version}**",
            (ROOT / "README.md").read_text(encoding="utf-8"),
        )
        for path in (ROOT / ".github" / "prompts").glob("*.prompt.md"):
            with self.subTest(prompt=path.name):
                self.assertIn(
                    f"methodology {version}.", path.read_text(encoding="utf-8"),
                )

    def test_executive_summary_contract_is_declared(self) -> None:
        agent = (ROOT / ".github" / "agents" / "ai-efficiency-performance-auditor.agent.md").read_text(
            encoding="utf-8"
        )
        agent = " ".join(agent.split())
        for requirement in (
            "at most 60 lines and 600 words",
            "Priority | Weak area | Code location | Recommended improvement | Expected benefit | Evidence",
            "do not replace the detailed six-section report",
            "without conducting a new audit",
            "do not add overlapping savings",
            'use "Executive Summary" in the title',
            "reports/<application>-audit-executive-summary.md",
            "never overwrite it",
            "must be a new `.md` file",
            "Never write in source, configuration, trace, or agent/skill discovery directories",
            "Check both length limits before saving",
            "Verify the saved file using a read tool",
            "If read-back fails",
            "Open the Executive Summary in Markdown preview?",
            "Only an explicit Yes authorizes",
            "Ask again for each newly created report",
            "file was not saved",
            "preview consent was not obtained",
            "Markdown: Open Preview",
            "Report permission, save, read-back, and preview errors explicitly",
        ):
            with self.subTest(requirement=requirement):
                self.assertIn(requirement, agent)

    def test_code_location_contract_is_declared(self) -> None:
        agent = (ROOT / ".github" / "agents" / "ai-efficiency-performance-auditor.agent.md").read_text(
            encoding="utf-8"
        )
        agent = " ".join(agent.split())
        for requirement in (
            "smallest verified file-and-line range",
            "include each relevant location",
            "Cite repeated-call statements separately from return statements",
            "Keep verified file-and-line notation visible",
            "not only in link targets or reference definitions",
            "show each affected path and range directly alongside its symbol",
            "tie the recommended improvement to it",
            "omit secrets or sensitive values",
            "Do not copy code into the Executive Summary",
            "A trace record alone is not a verified code location",
            "Code location not verified",
            "From supplied report; not reverified",
            "Not provided in supplied report",
            "without inspecting the codebase or guessing paths, symbols, or line numbers",
            "Include both sites for redundancy spanning multiple locations",
        ):
            with self.subTest(requirement=requirement):
                self.assertIn(requirement, agent)

    def test_detailed_report_persistence_contract_is_declared(self) -> None:
        agent = (ROOT / ".github" / "agents" / "ai-efficiency-performance-auditor.agent.md").read_text(
            encoding="utf-8"
        )
        agent = " ".join(agent.split())
        for requirement in (
            "reports/<application>-audit-detailed-report.md",
            "Save the detailed report first",
            "all six required sections and their evidence citations",
            "limits apply only to the Executive Summary, not the detailed report",
            "Provide clickable links to both verified saved reports",
            "do not generate or copy a new detailed audit",
            "identifying which report failed",
        ):
            with self.subTest(requirement=requirement):
                self.assertIn(requirement, agent)

    def test_reusable_prompts_save_both_reports(self) -> None:
        for name in ("audit-knowledge-search", "audit-agent-retries"):
            prompt = (ROOT / ".github" / "prompts" / f"{name}.prompt.md").read_text(
                encoding="utf-8"
            )
            for requirement in (
                'agent: "AI Efficiency & Performance Auditor"',
                "reports/<application>-audit-detailed-report.md",
                "reports/<application>-audit-executive-summary.md",
                "Never overwrite existing files",
                "Read both saved files back",
                "these limits do not apply to the detailed report",
                "Open the Executive Summary in Markdown preview?",
            ):
                with self.subTest(prompt=name, requirement=requirement):
                    self.assertIn(requirement, prompt)

    def test_documentation_links_resolve(self) -> None:
        paths = [ROOT / "README.md", ROOT / "CHANGELOG.md"]
        paths.extend((ROOT / "docs").glob("*.md"))
        paths.extend((ROOT / "evaluations").glob("*.md"))
        paths.extend((ROOT / ".github" / "skills").glob("**/*.md"))
        for path in paths:
            text = path.read_text(encoding="utf-8")
            for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text):
                if "://" in target or target.startswith("#"):
                    continue
                target = unquote(target.split("#", 1)[0])
                with self.subTest(source=path.name, target=target):
                    self.assertTrue((path.parent / target).exists())

    def test_service_skill_is_explicitly_opt_in_and_discoverable(self) -> None:
        path = ROOT / ".github" / "skills" / "service-performance-review" / "SKILL.md"
        text = path.read_text(encoding="utf-8")
        self.assertTrue(text.startswith("---\n"))
        header, body = text[4:].split("\n---\n", 1)
        self.assertIn(f"name: {path.parent.name}", header.splitlines())
        self.assertIn("disable-model-invocation: true", header.splitlines())
        description = next(
            line.removeprefix("description: ")
            for line in header.splitlines() if line.startswith("description: ")
        )
        self.assertIsInstance(json.loads(description), str)
        self.assertIn("explicitly asked", json.loads(description))
        normalized = " ".join(body.split())
        for requirement in (
            "Do not execute commands",
            "invoke other agents",
            "call external services",
            "only write exception",
            "sanitization gates",
            "including these skill reads",
            "Async blocking",
            "Clients and pools",
            "Concurrency",
            "Streaming",
            "Storage",
            "Resource lifecycle",
            "latency",
            "contention",
            "unknown",
            "Hypotheses stay unranked",
            "six report sections",
            "Never claim a performance improvement is validated without comparative evidence",
        ):
            with self.subTest(requirement=requirement):
                self.assertIn(requirement, normalized)
        agent = (ROOT / ".github" / "agents" / "ai-efficiency-performance-auditor.agent.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("`service-performance-review`", agent)
        self.assertIn("Do not silently broaden ordinary tool/model audits", agent)
        self.assertIn("Rank demonstrated service defects without requiring avoidable", agent)
        self.assertIn("Separate scenario-local and workload-weighted impact", normalized)
        self.assertIn("Without measured branch frequencies, rank within each scenario", normalized)

    def test_scope_and_stop_contract_is_declared(self) -> None:
        agent = " ".join(
            (ROOT / ".github" / "agents" / "ai-efficiency-performance-auditor.agent.md")
            .read_text(encoding="utf-8").split()
        )
        for requirement in (
            "If exactly one candidate application exists, audit it and state the selection basis",
            "If ask_user is absent or returns no reply",
            "'scope selection required' with no combined counts",
            "If the audit stops as 'not auditable' or 'scope selection required', do not create an Executive Summary or detailed report",
            "Report the stop reason, the search scope, and the paths checked in Chat only",
        ):
            with self.subTest(requirement=requirement):
                self.assertIn(requirement, agent)

    def test_sanitization_preflight_contract_is_declared(self) -> None:
        agent = " ".join(
            (ROOT / ".github" / "agents" / "ai-efficiency-performance-auditor.agent.md")
            .read_text(encoding="utf-8").split()
        )
        for requirement in (
            "one preflight ask_user question per audit, batching exact pending paths",
            "Do not read payloads while awaiting the answer",
            "Negative, ambiguous, or absent replies and unavailable ask_user leave those paths ineligible",
            "Missing paths do not warrant this preflight",
            "An explicit user denial of sanitization overrides an artifact's label",
            "before any header read, establish a payload-free line boundary",
            "sequential ranges of at most three lines",
            "Never include a records/events array or its elements",
            "After the one permitted sanitization preflight, the 'not auditable' stop rules take precedence",
        ):
            with self.subTest(requirement=requirement):
                self.assertIn(requirement, agent)

    def test_evidence_admissibility_and_reconciliation_contract(self) -> None:
        agent = " ".join(
            (ROOT / ".github" / "agents" / "ai-efficiency-performance-auditor.agent.md")
            .read_text(encoding="utf-8").split()
        )
        for requirement in (
            "Scope all keys by export namespace, run and layer",
            "names/arguments/timestamps cannot group retries",
            "Conflicting duplicates stay unresolved; no key means no deduplication",
            "Fallback keys must be documented and cited",
            "preserve types, array order and all fields",
            "equivalence is unproven, not a confirmed duplicate",
            "attempts >= initiated logical calls",
            "mutually exclusive outcomes",
            "totals equal disjoint row sums",
            "Planned but unstarted calls are separate",
            "State mismatches and affected unknowns rather than forcing reconciliation",
        ):
            with self.subTest(requirement=requirement):
                self.assertIn(requirement, agent)

    def test_scope_aware_ranking_and_validation_contract(self) -> None:
        agent = " ".join(
            (ROOT / ".github" / "agents" / "ai-efficiency-performance-auditor.agent.md")
            .read_text(encoding="utf-8").split()
        )
        for requirement in (
            "scenario-local impact (per scenario invocation)",
            "workload-weighted impact (per traffic request)",
            "Use measured branch frequencies from a representative window",
            "Rank within each scenario when weights are unavailable",
            "Cross-group cost ranking requires comparable supported pricing/usage",
            "sample-size rationale and repetitions",
            "quality equivalence/non-inferiority margin",
            "explicit pass/fail/inconclusive rules",
        ):
            with self.subTest(requirement=requirement):
                self.assertIn(requirement, agent)

    def test_provenance_and_safety_contract(self) -> None:
        agent = " ".join(
            (ROOT / ".github" / "agents" / "ai-efficiency-performance-auditor.agent.md")
            .read_text(encoding="utf-8").split()
        )
        for requirement in (
            "discovered versus inspected paths/ranges and selection reasons",
            "Do not discover extra provenance or compute digests",
            "Operation class (read/write) | Identity/auth scope | Freshness | Idempotency | Cache/retry eligibility | Evidence",
            "unknown attributes preclude confirmed safe caching, suppression or retry recommendations",
            "Display repository-relative paths/ranges, not user/home-directory details",
            "Absolute link targets are local-editor-only",
            "Area | Status | Evidence/gap",
            "models-context, output-consumption, safety and runtime-evidence",
            "inspected, partial, missing, not-applicable; cite evidence or explain gaps",
        ):
            with self.subTest(requirement=requirement):
                self.assertIn(requirement, agent)

    def test_exploration_budget_contract(self) -> None:
        agent = " ".join(
            (ROOT / ".github" / "agents" / "ai-efficiency-performance-auditor.agent.md")
            .read_text(encoding="utf-8").split()
        )
        for requirement in (
            "audit-wide 50 distinct files/15,000 returned content lines",
            "per scenario 25 files/7,500 lines",
            "shared guidance additionally 10 files/1,500 lines once per audit",
            "Per file: 300 lines, or up to 600 only for a current finding citing that file and line range",
            "Glob paths count toward file limits",
            "Repeated reads count again",
            "p95 needs at least 20",
            "mean/median need at least 5 completed requests",
            "Persistence checks are not new audit evidence; never use them to explore source",
        ):
            with self.subTest(requirement=requirement):
                self.assertIn(requirement, agent)

    def test_bounded_report_creation_and_host_fallback_contract(self) -> None:
        agent = " ".join(
            (ROOT / ".github" / "agents" / "ai-efficiency-performance-auditor.agent.md")
            .read_text(encoding="utf-8").split()
        )
        for requirement in (
            "Compose and validate complete content before the first write",
            "Probe at most 10 candidates per report, including the base path",
            "An unreadable path is not a free path",
            "Save the detailed report first, in one create operation",
            "truncation is not verification",
            "If read-back fails, a write is partial, or either artifact is invalid",
            "Leave any created file untouched",
            "do not repair, delete, overwrite or retry at another path",
            "This is not a transactional two-file write",
            "without ask_user, give manual preview instructions",
            "do not solicit consent through another tool",
        ):
            with self.subTest(requirement=requirement):
                self.assertIn(requirement, agent)

    def test_entry_point_discovery_contract(self) -> None:
        agent = (ROOT / ".github" / "agents" / "ai-efficiency-performance-auditor.agent.md").read_text(
            encoding="utf-8"
        )
        agent = " ".join(agent.split())
        for requirement in (
            "a supplied source entry point before enumerating source files",
            "using exact paths or file-scoped searches",
            "fits the remaining file budget",
            "exceeds a budget still exhausts it",
            "do not ignore surplus paths or restart the budget",
        ):
            with self.subTest(requirement=requirement):
                self.assertIn(requirement, agent)

    def test_license_is_explicit(self) -> None:
        self.assertTrue((ROOT / "LICENSE").read_text(encoding="utf-8").startswith("MIT License"))


if __name__ == "__main__":
    unittest.main()
