# New User Onboarding Message Template

Use this message when onboarding a new user to run the AI Efficiency & Performance Auditor with Scout.

```text
Hi <Name>,

Welcome! Here is the fastest way to set up and run the AI Efficiency & Performance Auditor with Scout.

1) Save the trusted bootstrap script for your platform. Git is required.

2) Open a terminal in the folder where you saved it:

Windows (PowerShell 7)
pwsh -NoProfile -File .\bootstrap-auditor.ps1

Linux/macOS (Bash)
bash ./bootstrap-auditor.sh

The script clones the auditor repo if it is missing, or reuses the existing
matching checkout. You do not need to clone the auditor manually.

3) Complete the prompts
- target repo URL/path
- choose a category, then a workflow: press Enter at both menus for a
  source-only audit, or choose category 4 then workflow 9 for observability
- optional focus (setup selects the required skills for your workflow)
- optional email/Teams delivery

4) Copy the generated Scout command
Also saved in: <target-repo>/SCOUT-AUDIT-COMMAND.txt

5) Replace the placeholders, review the scope, then paste the prompt into Scout.

Setup installs the agent and skills and drafts the prompt. It does not run the
audit or send a report.
```
