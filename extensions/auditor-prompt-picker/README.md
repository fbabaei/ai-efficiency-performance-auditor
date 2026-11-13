# Auditor Prompt Picker

A separate, optional VS Code extension that inserts one of the auditor's
14 prompt templates into Copilot Chat as **editable, unsent text**.

## Use

1. Install the AI Efficiency & Performance Auditor agent and any required skills
   in the application repository you want to review.
2. Select that agent in Copilot Chat. Finish or copy any existing Chat draft.
3. Open the Command Palette (`Ctrl+Shift+P`) and run **Auditor: Insert Prompt**.
4. Type `/audit-start`, `/audit-context`, or search by your goal.
   The picker lists required skills; it does not install them.
5. Select a prompt and confirm replacement of the existing Chat draft.
6. Replace all example paths and placeholders, review attachments and agent
   selection, then press **Enter** yourself when ready.

The slash-style names belong to this picker, **not Copilot's native slash menu**.
The extension cannot intercept text typed directly into Copilot Chat.
Assign `auditor.insertPrompt` a shortcut in Keyboard Shortcuts for quicker access.

## Build and install from the repository

Requirements: VS Code 1.146+, Node.js 22+ and npm for development.
The extension itself has no runtime npm dependencies.

In PowerShell, from the repository root:

```powershell
Set-Location .\extensions\auditor-prompt-picker
npm test
npx --yes --package @vscode/vsce@3 vsce package
```

The packaging command downloads Microsoft's VS Code extension packaging tool
if needed; it does not publish the extension. The prepublish build bundles
the current catalog from the repository, so build from the full checkout.
Use **Extensions: Install from VSIX...** to install the resulting package.

## Boundaries and compatibility

- Reads only its bundled templates. Does not read application source, collect
  telemetry, invoke a model, run audit tools or change the agent's permissions.
- Does not write the clipboard, automatically submit a query or attach files.
- Warns before replacing a draft; it cannot inspect or back up Copilot drafts.
- Does not select the agent or install skills. Review existing attachments,
  since they can affect the scope of the eventual request.
- Templates do not confirm runtime-file sanitization.
- Prefill uses VS Code's built-in `workbench.action.chat.open` command with
  `isPartialQuery: true`. This is a version-sensitive command contract, not a
  stable Chat-input editing API. Test it in your host before relying on it;
  mocked tests do not establish live Copilot compatibility.
- On a reported error, copy from the
  [prompt catalog](https://github.com/fbabaei/ai-efficiency-performance-auditor/blob/main/docs/usage-prompts.md)
  manually. No automatic-send fallback is used.

See the
[setup and verification guide](https://github.com/fbabaei/ai-efficiency-performance-auditor/blob/main/docs/prompt-picker.md)
for all command names and a manual host check.
