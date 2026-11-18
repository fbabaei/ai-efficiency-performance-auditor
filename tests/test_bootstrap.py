import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
AGENT = Path(".github/agents/ai-efficiency-performance-auditor.agent.md")
SKILLS = Path(".github/skills")
SCOUT = Path("SCOUT-AUDIT-COMMAND.txt")
SKILL = "example-review"


def git(repo, *args):
    subprocess.run(
        ["git", "-C", str(repo), *args], check=True, capture_output=True, timeout=30
    )


def write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


class BootstrapTests:
    def setUp(self):
        if not self.shell or not shutil.which("git"):
            self.skipTest("Bootstrap shell and Git are required")
        temp = tempfile.TemporaryDirectory(prefix="auditor bootstrap ")
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.source = self.root / "source repo"
        self.target = self.root / "target repo"
        for repo in (self.source, self.target):
            repo.mkdir()
            git(repo, "init", "-q")
        write(self.source / AGENT, "agent")
        write(self.source / SKILLS / SKILL / "references" / "notes.md", "notes")
        write(self.source / SKILLS / SKILL / "SKILL.md", "skill")

    def bootstrap(self, *skills, source=None, target=None, answers=None):
        source = self.source if source is None else source
        target = self.target if target is None else target
        if self.shell_type == "bash":
            args = [
                (SCRIPTS / "bootstrap-auditor.sh").as_posix(),
                "--source-repo-path", source.as_posix(),
                "--target-repo-path", target.as_posix(),
            ]
            for skill in skills:
                args.extend(["--skill", skill])
            if answers is not None:
                args.append("--interactive")
        else:
            def quoted(value):
                return "'" + str(value).replace("'", "''") + "'"

            command = (
                f"& {quoted(SCRIPTS / 'bootstrap-auditor.ps1')} "
                f"-SourceRepoPath {quoted(source)} -TargetRepoPath {quoted(target)}"
            )
            if skills:
                command += " -Skills " + ",".join(map(quoted, skills))
            if answers is not None:
                args = ["-NoProfile", "-Command", command + " -Interactive"]
            else:
                args = ["-NoProfile", "-NonInteractive", "-Command", command]
        return subprocess.run(
            [self.shell, *args], input=answers, capture_output=True, text=True, timeout=30
        )

    def assert_rejected(self, result, message):
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn(message, result.stderr)

    def assert_no_install(self):
        self.assertFalse((self.target / ".github").exists())
        self.assertFalse((self.target / SCOUT).exists())

    def test_rejects_unsafe_skill_names_before_install(self):
        for skill in ("../outside", r"..\outside", "/absolute", "C:drive", ".", "NUL", ""):
            with self.subTest(skill=skill):
                self.assert_rejected(self.bootstrap(SKILL, skill), "Invalid skill name")
                self.assert_no_install()

    def test_missing_late_skill_does_not_leave_partial_install(self):
        self.assert_rejected(self.bootstrap(SKILL, "missing"), "Requested skill not found")
        self.assert_no_install()

    def test_preflights_every_collision_without_overwriting(self):
        for path in (AGENT, SKILLS / SKILL / "custom.md", SCOUT):
            with self.subTest(path=path):
                item = self.target / path
                write(item, "keep")
                self.assert_rejected(self.bootstrap(SKILL), "Install path already exists")
                self.assertEqual(item.read_text(encoding="utf-8"), "keep")
                actual = {
                    entry.relative_to(self.target)
                    for entry in self.target.rglob("*")
                    if ".git" not in entry.relative_to(self.target).parts and entry.is_file()
                }
                self.assertEqual(actual, {path})
                item.unlink()
                if path.parts[0] == ".github":
                    for parent in item.parents:
                        if parent == self.target:
                            break
                        parent.rmdir()

    def test_rejects_linked_target_parent_and_nested_source_link(self):
        outside = self.root / "outside"
        outside.mkdir()
        write(outside / "keep.md", "keep")
        target_link = self.target / ".github"
        source_link = self.source / SKILLS / SKILL / "nested"
        for path in (target_link, source_link):
            if os.name == "nt":
                from _winapi import CreateJunction

                CreateJunction(str(outside), str(path))
            else:
                path.symlink_to(outside, target_is_directory=True)
            try:
                self.assert_rejected(self.bootstrap(SKILL), "link")
                self.assertEqual([entry.name for entry in outside.iterdir()], ["keep.md"])
                self.assertFalse((self.target / AGENT).exists())
                self.assertFalse((self.target / SCOUT).exists())
            finally:
                if os.name == "nt":
                    path.rmdir()
                else:
                    path.unlink()

    def test_installs_without_optional_skills(self):
        result = self.bootstrap()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue((self.target / AGENT).is_file())
        self.assertTrue((self.target / SCOUT).is_file())
        self.assertFalse((self.target / SKILLS).exists())

    def test_interactive_defaults_to_base_without_skills_or_delivery(self):
        result = self.bootstrap(answers="\n\n\n")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Observability readiness [audit-observability]", result.stdout)
        prompt = (self.target / SCOUT).read_text(encoding="utf-8")
        self.assertIn("Use source code and configuration only.", prompt)
        self.assertNotIn("Scout delivery only:", prompt)
        self.assertFalse((self.target / SKILLS).exists())

    def test_interactive_observability_copies_skill_and_preserves_catalog_safeguards(self):
        write(self.source / SKILLS / "observability-readiness" / "SKILL.md", "observability")
        result = self.bootstrap(
            answers="invalid\naudit-observability\nretry telemetry\nreview@example.invalid\ny\n"
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Unknown workflow", result.stdout)
        prompt = (self.target / SCOUT).read_text(encoding="utf-8")
        for expected in (
            "Explicitly use observability-readiness",
            "Report only: Use <exact existing report path>",
            "Scoped source: Start at <exact source entry point>",
            "exact-path sanitization gate before any payload access",
            "Rate alert readiness separately",
            "Additional focus within the selected scope: retry telemetry",
            "before emailing review@example.invalid",
            "After successful email delivery",
        ):
            self.assertIn(expected, prompt)
        self.assertEqual(
            [p.name for p in (self.target / SKILLS).iterdir()],
            ["observability-readiness"],
        )

    def test_interactive_comparison_installs_references_and_defaults_to_email_only(self):
        write(self.source / SKILLS / "audit-comparison" / "SKILL.md", "comparison")
        write(self.source / SKILLS / "audit-comparison" / "references" / "contract.md", "contract")
        result = self.bootstrap(answers="10\n\nreview@example.invalid\n\n")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        prompt = (self.target / SCOUT).read_text(encoding="utf-8")
        self.assertIn("compare these supplied reports only", prompt)
        self.assertIn("before emailing review@example.invalid", prompt)
        self.assertNotIn("send the same recipient a brief Teams", prompt)
        self.assertTrue((self.target / SKILLS / "audit-comparison/references/contract.md").is_file())

    def test_interactive_cancel_does_not_install(self):
        result = self.bootstrap(answers="0\n")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Setup cancelled.", result.stdout)
        self.assert_no_install()

    def test_interactive_deep_review_installs_all_required_skills(self):
        required = {
            "orchestration-efficiency-review", "context-retrieval-review",
            "service-performance-review",
        }
        for skill in required:
            write(self.source / SKILLS / skill / "SKILL.md", skill)
        result = self.bootstrap("context-retrieval-review", answers="audit-deep\n\n\n")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        prompt = (self.target / SCOUT).read_text(encoding="utf-8")
        self.assertEqual({p.name for p in (self.target / SKILLS).iterdir()}, required)
        for skill in required:
            self.assertIn(skill, prompt)

    def test_accepts_linked_worktree_roots_and_deduplicates_skills(self):
        for repo, name in ((self.source, "source worktree"), (self.target, "target worktree")):
            git(repo, "add", ".")
            git(repo, "-c", "user.name=Bootstrap Test", "-c", "user.email=test@example.invalid",
                "-c", "commit.gpgsign=false", "commit", "-qm", "Fixture", "--allow-empty")
            worktree = self.root / name
            git(repo, "worktree", "add", "-q", "--detach", str(worktree), "HEAD")
            self.assertTrue((worktree / ".git").is_file())
        target = self.root / "target worktree"
        result = self.bootstrap(SKILL, SKILL, source=self.root / "source worktree", target=target)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual((target / AGENT).read_text(encoding="utf-8"), "agent")
        self.assertEqual(
            (target / SKILLS / SKILL / "references" / "notes.md").read_text(encoding="utf-8"),
            "notes",
        )
        self.assertIn("focus on latency", (target / SCOUT).read_text(encoding="utf-8"))

    def test_rejects_fake_git_marker_and_subdirectory(self):
        fake = self.root / "not a repository"
        write(fake / ".git", "not a valid gitfile")
        nested = self.target / "nested"
        nested.mkdir()
        self.assert_rejected(
            self.bootstrap(source=fake), "Source path is not a git repository"
        )
        self.assert_rejected(
            self.bootstrap(target=nested), "Target path is not a git repository"
        )
        self.assert_no_install()


def find_bash():
    if os.name == "nt":
        git_bash = Path(os.environ.get("ProgramFiles", r"C:\Program Files")) / "Git/bin/bash.exe"
        if git_bash.is_file():
            return str(git_bash)
    return shutil.which("bash")


class BashBootstrapTests(BootstrapTests, unittest.TestCase):
    shell_type = "bash"
    shell = find_bash()


class PowerShellBootstrapTests(BootstrapTests, unittest.TestCase):
    shell_type = "powershell"
    shell = shutil.which("pwsh")
