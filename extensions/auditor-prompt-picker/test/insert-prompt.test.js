const assert = require("node:assert/strict");
const test = require("node:test");
const { insertPrompt } = require("../src/insert-prompt");
const catalog = require("../resources/catalog.json");

function host({ cancelPicker = false, cancelConfirmation = false, available = true, failure } = {}) {
  const calls = [];
  const errors = [];
  const vscode = {
    window: {
      async showQuickPick(items, options) {
        calls.push(["pick", items, options]);
        return cancelPicker ? undefined : items[0];
      },
      async showWarningMessage(...args) {
        calls.push(["confirm", ...args]);
        return cancelConfirmation ? undefined : "Insert draft";
      },
      async showErrorMessage(message) {
        errors.push(message);
      },
    },
    commands: {
      async getCommands() {
        return available ? ["workbench.action.chat.open"] : [];
      },
      async executeCommand(...args) {
        calls.push(["execute", ...args]);
        if (failure) {
          throw failure;
        }
      },
    },
  };
  return { vscode, calls, errors };
}

test("the picker inserts the exact template as a partial query only after consent", async () => {
  const { vscode, calls, errors } = host();
  await insertPrompt(vscode, async () => catalog);
  assert.deepEqual(calls.map((call) => call[0]), ["pick", "confirm", "execute"]);
  const items = calls[0][1];
  assert.equal(items.length, 14);
  assert.equal(items[0].label, "/audit-start");
  assert.match(items.find((item) => item.label === "/audit-deep").detail, /service-performance-review/);
  assert.equal(calls[1][2].modal, true);
  assert.match(calls[1][1], /replaces any existing Chat draft/);
  assert.deepEqual(calls[2], ["execute", "workbench.action.chat.open", {
    query: catalog[0].prompt,
    isPartialQuery: true,
  }]);
  assert.deepEqual(errors, []);
});

test("every picker choice inserts its own prompt, including the trace safeguards", async () => {
  for (let index = 0; index < catalog.length; index += 1) {
    const { vscode, calls, errors } = host();
    vscode.window.showQuickPick = async (items) => items[index];
    await insertPrompt(vscode, async () => catalog);
    const execution = calls.find((call) => call[0] === "execute");
    assert.deepEqual(execution[2], { query: catalog[index].prompt, isPartialQuery: true });
    assert.deepEqual(errors, []);
  }
});

test("cancelling the picker or replacement confirmation never opens Chat", async () => {
  for (const options of [{ cancelPicker: true }, { cancelConfirmation: true }]) {
    const { vscode, calls, errors } = host(options);
    await insertPrompt(vscode, async () => catalog);
    assert.ok(!calls.some((call) => call[0] === "execute"));
    assert.deepEqual(errors, []);
  }
});

test("missing Chat support reports an error without a send or clipboard fallback", async () => {
  const { vscode, calls, errors } = host({ available: false });
  await insertPrompt(vscode, async () => catalog);
  assert.ok(!calls.some((call) => call[0] === "execute"));
  assert.equal(errors.length, 1);
  assert.match(errors[0], /Chat prefill is unavailable/);
});

test("prefill failure is explicit and is not retried as a submitted query", async () => {
  const { vscode, calls, errors } = host({ failure: new Error("Host refused") });
  await insertPrompt(vscode, async () => catalog);
  assert.equal(calls.filter((call) => call[0] === "execute").length, 1);
  assert.equal(errors.length, 1);
  assert.match(errors[0], /Host refused/);
  assert.match(errors[0], /No automatic-send fallback/);
});

test("a missing or corrupt packaged catalog reports an error before prompting", async () => {
  const { vscode, calls, errors } = host();
  await insertPrompt(vscode, async () => { throw new Error("Invalid catalog"); });
  assert.deepEqual(calls, []);
  assert.equal(errors.length, 1);
  assert.match(errors[0], /Invalid catalog/);
});
