// Optional interaction checks, run by capture-print-baseline.mjs --verify-workspace.
// The parent harness intercepts every request and uses an isolated browser context.
import assert from "node:assert/strict";

export async function verifyWorkspace({ page, catalog, fixture }) {
  await page.emulateMedia({ media: "screen" });
  await page.goto("http://simplequest-baseline.test/");
  const ready = () => page.waitForFunction(() => /questões encontradas/.test(document.querySelector(".results-heading h2")?.textContent || ""));
  const stored = () => page.evaluate(() => JSON.parse(localStorage.getItem("simplequest:questions-view:v1")));
  const card = (number) => page.locator(".question-card").filter({ has: page.locator(".metadata span", { hasText: new RegExp(`^Questão ${number}$`) }) });
  const filterSelect = (name) => page.locator(".filters label").filter({ has: page.locator("span", { hasText: new RegExp("^" + name + "$", "u") }) }).locator("select");
  const filterYear = async (year) => {
    await filterSelect("Prova").selectOption("CMB");
    await filterSelect("Ano").selectOption(String(year));
  };
  await ready();
  console.log("Browser: catálogo carregado; verificando respostas e estado local.");

  await filterYear(2003);
  await page.locator(".sort-control select").selectOption("oldest");
  assert.equal(await page.locator(".question-card").count(), 10);
  await card(2).getByRole("button", { name: "Ver questão completa", exact: true }).click();
  assert.match(await card(2).locator(".quality").textContent(), /Autenticada · Admin/);
  const radios = card(2).getByRole("radio");
  await radios.nth(1).click();
  assert.equal(await radios.nth(1).getAttribute("aria-checked"), "true");
  assert.match(await card(2).locator(".answer-feedback").textContent(), /Resposta incorreta. Gabarito: A/);
  await radios.nth(1).press("Enter");
  assert.equal(await card(2).locator(".answer-feedback").count(), 0);
  await radios.nth(0).press("Space");
  assert.equal(await card(2).locator(".answer-feedback").textContent(), "Resposta correta.");
  await card(2).getByRole("button", { name: "Mostrar gabarito", exact: true }).click();
  assert.equal(await card(2).getByRole("button", { name: "Gabarito: A", exact: true }).count(), 1);
  await page.getByLabel("Título do simulado").fill("Título preservado no 1B");
  await page.evaluate(() => window.scrollTo(0, 650));
  await page.waitForFunction(() => JSON.parse(localStorage.getItem("simplequest:questions-view:v1")).scrollY > 500);
  const beforeReload = await stored();
  await page.reload();
  await ready();
  await page.waitForFunction(() => window.scrollY > 500);
  assert.equal(await page.getByLabel("Título do simulado").inputValue(), "Título preservado no 1B");
  assert.equal(await card(2).getByRole("radio").first().getAttribute("aria-checked"), "true");
  assert.equal(await card(2).getByRole("button", { name: "Gabarito: A", exact: true }).count(), 1);
  const afterReload = await stored();
  console.log("Browser: estado restaurado; verificando conteúdo rico e filtros.");
  for (const key of ["query", "school", "year", "subject", "status", "sort", "page", "expanded", "selectedIds", "revealed", "responses", "simulationTitle"]) assert.deepEqual(afterReload[key], beforeReload[key], key);

  await card(1).getByRole("button", { name: "Ver questão completa", exact: true }).click();
  assert.equal(await card(1).locator(".math-formula").count(), 1);
  assert.equal(await card(2).locator(".alternatives-list").count(), 0);
  await card(4).getByRole("button", { name: "Ver questão completa", exact: true }).click();
  assert.equal(await card(4).locator(".inline-math").count(), 1);
  await page.getByRole("button", { name: "Próxima", exact: true }).click();
  assert.match(await page.locator(".pagination").textContent(), /Página 2 de/);
  await card(11).getByRole("button", { name: "Ver questão completa", exact: true }).click();
  assert.equal(await card(11).locator(".question-content img").count(), 2);
  await card(11).getByRole("button", { name: "Ampliar Ilustração da questão 11" }).first().click();
  assert.equal(await page.getByRole("dialog").count(), 1);
  await page.keyboard.press("Escape");
  assert.equal(await page.getByRole("dialog").count(), 0);

  await filterYear(2008);
  await page.getByRole("button", { name: "Próxima", exact: true }).click();
  await card(13).getByRole("button", { name: "Ver questão completa", exact: true }).click();
  assert.equal(await card(13).locator("table td").count(), 5);
  await filterYear(2014);
  await page.getByRole("button", { name: "Próxima", exact: true }).click();
  await card(15).getByRole("button", { name: "Ver questão completa", exact: true }).click();
  assert.equal(await card(15).getByRole("radio").locator("img").count(), 5);
  await card(15).getByRole("radio").first().getByRole("button").click();
  assert.equal(await page.getByRole("dialog").count(), 1);
  assert.equal(await card(15).locator(".answer-feedback").count(), 0, "abrir imagem não seleciona resposta");
  await page.keyboard.press("Escape");

  await page.getByRole("button", { name: "Limpar filtros", exact: true }).click();
  await page.getByLabel("Pesquisar questões").fill("Oribogonto");
  assert.equal(await page.locator(".question-card").count(), 1);
  assert.match(await page.locator(".metadata").textContent(), /Questão 4/);
  assert.equal(await page.locator(".selected-list li").count(), 6);
  await page.getByLabel("Pesquisar questões").fill("xyzsemresultado999");
  assert.match(await page.locator(".empty-state").textContent(), /Nenhuma questão encontrada/);
  await page.getByRole("button", { name: "Limpar filtros", exact: true }).click();
  await filterSelect("Conteúdo").selectOption("authenticated");
  assert.equal(await page.locator(".question-card .quality.authenticated").count(), 10);
  await page.getByRole("button", { name: "Limpar filtros", exact: true }).click();
  await filterSelect("Assunto").selectOption(catalog.find((q) => q.id === fixture.cases.text).subjects[0]);
  assert.ok(await page.locator(".question-card").count() > 0);
  await page.getByRole("button", { name: "Limpar filtros", exact: true }).click();

  await page.evaluate(() => { window.__printCalls = 0; window.print = () => { window.__printCalls++; }; });
  console.log("Browser: conteúdo e filtros verificados; verificando simulado e falhas recuperáveis.");
  await page.getByRole("button", { name: "Gerar simulado / PDF", exact: true }).click();
  assert.equal(await page.evaluate(() => window.__printCalls), 1);
  await page.getByRole("button", { name: "Remover questão 2", exact: true }).click();
  assert.equal(await page.locator(".selected-list li").count(), 5);
  await page.getByRole("button", { name: "Remover todas", exact: true }).click();
  assert.equal(await page.getByRole("button", { name: "Gerar simulado / PDF", exact: true }).isDisabled(), true);
  assert.equal(await page.locator(".print-sheet article").count(), 0);
  await filterYear(2003);
  await card(2).locator(".select-question").click();
  assert.equal(await card(2).getByRole("checkbox").isChecked(), true);
  assert.equal(await page.locator(".selected-list li").count(), 1);
  await card(2).getByRole("checkbox").press("Space");
  assert.equal(await card(2).getByRole("checkbox").isChecked(), false);
  assert.equal(await page.locator(".selected-list li").count(), 0);

  // New catalog states: base errors must be recoverable; revisions failure keeps base usable.
  await page.route("**/data/questions.json", (route) => route.fulfill({ status: 503, json: [] }));
  await page.reload();
  await page.getByRole("alert").waitFor();
  assert.equal(await page.locator(".question-card").count(), 0);
  assert.equal(await page.getByText("Nenhuma questão encontrada", { exact: true }).count(), 0);
  await page.unroute("**/data/questions.json");
  await page.getByRole("button", { name: "Tentar novamente", exact: true }).click();
  await ready();
  await page.route("**/api/questions/revisions", (route) => route.fulfill({ status: 503, json: {} }));
  await page.reload();
  await page.getByText("Revisões indisponíveis.", { exact: false }).waitFor();
  assert.ok(await page.locator(".question-card").count() > 0);
  await page.unroute("**/api/questions/revisions");
  await page.getByRole("button", { name: "Tentar novamente", exact: true }).click();
  await ready();
  assert.equal(await page.getByText("Revisões indisponíveis.", { exact: false }).count(), 0);

  let releaseBase;
  let baseIntercepted;
  const pendingBase = new Promise((resolve) => { baseIntercepted = resolve; });
  await page.route("**/data/questions.json", async (route) => {
    await new Promise((resolve) => { releaseBase = resolve; baseIntercepted(); });
    await route.fulfill({ json: catalog });
  });
  await page.reload({ waitUntil: "domcontentloaded" });
  await page.getByText("Carregando acervo…", { exact: true }).waitFor();
  await pendingBase;
  releaseBase();
  await ready();
  await page.unroute("**/data/questions.json");
  return { contentCases: 7, responsesAndKeyboard: true, mediaPropagation: true, filtersAndPagination: true, localStateAndScroll: true, selectionAndPrint: true, catalogStatesAndRetry: true };
}
