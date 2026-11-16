# New User Onboarding Message Template

Use this message when onboarding a new user to run the AI Efficiency & Performance Auditor with Scout.

```text
Hi <Name> — here’s the fastest way to set up and run the AI Efficiency & Performance Auditor with Scout.

1) Clone this repo:
https://github.com/fbabaei/ai-efficiency-performance-auditor

2) Open a terminal in that repo and run interactive setup:

Windows
.\scripts\bootstrap-auditor.cmd -Interactive

Linux/macOS
./scripts/bootstrap-auditor.sh --interactive

3) Answer the prompts (target repo URL/path, optional skills, audit focus, optional email/Teams delivery).

4) When it finishes, copy the generated Scout command (also saved in <target-repo>/SCOUT-AUDIT-COMMAND.txt).

5) Paste that command into Scout and run it.

That’s it — setup + ready-to-run audit command are handled automatically.
```

