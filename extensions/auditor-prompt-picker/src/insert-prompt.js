const CHAT_COMMAND = "workbench.action.chat.open";

async function insertPrompt(vscode, loadCatalog) {
  try {
    const catalog = await loadCatalog();
    const selected = await vscode.window.showQuickPick(
      catalog.map((entry) => ({
        label: `/${entry.command}`,
        description: entry.title,
        detail: entry.skills.length
          ? `Required skills: ${entry.skills.join(", ")} (install whole directories).`
          : "Base auditor only; no optional skill required.",
        prompt: entry.prompt,
      })),
      {
        title: "Auditor: Insert Prompt",
        placeHolder: "Type /audit-start or search by goal. Insert only; never send.",
        matchOnDescription: true,
        matchOnDetail: true,
      },
    );
    if (!selected) {
      return;
    }
    const confirmation = await vscode.window.showWarningMessage(
      "Insert an editable prompt? This replaces any existing Chat draft. " +
      "Before sending, select AI Efficiency & Performance Auditor, review " +
      "attachments, install the listed skills and replace example paths/placeholders. " +
      "Insertion does not confirm trace sanitization.",
      { modal: true },
      "Insert draft",
    );
    if (confirmation !== "Insert draft") {
      return;
    }
    const commands = await vscode.commands.getCommands(true);
    if (!commands.includes(CHAT_COMMAND)) {
      throw new Error("Chat prefill is unavailable in this VS Code installation");
    }
    await vscode.commands.executeCommand(CHAT_COMMAND, {
      query: selected.prompt,
      isPartialQuery: true,
    });
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    await vscode.window.showErrorMessage(
      `Auditor prompt insertion failed: ${message}. ` +
      "Use the prompt catalog to copy manually. No automatic-send fallback was attempted.",
    );
  }
}

module.exports = { insertPrompt };
