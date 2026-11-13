# Editable prompt insertion in VS Code

The optional [Auditor Prompt Picker extension](../extensions/auditor-prompt-picker/)
lets you choose a short name and insert the corresponding prompt as **editable,
unsent text** in Copilot Chat. It is separate from the auditor and its skills;
the agent definition and permissions are unchanged.

This is the picker-based alternative to literal slash expansion. It **does not**
intercept `/commands` typed in Copilot's own input box or register native slash
commands. Native skills load instructions rather than expanding editable text.

## Install

You need VS Code 1.146+ with Copilot Chat, plus Node.js 22+ and npm to build.
Use a full checkout of this repository, since the build reads the existing
[prompt catalog](usage-prompts.md) rather than maintaining another prompt copy.

From the repository root in PowerShell:

```powershell
Set-Location .\extensions\auditor-prompt-picker
npm test
npx --yes --package @vscode/vsce@3 vsce package
```

The last command downloads Microsoft's packaging tool if needed and creates
`auditor-prompt-picker-0.1.0.vsix` in that directory. It does not publish to the
Marketplace. In VS Code, run **Extensions: Install from VSIX...**, choose the
package and reload if requested. No npm dependencies are needed at runtime.

For development without installation, run `npm run build` in the same directory,
then launch an Extension Development Host:

```powershell
code --new-window --extensionDevelopmentPath="$PWD"
```

Install the base auditor and required whole skill directories in your
**application repository** separately, following the [quick start](quick-start.md).
The extension bundles templates, not the agent or skills. Installing a VSIX
does not install the auditor in every workspace.

## Use

1. Open the application repository and select **AI Efficiency & Performance
   Auditor** in Copilot Chat.
2. Finish or copy any existing Chat draft.
3. Press **Ctrl+Shift+P** and choose **Auditor: Insert Prompt**.
4. Type `/audit-start` or search by goal; select the result.
5. Confirm replacing the Chat draft. **Cancel** or **Escape** leaves it alone.
6. Edit the inserted prompt: replace every placeholder and example path, install
   the listed skills, and check agent selection and existing attachments.
7. Press **Enter** yourself when ready. Selecting a picker item never sends it.

For fewer keystrokes, open **Preferences: Open Keyboard Shortcuts**, search for
**Auditor: Insert Prompt** (`auditor.insertPrompt`) and assign an unused shortcut.
No global keybinding is installed automatically.

## Picker names

| Name typed in the picker | Template | Required skills |
|---|---|---|
| `/audit-start` | [Base source-only audit](usage-prompts.md#base-source-only-audit) | None |
| `/audit-summary` | [Summarize an existing report](usage-prompts.md#summarize-an-existing-report) | None |
| `/audit-context` | [Context and retrieval](usage-prompts.md#context-and-retrieval) | `context-retrieval-review` |
| `/audit-orchestration` | [Orchestration efficiency](usage-prompts.md#orchestration-efficiency) | `orchestration-efficiency-review` |
| `/audit-service` | [Service performance](usage-prompts.md#service-performance) | `service-performance-review` |
| `/audit-plan` | [Recommendation planning](usage-prompts.md#recommendation-planning) | `recommendation-planning` |
| `/audit-change` | [Change-impact review](usage-prompts.md#change-impact-review) | `change-impact-review` |
| `/audit-measurement` | [Measurement readiness](usage-prompts.md#measurement-readiness) | `measurement-readiness` |
| `/audit-compare` | [Baseline/candidate comparison](usage-prompts.md#baselinecandidate-comparison) | `audit-comparison` with references |
| `/audit-verify` | [Finding-level verification](usage-prompts.md#finding-level-verification) | `audit-comparison` with references |
| `/audit-budgets` | [Efficiency-budget interpretation](usage-prompts.md#efficiency-budget-interpretation) | `efficiency-budget-review` |
| `/audit-focused` | [Focused first audit](usage-prompts.md#focused-first-audit) | Context + orchestration skills |
| `/audit-deep` | [Deep analysis](usage-prompts.md#deep-analysis) | Context + orchestration + service skills |
| `/audit-traces` | [Trace-only audit](usage-prompts.md#trace-only-audit) | None; eligible sanitized trace inputs required |

Every choice includes the base auditor. No command runs the offline importer
or gate. Existing reusable prompt files and optional skill commands are unchanged.

## Boundaries and compatibility

- The extension reads only its bundled catalog, not application files. It
  performs no model calls, telemetry collection or audit execution, and it does
  not use the clipboard or attach files.
- The confirmation is necessary because VS Code does not expose a supported
  draft-inspection/backup API for this integration. The extension cannot merge
  drafts or verify which agent and attachments are selected.
- Insertion is **not sanitization confirmation**. Runtime artifacts still need
  exact-path eligibility evidence under the core policy. Do not endorse paths
  you have not checked, or paste secrets/private payloads.
- Prefill uses the built-in `workbench.action.chat.open` command with
  `isPartialQuery: true`. VS Code's current implementation sets the draft for
  that option instead of accepting it. This is a version-sensitive command
  contract, not a stable public Chat-input editing API. A command returning
  without error does not prove that every harness displayed the draft correctly.
- Errors are shown explicitly. There is no retry that drops `isPartialQuery`,
  automatic-send fallback, model-based expansion or silent clipboard fallback.
  If insertion fails, copy a template from the catalog manually.

Implementation reference:
[VS Code chat actions](https://github.com/microsoft/vscode/blob/main/src/vs/workbench/contrib/chat/browser/actions/chatActions.ts).
Legacy `.prompt.md` invocation and native skill invocation are different features;
see [prompt files](https://code.visualstudio.com/docs/agent-customization/prompt-files)
and [skills](https://code.visualstudio.com/docs/agent-customization/agent-skills).

## Verify in your VS Code host

The automated checks validate catalog coverage, verbatim prompt generation,
consent/cancellation, error reporting and partial-query arguments using a mocked
host. They do **not** prove live Copilot behavior.

After installation, perform this manual check without submitting an audit:

1. Put a disposable draft in Chat. Open the picker, choose `/audit-start`, then
   cancel the replacement warning. Verify the draft is unchanged.
2. Repeat and confirm insertion. Verify the full prompt is editable and no
   request was sent or model response started.
3. Replace a placeholder, then clear the draft without sending.
4. Check `/audit-deep` lists all three skills and inserts its own template.
5. Check `/audit-traces` retains the statement that the template does not
   confirm sanitization. Do not attach real traces for this UI check.

If any step fails, do not rely on prefill in that host; use manual copy/paste.
