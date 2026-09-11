import assert from "node:assert/strict";
import test from "node:test";
import { normalizeSearchText, searchRelevance } from "../app/search-utils.ts";

const sample = "Professores trabalham porcentagem, fração e mínimo múltiplo comum no CMB 2007.";

test("normaliza acentos, pontuação e caixa", () => {
  assert.equal(normalizeSearchText("  FRAÇÃO — Matemática! "), "fracao matematica");
});

test("encontra erros ortográficos pequenos e letras invertidas", () => {
  assert.notEqual(searchRelevance("profesores", sample), null);
  assert.notEqual(searchRelevance("porcentagen", sample), null);
  assert.notEqual(searchRelevance("geomteria", "Questão de geometria"), null);
});

test("reconhece sinônimos pedagógicos cadastrados", () => {
  assert.notEqual(searchRelevance("percentagem", sample), null);
  assert.notEqual(searchRelevance("MMC", sample), null);
});

test("mantém siglas e números curtos estritos", () => {
  assert.equal(searchRelevance("CMB 2008", sample), null);
  assert.equal(searchRelevance("CMC", sample), null);
});

test("prioriza frase literal antes de palavras aproximadas", () => {
  assert.ok(searchRelevance("professores", sample) < searchRelevance("profesores", sample));
});
