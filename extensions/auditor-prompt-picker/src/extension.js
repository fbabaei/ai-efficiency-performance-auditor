const vscode = require("vscode");
const { insertPrompt } = require("./insert-prompt");

function activate(context) {
  context.subscriptions.push(
    vscode.commands.registerCommand("auditor.insertPrompt", () =>
      insertPrompt(vscode, async () => {
        const uri = vscode.Uri.joinPath(context.extensionUri, "resources", "catalog.json");
        const bytes = await vscode.workspace.fs.readFile(uri);
        return JSON.parse(Buffer.from(bytes).toString("utf8"));
      }),
    ),
  );
}

module.exports = { activate };
