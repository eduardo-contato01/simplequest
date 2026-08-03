"use client";

import { useEffect, useMemo, useState } from "react";
import { loadQuestionCatalog, type ChoiceMode, type Question } from "./question-model";

const CHOICE_OPTIONS: Record<ChoiceMode, string[]> = {
  ABCDE: ["A", "B", "C", "D", "E"],
  ABCD: ["A", "B", "C", "D"],
  CE: ["C", "E"],
};

const PAGE_SIZE = 10;

function normalize(value: string) {
  return value
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase();
}

function splitQuestionContent(content: string, mode: ChoiceMode) {
  const lines = content.split(/\r?\n/).map((line) => line.trim()).filter(Boolean);

  if (mode === "CE") {
    return { stem: lines.join("\n"), alternatives: ["Certo", "Errado"] };
  }

  const optionCount = CHOICE_OPTIONS[mode].length;
  if (lines.length <= optionCount) {
    return { stem: lines.join("\n"), alternatives: CHOICE_OPTIONS[mode].map((option) => `Alternativa ${option}`) };
  }

  return {
    stem: lines.slice(0, -optionCount).join("\n"),
    alternatives: lines.slice(-optionCount).map((line) => line.replace(/^[A-E]\s*[).:\-–—]\s*/i, "")),
  };
}

