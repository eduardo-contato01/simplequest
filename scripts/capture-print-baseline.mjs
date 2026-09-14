// Optional browser verification: uses an existing Playwright installation/browser.
// All requests are fulfilled locally; no application API or D1 database is used.
import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { readFile, readdir, mkdir, writeFile } from "node:fs/promises";
import { createRequire } from "node:module";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { build } from "vite";

const root = fileURLToPath(new URL("../", import.meta.url));
const require = createRequire(import.meta.url);
const { chromium } = require(process.env.SIMPLEQUEST_PLAYWRIGHT_MODULE || "playwright");
const fixture = JSON.parse(await readFile(path.join(root, "tests/fixtures/baseline-cases.json"), "utf8"));
const catalogBytes = await readFile(path.join(root, "public/data/questions.json"));
const catalog = JSON.parse(catalogBytes);
const compareBaseline = process.argv.includes("--compare-baseline");
const output = path.join(root, compareBaseline ? "outputs/baseline-1b" : "outputs/baseline-1a");
const assets = path.join(root, "dist/client/assets");
const cssFiles = (await readdir(assets)).filter((name) => name.endsWith(".css"));
assert.ok(cssFiles.length, "Execute npm run build antes da captura.");
const css = (await Promise.all(cssFiles.map((name) => readFile(path.join(assets, name), "utf8")))).join("\n");
const entry = path.join(root, "baseline-capture-entry.mjs").replaceAll("\\", "/");
const bundle = await build({
  configFile: false, root, publicDir: false, logLevel: "error",
  plugins: [{
    name: "baseline-entry",
    resolveId(id) { if (id.replaceAll("\\", "/") === entry) return "\0" + entry; },
    load(id) {
      if (id === "\0" + entry) return `import { createRoot } from "react-dom/client"; import { createElement } from "react"; import Home from ${JSON.stringify(path.join(root, "app/page.tsx").replaceAll("\\", "/"))}; createRoot(document.getElementById("root")).render(createElement(Home));`;
    },
  }],
  build: { write: false, lib: { entry, formats: ["iife"], name: "Baseline" } },
  define: { "process.env.NODE_ENV": '"production"' },
});
const browser = await chromium.launch({
  ...(process.env.SIMPLEQUEST_BROWSER_EXECUTABLE ? { executablePath: process.env.SIMPLEQUEST_BROWSER_EXECUTABLE } : {}),
  headless: true,
});
try {
  const context = await browser.newContext({ viewport: { width: 794, height: 1123 }, deviceScaleFactor: 1 });
  const page = await context.newPage();
  page.setDefaultTimeout(10000);
  page.setDefaultNavigationTimeout(10000);
  const errors = [];
  const apiRequests = [];
  page.on("pageerror", (error) => errors.push(error.message));
  await context.addInitScript((simulation) => {
    if (localStorage.getItem("simplequest:questions-view:v1")) return;
    localStorage.setItem("simplequest:questions-view:v1", JSON.stringify({
      selectedIds: simulation.selectedIds, simulationTitle: simulation.title,
    }));
  }, fixture.simulation);
  const mime = { ".webp": "image/webp", ".woff2": "font/woff2", ".woff": "font/woff", ".ttf": "font/ttf" };
  await context.route("**/*", async (route) => {
    const url = new URL(route.request().url());
    if (url.origin !== "http://simplequest-baseline.test") throw new Error(`Requisição externa inesperada: ${url}`);
    if (url.pathname === "/") return route.fulfill({ contentType: "text/html", body: `<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><style>${css}</style></head><body><div id="root"></div><script src="/baseline.js"></script></body></html>` });
    if (url.pathname === "/baseline.js") return route.fulfill({ contentType: "text/javascript", body: bundle[0].output.find((item) => item.type === "chunk").code });
    if (url.pathname === "/data/questions.json") return route.fulfill({ contentType: "application/json", body: catalogBytes });
    if (url.pathname === "/api/questions/revisions") {
      apiRequests.push({ method: route.request().method(), path: url.pathname });
      return route.fulfill({ json: { questions: [] } });
    }
    if (/^\/(assets|question-media)\/[\w.-]+$/.test(url.pathname)) {
      const base = url.pathname.startsWith("/assets/") ? "dist/client" : "public";
      return route.fulfill({ contentType: mime[path.extname(url.pathname)] || "application/octet-stream", body: await readFile(path.join(root, base, url.pathname)) });
    }
    throw new Error(`Requisição local inesperada: ${url.pathname}`);
  });
  await page.goto("http://simplequest-baseline.test/");
  await page.waitForFunction(() => document.querySelectorAll(".print-sheet article").length === 6);
  assert.equal(await page.locator(".print-sheet").evaluate((element) => getComputedStyle(element).display), "none");
  const actualOrder = await page.locator(".selected-list li > span").allTextContents();
  const expectedLabels = fixture.simulation.expectedOrder.map((id) => {
    const q = catalog.find((question) => question.id === id);
    return `${q.school} · ${q.year} · Q${q.number}`;
  });
  assert.deepEqual(actualOrder, expectedLabels);
  assert.deepEqual(await page.locator(".answer-key span strong").allTextContents(), fixture.simulation.expectedAnswers);
  assert.deepEqual(await page.locator(".print-sheet article ol").evaluateAll((lists) => lists.map((list) => list.children.length)), [5, 5, 5, 5, 5, 5]);
  assert.equal(await page.locator(".print-sheet header h1").textContent(), fixture.simulation.title);
  await page.emulateMedia({ media: "print" });
  await page.waitForFunction(() => [...document.querySelectorAll(".print-sheet img")].every((image) => image.complete && image.naturalWidth > 0));
  await page.evaluate(() => document.fonts.ready);
  assert.equal(await page.locator(".app-shell").evaluate((element) => getComputedStyle(element).display), "none");
  assert.equal(await page.locator(".print-sheet article").nth(0).locator(".math-formula").count(), 1);
  assert.equal(await page.locator(".print-sheet article").nth(2).locator(".inline-math").count(), 1);
  assert.equal(await page.locator(".print-sheet table td").count(), 5);
  assert.equal(await page.locator(".print-sheet img").count(), 8);
  assert.equal(await page.locator(".print-sheet article").nth(5).locator("ol img").count(), 5);
  assert.equal(await page.locator(".answer-key").evaluate((element) => getComputedStyle(element).breakBefore), "page");
  assert.deepEqual(errors, []);
  assert.deepEqual(apiRequests, [{ method: "GET", path: "/api/questions/revisions" }]);

  // Freeze actual rendered DOM and compiled CSS with embedded assets, without JS.
  let frozenCss = css;
  for (const match of new Set(css.match(/\/assets\/[\w.-]+/g) || [])) {
    const bytes = await readFile(path.join(root, "dist/client", match));
    frozenCss = frozenCss.replaceAll(match, `data:${mime[path.extname(match)] || "application/octet-stream"};base64,${bytes.toString("base64")}`);
  }
  let markup = await page.locator(".print-sheet").evaluate((element) => element.outerHTML);
  for (const match of new Set(markup.match(/\/question-media\/[\w.-]+/g) || [])) {
    const bytes = await readFile(path.join(root, "public", match));
    markup = markup.replaceAll(match, `data:image/webp;base64,${bytes.toString("base64")}`);
  }
  const html = `<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><title>SimpleQuest — referência de impressão 1A</title><style>${frozenCss}</style></head><body>${markup}</body></html>`;
  await mkdir(output, { recursive: true });
  await writeFile(path.join(output, "print.html"), html);
  const originalPng = await page.locator(".print-sheet").screenshot();
  const listStyleType = await page.locator(".print-sheet ol").first().evaluate((element) => getComputedStyle(element).listStyleType);
  await page.setContent(html);
  await page.waitForFunction(() => [...document.querySelectorAll(".print-sheet img")].every((image) => image.complete && image.naturalWidth > 0));
  await page.evaluate(() => document.fonts.ready);
  const frozenPng = await page.locator(".print-sheet").screenshot({ path: path.join(output, "print.png") });
  assert.deepEqual(frozenPng, originalPng, "A referência autossuficiente deve renderizar como a folha original.");
  if (compareBaseline) {
    await page.setContent(await readFile(path.join(root, "docs/baseline-1a/print.html"), "utf8"));
    await page.waitForFunction(() => [...document.querySelectorAll(".print-sheet img")].every((image) => image.complete && image.naturalWidth > 0));
    await page.evaluate(() => document.fonts.ready);
    const baselinePng = await page.locator(".print-sheet").screenshot();
    assert.deepEqual(originalPng, baselinePng, "A impressão atual deve corresponder ao baseline congelado do 1A.");
  }
  const report = {
    capturedAt: new Date().toISOString(), browser: browser.version(),
    source: "Home e componentes reais, CSS do build; catálogo base com revisões vazias interceptadas, sem acesso ao D1",
    catalogSha256: createHash("sha256").update(catalogBytes).digest("hex"),
    htmlSha256: createHash("sha256").update(html).digest("hex"),
    records: fixture.simulation.expectedOrder.map((id) => ({
      id, sha256: createHash("sha256").update(JSON.stringify(catalog.find((question) => question.id === id))).digest("hex"),
    })),
    simulation: fixture.simulation, actualOrder, answers: fixture.simulation.expectedAnswers,
    articles: 6, alternativesPerArticle: 5, images: 8, tables: 1,
    listStyleType, standaloneMatchesOriginal: true,
    ...(compareBaseline ? { baseline1aMatchesOriginal: true } : {}),
    apiRequests, pageErrors: errors,
    note: "HTML preserva mídia screen/print original: fica oculto na tela normal; abrir a impressão para visualizar. PNG usa mídia print sem paginação física.",
  };
  if (process.argv.includes("--verify-workspace")) {
    const { verifyWorkspace } = await import("../tests/workspace-browser-checks.mjs");
    report.workspaceChecks = await verifyWorkspace({ page, catalog, fixture });
    assert.deepEqual(errors, []);
  }
  await writeFile(path.join(output, "capture.json"), JSON.stringify(report, null, 2) + "\n");
  console.log(JSON.stringify(report, null, 2));
} finally {
  await browser.close();
}
