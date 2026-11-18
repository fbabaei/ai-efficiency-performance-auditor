const fs = require("node:fs");
const path = require("node:path");

const COMMANDS = fs.readFileSync(
  path.resolve(__dirname, "../../../scripts/audit-workflows.txt"),
  "utf8",
).trim().split(/\r?\n/).map((line) => {
  const [command, title, skills] = line.split("|");
  return [command, title, skills ? skills.split(",") : []];
});

function parseCatalog(markdown) {
  const sections = markdown.replace(/\r\n/g, "\n").split(/^## /m).slice(1);
  const prompts = new Map();
  for (const section of sections) {
    const newline = section.indexOf("\n");
    const title = section.slice(0, newline).trim();
    const blocks = [...section.matchAll(/^```text\n([\s\S]*?)^```[ \t]*$/gm)];
    const command = COMMANDS.find((entry) => entry[1] === title);
    if (!command && blocks.length === 0) {
      continue;
    }
    if (!command) {
      throw new Error(`No picker command maps to catalog section: ${title}`);
    }
    if (prompts.has(title) || blocks.length !== 1 || !blocks[0][1].trim()) {
      throw new Error(`Expected one nonempty prompt in a unique section: ${title}`);
    }
    prompts.set(title, blocks[0][1].trimEnd());
  }
  return COMMANDS.map(([command, title, skills]) => {
    if (!prompts.has(title)) {
      throw new Error(`Missing catalog prompt: ${title}`);
    }
    return { command, title, skills, prompt: prompts.get(title) };
  });
}

module.exports = { parseCatalog };