export default function Home() {
  const [questions, setQuestions] = useState<Question[]>([]);
  const [loading, setLoading] = useState(true);
  const [query, setQuery] = useState("");
  const [school, setSchool] = useState("");
  const [year, setYear] = useState("");
  const [subject, setSubject] = useState("");
  const [status, setStatus] = useState("");
  const [sort, setSort] = useState("recent");
  const [page, setPage] = useState(1);
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
  const [expanded, setExpanded] = useState<string | null>(null);
  const [revealed, setRevealed] = useState<Set<string>>(new Set());
  const [responses, setResponses] = useState<Record<string, string>>({});
  const [choiceModes, setChoiceModes] = useState<Record<string, ChoiceMode>>({});
  const [simulationTitle, setSimulationTitle] = useState("Simulado de Matemática — 6º ano");

  useEffect(() => {
    loadQuestionCatalog()
      .then(setQuestions)
      .finally(() => setLoading(false));
  }, []);

  const schools = useMemo(
    () => [...new Set(questions.map((question) => question.school))].sort(),
    [questions],
  );
  const years = useMemo(
    () => [...new Set(questions.map((question) => question.year))].sort((a, b) => b - a),
    [questions],
  );
  const subjects = useMemo(
    () => [...new Set(questions.flatMap((question) => question.subjects))].sort((a, b) => a.localeCompare(b)),
    [questions],
  );

  const filtered = useMemo(() => {
    const needle = normalize(query.trim());
    const result = questions.filter((question) => {
      const searchable = normalize(
        `${question.school} ${question.year} ${question.number} ${question.subjects.join(" ")} ${question.content}`,
      );
      return (
        (!needle || searchable.includes(needle)) &&
        (!school || question.school === school) &&
        (!year || question.year === Number(year)) &&
        (!subject || question.subjects.includes(subject)) &&
        (!status || question.status === status)
      );
    });
    return result.sort((a, b) => {
      if (sort === "oldest") return a.year - b.year || a.number - b.number;
      if (sort === "school") return a.school.localeCompare(b.school) || b.year - a.year || a.number - b.number;
      return b.year - a.year || a.school.localeCompare(b.school) || a.number - b.number;
    });
  }, [questions, query, school, year, subject, status, sort]);

  useEffect(() => setPage(1), [query, school, year, subject, status, sort]);

  const pageCount = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
  const visible = filtered.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);
  const selected = questions.filter((question) => selectedIds.has(question.id));

  function toggleSelected(id: string) {
    setSelectedIds((current) => {
      const next = new Set(current);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  }

  function toggleAnswer(id: string) {
    setRevealed((current) => {
      const next = new Set(current);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  }

  function markResponse(id: string, option: string) {
    setResponses((current) => ({
      ...current,
      [id]: current[id] === option ? "" : option,
    }));
  }

  function changeChoiceMode(id: string, mode: ChoiceMode) {
    setChoiceModes((current) => ({ ...current, [id]: mode }));
    setResponses((current) => ({ ...current, [id]: "" }));
  }

  function clearFilters() {
    setQuery("");
    setSchool("");
    setYear("");
    setSubject("");
    setStatus("");
  }

  return (
    <>
      <div className="app-shell">
        <header className="topbar">
          <a className="brand" href="#top" aria-label="SimpleQuest — início">
            <span className="brand-mark">SQ</span>
            <span><strong>SimpleQuest</strong><small>Banco de questões</small></span>
          </a>
          <nav aria-label="Navegação principal">
            <a className="nav-active" href="#questoes">Questões</a>
            <a href="#simulado">Simulado <span className="nav-count">{selected.length}</span></a>
            <a href="/revisao">Revisão</a>
          </nav>
          <div className="top-actions">
            <span className="sync-state"><i /> Acervo importado</span>
            <button className="avatar" aria-label="Perfil do professor">PR</button>
          </div>
        </header>

        <main id="top">
          <section className="hero" aria-labelledby="hero-title">
            <div>
              <span className="eyebrow">MATEMÁTICA · 6º ANO</span>
              <h1 id="hero-title">Encontre a questão certa.<br />Monte a prova em minutos.</h1>
              <p>O acervo que antes vivia em planilhas e documentos agora pode ser pesquisado, selecionado e diagramado em um só lugar.</p>
            </div>
            <div className="hero-metrics" aria-label="Resumo do acervo">
              <article><strong>1.217</strong><span>questões recuperadas</span></article>
              <article><strong>9</strong><span>fontes de prova</span></article>
              <article><strong>2003–2024</strong><span>período coberto</span></article>
            </div>
          </section>

          <section className="workspace" id="questoes">
            <div className="search-panel">
              <div className="search-row">
                <label className="search-box">
                  <span aria-hidden="true">⌕</span>
                  <input
                    value={query}
                    onChange={(event) => setQuery(event.target.value)}
                    placeholder="Busque por palavra, assunto ou número da questão"
                    aria-label="Pesquisar questões"
                  />
                  <kbd>Ctrl K</kbd>
                </label>
                <button className="primary-button" onClick={() => setPage(1)}>Pesquisar</button>
              </div>
              <div className="filters" aria-label="Filtros da pesquisa">
                <label><span>Prova</span><select value={school} onChange={(e) => setSchool(e.target.value)}><option value="">Todas</option>{schools.map((item) => <option key={item}>{item}</option>)}</select></label>
                <label><span>Ano</span><select value={year} onChange={(e) => setYear(e.target.value)}><option value="">Todos</option>{years.map((item) => <option key={item}>{item}</option>)}</select></label>
                <label className="subject-filter"><span>Assunto</span><select value={subject} onChange={(e) => setSubject(e.target.value)}><option value="">Todos os assuntos</option>{subjects.map((item) => <option key={item}>{item}</option>)}</select></label>
                <label><span>Conteúdo</span><select value={status} onChange={(e) => setStatus(e.target.value)}><option value="">Todos</option><option value="ready">Texto simples</option><option value="review">Com mídia/fórmula</option></select></label>
                <button className="clear-button" onClick={clearFilters}>Limpar filtros</button>
              </div>
            </div>

            <div className="content-grid">
              <section className="results" aria-live="polite">
                <div className="results-heading">
                  <div><span className="section-kicker">BANCO DE QUESTÕES</span><h2>{loading ? "Carregando acervo…" : `${filtered.length.toLocaleString("pt-BR")} questões encontradas`}</h2></div>
                  <label className="sort-control">Ordenar por <select value={sort} onChange={(e) => setSort(e.target.value)}><option value="recent">Mais recentes</option><option value="oldest">Mais antigas</option><option value="school">Prova</option></select></label>
                </div>

                <div className="question-list">
                  {visible.map((question) => {
                    const isSelected = selectedIds.has(question.id);
                    const isExpanded = expanded === question.id;
                    const choiceMode = choiceModes[question.id] || question.answerType || "ABCDE";
                    const response = responses[question.id] || "";
                    const questionParts = splitQuestionContent(question.content, choiceMode);
                    return (
                      <article className={`question-card ${isSelected ? "selected" : ""}`} key={question.id}>
                        <div className="card-topline">
                          <label className="select-question">
                            <input type="checkbox" checked={isSelected} onChange={() => toggleSelected(question.id)} />
                            <span aria-hidden="true" />
                            Adicionar
                          </label>
                          <div className="metadata">
                            <strong>{question.school}</strong><span>{question.year}</span><span>Questão {question.number}</span>
                          </div>
                          <span className={`quality ${question.status}`}>{question.status === "ready" ? "Texto importado" : "Mídia em revisão"}</span>
                        </div>
                        <div className="topic-row">
                          {question.subjects.length ? question.subjects.map((item) => <span key={item}>{item}</span>) : <span>Sem classificação</span>}
                        </div>
                        {isExpanded ? (
                          <div className="question-content expanded">
                            <div className="question-stem">{questionParts.stem || "Conteúdo pendente de conferência."}</div>
                            <div className="alternatives-heading">
                              <span>Selecione uma alternativa</span>
                              <label>
                                Formato
                                <select
                                  value={choiceMode}
                                  onChange={(event) => changeChoiceMode(question.id, event.target.value as ChoiceMode)}
                                  aria-label={`Formato das alternativas da questão ${question.number}`}
                                >
                                  <option value="ABCDE">A–E</option>
                                  <option value="ABCD">A–D</option>
                                  <option value="CE">Certo / Errado</option>
                                </select>
                              </label>
                            </div>
                            <div className="alternatives-list" role="group" aria-label={`Alternativas da questão ${question.number}`}>
                              {CHOICE_OPTIONS[choiceMode].map((option, optionIndex) => (
                                <button
                                  type="button"
                                  key={option}
                                  className={response === option ? "marked" : ""}
                                  aria-pressed={response === option}
                                  onClick={() => markResponse(question.id, option)}
                                >
                                  <strong>{option}</strong>
                                  <span>{questionParts.alternatives[optionIndex] || `Alternativa ${option}`}</span>
                                </button>
                              ))}
                            </div>
                            {response && <span className="answer-feedback">Resposta marcada: <strong>{choiceMode === "CE" ? (response === "C" ? "Certo" : "Errado") : response}</strong></span>}
                          </div>
                        ) : (
                          <div className="question-content">{question.preview || "Conteúdo pendente de conferência."}</div>
                        )}
                        {question.status === "review" && isExpanded && (
                          <p className="review-note">Esta questão contém {[
                            question.hasMedia && "imagem",
                            question.hasTable && "tabela",
                            question.hasMath && "fórmula",
                          ].filter(Boolean).join(", ")}. O texto já foi recuperado; os elementos visuais serão convertidos na próxima etapa.</p>
                        )}
                        <footer className="card-footer">
                          <button onClick={() => setExpanded(isExpanded ? null : question.id)}>{isExpanded ? "Recolher" : "Ver questão completa"}</button>
                          <button onClick={() => toggleAnswer(question.id)}>{revealed.has(question.id) ? `Gabarito: ${question.answer || "—"}` : "Mostrar gabarito"}</button>
                          <span>Fonte: {question.sourceDocument}</span>
                        </footer>
                      </article>
                    );
                  })}
                  {!loading && !visible.length && <div className="empty-state"><strong>Nenhuma questão encontrada</strong><p>Tente retirar um filtro ou pesquisar por outro termo.</p></div>}
                </div>

                {filtered.length > PAGE_SIZE && (
                  <nav className="pagination" aria-label="Paginação das questões">
                    <button disabled={page === 1} onClick={() => setPage((value) => value - 1)}>Anterior</button>
                    <span>Página <strong>{page}</strong> de {pageCount}</span>
                    <button disabled={page === pageCount} onClick={() => setPage((value) => value + 1)}>Próxima</button>
                  </nav>
                )}
              </section>

              <aside className="simulation-panel" id="simulado">
                <div className="panel-title"><span>SIMULADO ATUAL</span><strong>{selected.length}</strong></div>
                <input className="simulation-name" value={simulationTitle} onChange={(e) => setSimulationTitle(e.target.value)} aria-label="Título do simulado" />
                {selected.length ? (
                  <ol className="selected-list">
                    {selected.slice(0, 8).map((question) => (
                      <li key={question.id}><span>{question.school} · {question.year} · Q{question.number}</span><button onClick={() => toggleSelected(question.id)} aria-label={`Remover questão ${question.number}`}>×</button></li>
                    ))}
                    {selected.length > 8 && <li className="more-items">+ {selected.length - 8} questões selecionadas</li>}
                  </ol>
                ) : (
                  <div className="panel-empty"><span>＋</span><strong>Seu simulado começa aqui</strong><p>Adicione questões à esquerda para montar a prova.</p></div>
                )}
                <div className="panel-summary"><span>Questões <strong>{selected.length}</strong></span><span>Gabarito <strong>incluído</strong></span></div>
                <button className="generate-button" disabled={!selected.length} onClick={() => window.print()}>Gerar simulado / PDF</button>
                {!!selected.length && <button className="remove-all" onClick={() => setSelectedIds(new Set())}>Remover todas</button>}
                <p className="panel-tip">A impressão gera a versão do aluno e uma página separada com o gabarito.</p>
              </aside>
            </div>
          </section>

          <section className="migration-note">
            <span>PRÓXIMA ETAPA</span>
            <div><h2>O acervo continua crescendo sem trabalho duplicado.</h2><p>Há 1.253 registros catalogados sem conteúdo vinculado. Eles entrarão numa fila de importação assistida, junto às provas digitadas que ainda não possuem indicadores.</p></div>
            <strong>1.253<br /><small>itens no backlog</small></strong>
          </section>
        </main>
      </div>

      <section className="print-sheet" aria-hidden="true">
        <header><h1>{simulationTitle}</h1><p>Nome: _______________________________________________ &nbsp; Data: ____/____/______</p></header>
        {selected.map((question, index) => (
          <article key={question.id}><h2>{index + 1}. <small>{question.school} · {question.year}</small></h2><div>{question.content}</div></article>
        ))}
        <div className="answer-key"><h1>Gabarito</h1>{selected.map((question, index) => <span key={question.id}>{index + 1}. <strong>{question.answer || "—"}</strong></span>)}</div>
      </section>
    </>
  );
}
