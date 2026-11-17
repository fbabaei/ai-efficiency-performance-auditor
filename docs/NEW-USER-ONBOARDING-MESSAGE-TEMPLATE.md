# New User Onboarding Message Template

Use this message when onboarding a new user to run the AI Efficiency & Performance Auditor with Scout.

```text
Hi <Name>,

Welcome! Here is the fastest way to set up and run the AI Efficiency & Performance Auditor with Scout.

1) Clone the repository
https://github.com/fbabaei/ai-efficiency-performance-auditor

2) Open a terminal in that repo and run interactive setup

Windows
.\scripts\bootstrap-auditor.cmd -Interactive

Linux/macOS
./scripts/bootstrap-auditor.sh --interactive

3) Complete the prompts
- target repo URL/path
- optional skills
- audit focus
- optional email/Teams delivery

4) Copy the generated Scout command
Also saved in: <target-repo>/SCOUT-AUDIT-COMMAND.txt

5) Paste the command into Scout and run it

That's it - setup and a ready-to-run audit command are handled automatically.
```
