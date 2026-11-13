const COMMANDS = [
  ["audit-start", "Base source-only audit", []],
  ["audit-summary", "Summarize an existing report", []],
  ["audit-context", "Context and retrieval", ["context-retrieval-review"]],
  ["audit-orchestration", "Orchestration efficiency", ["orchestration-efficiency-review"]],
  ["audit-service", "Service performance", ["service-performance-review"]],
  ["audit-plan", "Recommendation planning", ["recommendation-planning"]],
  ["audit-change", "Change-impact review", ["change-impact-review"]],
  ["audit-measurement", "Measurement readiness", ["measurement-readiness"]],
  ["audit-compare", "Baseline/candidate comparison", ["audit-comparison"]],
  ["audit-verify", "Finding-level verification", ["audit-comparison"]],
  ["audit-budgets", "Efficiency-budget interpretation", ["efficiency-budget-review"]],
  ["audit-focused", "Focused first audit", ["orchestration-efficiency-review", "context-retrieval-review"]],
  ["audit-deep", "Deep analysis", ["orchestration-efficiency-review", "context-retrieval-review", "service-performance-review"]],
  ["audit-traces", "Trace-only audit", []],
];

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
