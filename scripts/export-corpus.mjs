// Exports the frontend's mock newsroom (src/data/mock-newspaper.ts) to
// backend/app/data/corpus.json so the chat backend retrieves from the
// exact same stories and editions the UI shows. Run: npm run export:corpus
import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { createRequire } from "node:module";
import path from "node:path";
import { fileURLToPath } from "node:url";
import vm from "node:vm";

const require = createRequire(import.meta.url);
const ts = require("typescript");

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const source = readFileSync(path.join(root, "src/data/mock-newspaper.ts"), "utf8");

const { outputText } = ts.transpileModule(source, {
  compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2020 },
});

const sandbox = { exports: {}, require: () => ({}) };
vm.runInNewContext(outputText, sandbox);
const { mockArticles, mockEditions, mockStoryDetails } = sandbox.exports;

const articles = mockArticles.map((a) => {
  const detail = mockStoryDetails[a.id];
  return {
    id: a.id,
    title: a.title,
    summary: a.summary,
    category: a.category,
    source: a.source,
    source_url: a.sourceUrl,
    published_at: a.publishedAt,
    image_url: a.imageUrl ?? null,
    topics: a.topics,
    what_happened: detail?.whatHappened ?? null,
    why_it_matters: detail?.whyItMatters ?? null,
    key_facts: detail?.keyFacts ?? [],
  };
});

const editions = mockEditions.map((e) => ({
  id: e.id,
  date: e.date,
  headline: e.headline,
  summary: e.summary,
  story_ids: e.stories.map((s) => s.id),
}));

const out = path.join(root, "backend/app/data/corpus.json");
mkdirSync(path.dirname(out), { recursive: true });
writeFileSync(out, JSON.stringify({ articles, editions }, null, 2) + "\n");
console.log(`Wrote ${articles.length} articles and ${editions.length} editions to ${path.relative(root, out)}`);
