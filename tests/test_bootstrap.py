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

    def standalone_bootstrap(self, answers):
        source_url = "https://github.com/fbabaei/ai-efficiency-performance-auditor.git"
        home = self.root / "home"
        home.mkdir(exist_ok=True)
        downloads = self.root / "downloads"
        downloads.mkdir(exist_ok=True)
        suffix = "sh" if self.shell_type == "bash" else "ps1"
        launcher = downloads / f"bootstrap-auditor.{suffix}"
        shutil.copyfile(SCRIPTS / launcher.name, launcher)
        args = [launcher.as_posix()] if suffix == "sh" else ["-NoProfile", "-File", str(launcher)]
        return subprocess.run(
            [self.shell, *args], input=answers, capture_output=True, text=True, timeout=30,
            env={
                **os.environ,
                "HOME": str(home), "USERPROFILE": str(home),
                "GIT_CONFIG_COUNT": "1",
                "GIT_CONFIG_KEY_0": f"url.{self.source.as_uri()}.insteadOf",
                "GIT_CONFIG_VALUE_0": source_url,
            },
        )

    def test_standalone_clones_and_reuses_auditor_checkout(self):
        for relative in ("scripts/audit-workflows.txt", "docs/usage-prompts.md"):
            (self.source / relative).parent.mkdir(exist_ok=True)
            shutil.copyfile(ROOT / relative, self.source / relative)
        write(self.source / SKILLS / "observability-readiness" / "SKILL.md", "observability")
        git(self.source, "add", ".")
        git(self.source, "-c", "user.name=Bootstrap Test", "-c", "user.email=test@example.invalid",
            "-c", "commit.gpgsign=false", "commit", "-qm", "Fixture")

        result = self.standalone_bootstrap(f"2\n{self.target}\n4\naudit-observability\n\n\n")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        clone = self.root / "home/workspace/ai-efficiency-performance-auditor"
        self.assertTrue((clone / ".git").is_dir())
        self.assertTrue((self.target / SKILLS / "observability-readiness" / "SKILL.md").is_file())
        self.assertIn("Explicitly use observability-readiness", (self.target / SCOUT).read_text(encoding="utf-8"))

        self.source.rename(self.root / "offline-source")
        result = self.standalone_bootstrap(f"2\n{self.target}\n0\n")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Reusing auditor checkout:", result.stdout)
        self.assertIn("Setup cancelled.", result.stdout)

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
        result = self.bootstrap(answers="\n\n\n\n")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        category_menu, submenu = result.stdout.split("\n  Get started\n", 1)
        self.assertNotIn("[audit-", category_menu)
        self.assertNotIn("\x1b", category_menu + submenu)
        self.assertIn("  4) Measurement and observability", category_menu)
        self.assertEqual(
            [line for line in submenu.splitlines() if "[audit-" in line],
            [
                "     1) Base source-only audit [audit-start]",
                "     2) Summarize an existing report [audit-summary]",
            ],
        )
        prompt = (self.target / SCOUT).read_text(encoding="utf-8")
        self.assertIn("Use source code and configuration only.", prompt)
        self.assertNotIn("Scout delivery only:", prompt)
        self.assertFalse((self.target / SKILLS).exists())

    def test_interactive_observability_copies_skill_and_preserves_catalog_safeguards(self):
        write(self.source / SKILLS / "observability-readiness" / "SKILL.md", "observability")
        result = self.bootstrap(
            answers="invalid\n1\naudit-observability\nB\n4\naudit-observability\nretry telemetry\nreview@example.invalid\ny\n"
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Unknown category", result.stdout)
        self.assertIn("Unknown workflow in this category", result.stdout)
        submenu = result.stdout.split("\n  Measurement and observability\n", 1)[1]
        self.assertEqual(
            [line for line in submenu.splitlines() if "[audit-" in line],
            [
                "     8) Measurement readiness [audit-measurement]",
                "     9) Observability readiness [audit-observability]",
            ],
        )
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
        result = self.bootstrap(answers="5\n10\n\nreview@example.invalid\n\n")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        prompt = (self.target / SCOUT).read_text(encoding="utf-8")
        self.assertIn("compare these supplied reports only", prompt)
        self.assertIn("before emailing review@example.invalid", prompt)
        self.assertNotIn("send the same recipient a brief Teams", prompt)
        self.assertTrue((self.target / SKILLS / "audit-comparison/references/contract.md").is_file())

    def test_interactive_cancel_does_not_install(self):
        for answers in ("0\n", "4\n0\n"):
            result = self.bootstrap(answers=answers)
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
        result = self.bootstrap("context-retrieval-review", answers="6\naudit-deep\n\n\n")
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
