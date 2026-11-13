const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");
const vm = require("node:vm");
const { insertPrompt } = require("../src/insert-prompt");

test("the contributed command loads its packaged catalog and registers disposal", async () => {
  const manifest = require("../package.json");
  const subscriptions = [];
  const catalog = fs.readFileSync(path.resolve(__dirname, "..", "resources", "catalog.json"));
  let handler;
  let requestedUri;
  let offeredItems;
  const disposable = { dispose() {} };
  const vscode = {
    Uri: { joinPath: (...segments) => segments.join("/") },
    commands: {
      registerCommand(command, callback) {
        assert.equal(command, manifest.contributes.commands[0].command);
        handler = callback;
        return disposable;
      },
    },
    workspace: {
      fs: {
        async readFile(uri) {
          requestedUri = uri;
          return catalog;
        },
      },
    },
    window: {
      async showQuickPick(items) {
        offeredItems = items;
        return undefined;
      },
      async showErrorMessage(message) {
        assert.fail(message);
      },
    },
  };
  const moduleObject = { exports: {} };
  vm.runInNewContext(
    fs.readFileSync(path.resolve(__dirname, "..", manifest.main), "utf8"),
    {
      module: moduleObject,
      Buffer,
      require(name) {
        if (name === "vscode") return vscode;
        if (name === "./insert-prompt") return { insertPrompt };
        assert.fail(`Unexpected dependency: ${name}`);
      },
    },
  );
  moduleObject.exports.activate({ subscriptions, extensionUri: "extension" });
  assert.equal(subscriptions[0], disposable);
  await handler();
  assert.equal(requestedUri, "extension/resources/catalog.json");
  assert.equal(offeredItems.length, 14);
});
