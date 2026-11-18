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
- what you want to do: press Enter for a source-only audit, or choose a specialist
  such as audit-observability to review telemetry and alert readiness
- optional focus (setup selects the required skills for your workflow)
- optional email/Teams delivery

4) Copy the generated Scout command
Also saved in: <target-repo>/SCOUT-AUDIT-COMMAND.txt

5) Replace the placeholders, review the scope, then paste the prompt into Scout.

Setup installs the agent and skills and drafts the prompt. It does not run the
audit or send a report.
```
