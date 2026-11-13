const fs = require("node:fs");
const path = require("node:path");
const { parseCatalog } = require("../src/catalog");

const root = path.resolve(__dirname, "..", "..", "..");
const catalog = fs.readFileSync(path.join(root, "docs", "usage-prompts.md"), "utf8");
const output = path.join(__dirname, "..", "resources");
fs.mkdirSync(output, { recursive: true });
fs.writeFileSync(
  path.join(output, "catalog.json"),
  `${JSON.stringify(parseCatalog(catalog), null, 2)}\n`,
);
fs.copyFileSync(path.join(root, "LICENSE"), path.join(__dirname, "..", "LICENSE"));
console.log("Built prompt catalog from docs/usage-prompts.md.");
