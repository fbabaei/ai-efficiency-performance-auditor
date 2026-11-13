const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");
const { parseCatalog } = require("../src/catalog");

const markdown = fs.readFileSync(
  path.resolve(__dirname, "..", "..", "..", "docs", "usage-prompts.md"),
  "utf8",
).replace(/\r\n/g, "\n");

test("all 14 catalog templates are packaged verbatim and have unique commands", () => {
  const catalog = parseCatalog(markdown);
  const templates = [...markdown.matchAll(/^```text\n([\s\S]*?)^```[ \t]*$/gm)]
    .map((match) => match[1].trimEnd());
  assert.equal(catalog.length, 14);
  assert.equal(new Set(catalog.map((entry) => entry.command)).size, catalog.length);
  assert.deepEqual(catalog.map((entry) => entry.prompt), templates);
  assert.deepEqual(require("../resources/catalog.json"), catalog);
  for (const entry of catalog) {
    for (const skill of entry.skills) {
      assert.ok(entry.prompt.includes(skill), `${entry.command} must request ${skill}`);
      assert.ok(fs.existsSync(path.resolve(
        __dirname, "..", "..", "..", ".github", "skills", skill, "SKILL.md",
      )));
    }
  }
});

test("Windows line endings do not change the inserted prompts", () => {
  assert.deepEqual(parseCatalog(markdown.replace(/\n/g, "\r\n")), parseCatalog(markdown));
});

test("a new unmapped template fails the build instead of silently omitting it", () => {
  assert.throws(
    () => parseCatalog(`${markdown}\n## New workflow\n\n\`\`\`text\nReview.\n\`\`\`\n`),
    /No picker command maps/,
  );
});

test("missing and duplicate prompt sections fail explicitly", () => {
  assert.throws(
    () => parseCatalog(markdown.replace("## Base source-only audit", "## Renamed audit")),
    /No picker command maps/,
  );
  assert.throws(
    () => parseCatalog(`${markdown}\n## Base source-only audit\n\n\`\`\`text\nAgain.\n\`\`\`\n`),
    /unique section/,
  );
  assert.throws(() => parseCatalog("## Choose your goal\nNo prompts."), /Missing catalog prompt/);
});

test("an empty or ambiguous template is rejected", () => {
  assert.throws(
    () => parseCatalog("## Base source-only audit\n\n```text\n \n```\n"),
    /nonempty prompt/,
  );
  assert.throws(
    () => parseCatalog("## Base source-only audit\n```text\nFirst\n```\n```text\nSecond\n```\n"),
    /one nonempty prompt/,
  );
});
