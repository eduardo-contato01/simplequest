import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";
import {
  loadQuestionCatalog,
  loadQuestionCatalogWithStatus,
  mergeQuestionCatalog,
  normalizeQuestionContent,
  visibleQuestionContentBlocks,
} from "../app/question-model.ts";

const catalog = JSON.parse(await readFile(new URL("../public/data/questions.json", import.meta.url), "utf8"));
const { cases } = JSON.parse(await readFile(new URL("./fixtures/baseline-cases.json", import.meta.url), "utf8"));
const example = (name) => {
  const question = catalog.find(({ id }) => id === cases[name]);
  assert.ok(question, `Exemplo ausente: ${name} (${cases[name]})`);
  return normalizeQuestionContent(question);
};

test("os exemplos reais mantêm os contratos de conteúdo e bloqueio", () => {
  const text = example("text");
  assert.ok([...visibleQuestionContentBlocks(text), ...text.alternativeBlocks.flat()].every(({ type }) => type === "text"));
  const inline = visibleQuestionContentBlocks(example("inlineMath")).filter(({ type }) => type === "formula");
  assert.deepEqual(inline.map(({ latex, display }) => ({ latex, display })), [{ latex: "\\frac{3}{28}", display: "inline" }]);
  const block = visibleQuestionContentBlocks(example("blockFormula")).filter(({ type }) => type === "formula");
  assert.equal(block.length, 1);
  assert.equal(block[0].display, "block");
  const table = visibleQuestionContentBlocks(example("table")).find(({ type }) => type === "table");
  assert.equal(table.data, "F = 80794 | G = 16832 | H = 49698 | I = 83160 | J = 24840");
  assert.equal(table.hasHeader, false);
  assert.deepEqual(visibleQuestionContentBlocks(example("image")).filter(({ type }) => type === "image").flatMap(({ urls }) => urls), [
    "/question-media/cmb-2003-11_1.webp", "/question-media/cmb-2003-11_2.webp",
  ]);
  const alternatives = example("alternativeImage").alternativeBlocks;
  assert.equal(alternatives.length, 5);
  for (const blocks of alternatives) assert.ok(blocks.some(({ type, urls }) => type === "image" && urls.length));
  const locked = example("locked");
  assert.equal(locked.isLocked, true);
  assert.ok(locked.authenticatedAt);
  assert.ok(locked.auditTrail.some(({ type }) => type === "authenticated"));
});

test("normalizar os exemplos preserva os registros de origem e é idempotente", () => {
  const source = Object.values(cases).map((id) => structuredClone(catalog.find((question) => question.id === id)));
  const before = structuredClone(source);
  const normalized = source.map(normalizeQuestionContent);
  assert.deepEqual(source, before);
  assert.deepEqual(normalized.map(normalizeQuestionContent), normalized);
});

test("revisões prevalecem por ID sem reordenar a base ou alterar os argumentos", () => {
  const base = [example("text"), example("inlineMath")];
  const revision = { id: base[0].id, answer: "B", isLocked: false };
  const custom = { ...example("table"), id: "contract-only-custom", isCustom: true };
  const before = structuredClone({ base, revision, custom });
  const merged = mergeQuestionCatalog(base, [revision, custom]);
  assert.deepEqual(merged.map(({ id }) => id), [base[0].id, base[1].id, custom.id]);
  assert.equal(merged[0].answer, "B");
  assert.equal(merged[0].isLocked, false);
  assert.equal(merged[0].school, base[0].school);
  assert.deepEqual({ base, revision, custom }, before);
});

test("carregamento mescla revisões e mantém o fallback quando elas estão indisponíveis", async (t) => {
  const base = [catalog.find(({ id }) => id === cases.inlineMath)];
  const scenarios = [
    { name: "revisão disponível", response: () => Response.json({ questions: [{ id: base[0].id, answer: "A" }] }), answer: "A" },
    { name: "revisões vazias", response: () => Response.json({}), answer: base[0].answer },
    { name: "erro HTTP", response: () => new Response(null, { status: 503 }), answer: base[0].answer },
    { name: "falha de rede", response: () => { throw new Error("offline"); }, answer: base[0].answer },
    { name: "JSON inválido", response: () => new Response("invalid json"), answer: base[0].answer },
  ];
  for (const scenario of scenarios) {
    await t.test(scenario.name, async (t) => {
      const calls = [];
      t.mock.method(globalThis, "fetch", async (url) => {
        calls.push(url);
        return url === "/data/questions.json" ? Response.json(base) : scenario.response();
      });
      const result = await loadQuestionCatalog();
      assert.deepEqual(calls, ["/data/questions.json", "/api/questions/revisions"]);
      assert.deepEqual(result, [normalizeQuestionContent({ ...base[0], answer: scenario.answer })]);
    });
  }
});

test("falha ao carregar a base continua sendo propagada", async (t) => {
  t.mock.method(globalThis, "fetch", async () => { throw new Error("base indisponível"); });
  await assert.rejects(loadQuestionCatalog, /base indisponível/);
});

test("o carregamento distingue catálogo completo de fallback sem mudar os dados", async (t) => {
  const base = [example("inlineMath")];
  for (const available of [true, false]) {
    await t.test(available ? "completo" : "revisões indisponíveis", async (t) => {
      t.mock.method(globalThis, "fetch", async (url) => url === "/data/questions.json"
        ? Response.json(base)
        : available ? Response.json({ questions: [] }) : new Response(null, { status: 503 }));
      const result = await loadQuestionCatalogWithStatus();
      assert.equal(result.status, available ? "available" : "revisions-unavailable");
      assert.deepEqual(result.questions, base);
    });
  }
});

test("erro HTTP ou formato inválido da base não é confundido com catálogo vazio", async (t) => {
  for (const response of [() => Response.json([], { status: 500 }), () => Response.json({ error: "invalid" }), () => new Response("invalid json")]) {
    await t.test("base inválida", async (t) => {
      const fetch = t.mock.method(globalThis, "fetch", async () => response());
      await assert.rejects(loadQuestionCatalogWithStatus);
      assert.equal(fetch.mock.callCount(), 1);
    });
  }
});
