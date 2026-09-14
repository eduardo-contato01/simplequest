import assert from "node:assert/strict";
import { mkdir, readFile, writeFile } from "node:fs/promises";
import path from "node:path";
import test, { before } from "node:test";
import { fileURLToPath, pathToFileURL } from "node:url";
import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { build } from "vite";
import { normalizeQuestionContent } from "../app/question-model.ts";

const root = fileURLToPath(new URL("../", import.meta.url));
const catalog = JSON.parse(await readFile(new URL("../public/data/questions.json", import.meta.url), "utf8"));
const fixture = JSON.parse(await readFile(new URL("./fixtures/baseline-cases.json", import.meta.url), "utf8"));
const example = (name) => normalizeQuestionContent(catalog.find(({ id }) => id === fixture.cases[name]));
const noop = () => {};
let components;

before(async () => {
  // Compile the real TSX modules with the project's bundler. No browser, API or server.
  const entry = path.join(root, "component-contract-entry.mjs").replaceAll("\\", "/");
  const names = ["QuestionCard", "QuestionAlternatives", "QuestionFilters", "QuestionsPagination", "SimulationComposer", "SimulationPrintSheet"];
  const result = await build({
    configFile: false, root, publicDir: false, logLevel: "error",
    plugins: [{
      name: "component-contracts",
      resolveId(id) { if (id.replaceAll("\\", "/") === entry) return "\0" + entry; },
      load(id) { if (id === "\0" + entry) return names.map((name) => `export { ${name} } from ${JSON.stringify(path.join(root, `app/components/${name}.tsx`).replaceAll("\\", "/"))};`).join("\n"); },
    }],
    build: { write: false, lib: { entry, formats: ["es"] }, rolldownOptions: { external: ["react", "react-dom", "react/jsx-runtime"] } },
    define: { "process.env.NODE_ENV": '"test"' },
  });
  const output = path.join(root, "outputs/component-contracts.mjs");
  await mkdir(path.dirname(output), { recursive: true });
  await writeFile(output, result[0].output.find(({ type }) => type === "chunk").code);
  components = await import(pathToFileURL(output).href);
});

const render = (name, props) => renderToStaticMarkup(createElement(components[name], props));
const cardProps = (question) => ({ question, isSelected: false, isExpanded: true, isRevealed: false, response: "", onToggleSelected: noop, onToggleExpanded: noop, onToggleAnswer: noop, onResponseChange: noop });

test("cartões extraídos preservam os exemplos ricos e o selo editorial", () => {
  const text = render("QuestionCard", cardProps(example("text")));
  assert.match(text, /class="question-blocks"/);
  assert.match(text, /Autenticada · Admin/);
  assert.match(text, /625/);
  assert.match(text, /role="radiogroup"/);
  assert.equal((text.match(/role="radio"/g) || []).length, 5);
  assert.match(render("QuestionCard", cardProps(example("inlineMath"))), /class="inline-math/);
  assert.match(render("QuestionCard", cardProps(example("blockFormula"))), /class="math-formula/);
  const table = render("QuestionCard", cardProps(example("table")));
  assert.equal((table.match(/<td[ >]/g) || []).length, 5);
  assert.match(table, /83160/);
  assert.equal((render("QuestionCard", cardProps(example("image"))).match(/<img /g) || []).length, 2);
  assert.equal((render("QuestionCard", cardProps(example("alternativeImage"))).match(/<img /g) || []).length, 6);
  const collapsed = render("QuestionCard", { ...cardProps(example("text")), isExpanded: false, isSelected: true, isRevealed: true });
  assert.match(collapsed, /question-card selected/);
  assert.match(collapsed, /Gabarito: A/);
  assert.doesNotMatch(collapsed, /role="radio"/);
});

test("alternativas controladas preservam feedback e fallbacks dos modos de resposta", () => {
  const props = { question: example("text"), response: "B", onResponseChange: noop };
  const incorrect = render("QuestionAlternatives", props);
  assert.match(incorrect, /alternative-option correct" role="radio" aria-checked="false"/);
  assert.match(incorrect, /alternative-option incorrect" role="radio" aria-checked="true"/);
  assert.match(incorrect, /Resposta incorreta. Gabarito: A./);
  assert.match(render("QuestionAlternatives", { ...props, response: "A" }), /Resposta correta./);
  assert.doesNotMatch(render("QuestionAlternatives", { ...props, response: "" }), /answer-feedback/);
  for (const [answerType, count, fallback] of [["ABCDE", 5, "Alternativa E"], ["ABCD", 4, "Alternativa D"], ["CE", 2, "Certo"]]) {
    const html = render("QuestionAlternatives", { ...props, response: "", question: { ...props.question, answerType, alternatives: [], alternativeBlocks: [] } });
    assert.equal((html.match(/role="radio"/g) || []).length, count);
    assert.match(html, new RegExp(fallback));
    if (answerType === "CE") assert.match(html, /Errado/);
  }
});

test("filtros e paginação mantêm opções e limites", () => {
  const filters = render("QuestionFilters", { query: "fração", school: "CMB", year: "2003", subject: "", status: "", schools: ["CMB"], years: [2003], subjects: [], setQuery: noop, setSchool: noop, setYear: noop, setSubject: noop, setStatus: noop, setPage: noop, clearFilters: noop });
  assert.match(filters, /value="fração"/);
  assert.match(filters, /Autenticadas/);
  assert.doesNotMatch(filters, /Formato/);
  assert.equal(render("QuestionsPagination", { currentPage: 1, pageCount: 1, setPage: noop }), "");
  assert.match(render("QuestionsPagination", { currentPage: 1, pageCount: 2, setPage: noop }), /<button disabled="">Anterior/);
  assert.match(render("QuestionsPagination", { currentPage: 2, pageCount: 2, setPage: noop }), /<button disabled="">Próxima/);
});

test("compositor e impressão preservam seleção completa e gabarito independente", () => {
  const selected = fixture.simulation.expectedOrder.map((id) => normalizeQuestionContent(catalog.find((q) => q.id === id)));
  const props = { selected, simulationTitle: fixture.simulation.title, onTitleChange: noop, onRemove: noop, onClear: noop };
  assert.match(render("SimulationComposer", { ...props, selected: [] }), /class="generate-button" disabled=""/);
  assert.match(render("SimulationComposer", props), /Remover todas/);
  const many = Array.from({ length: 10 }, (_, index) => ({ ...selected[0], id: `memory-${index}` }));
  const summary = render("SimulationComposer", { ...props, selected: many });
  assert.equal((summary.match(/aria-label="Remover questão/g) || []).length, 8);
  assert.match(summary, /\+ 2 questões selecionadas/);
  const print = render("SimulationPrintSheet", props);
  assert.equal((print.match(/<article>/g) || []).length, 6);
  assert.equal((print.match(/<li>/g) || []).length, 30);
  assert.equal((print.match(/<img /g) || []).length, 8);
  assert.match(print, /class="answer-key"/);
  for (const [index, answer] of fixture.simulation.expectedAnswers.entries()) assert.ok(print.includes(`${index + 1}. <strong>${answer}</strong>`));
  assert.equal((render("SimulationPrintSheet", { ...props, selected: many }).match(/<article>/g) || []).length, 10);
});
