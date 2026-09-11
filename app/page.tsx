"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { ANSWER_OPTIONS, defaultAlternativeText, loadQuestionCatalog, structureQuestion, type Question } from "./question-model";
import { QuestionBlocks } from "./components/QuestionBlocks";
import { searchRelevance } from "./search-utils";

const PAGE_SIZE = 10;
const QUESTIONS_VIEW_KEY = "simplequest:questions-view:v1";

type QuestionsViewState = {
  query?: string;
  school?: string;
  year?: string;
  subject?: string;
  status?: string;
  sort?: string;
  page?: number;
  expanded?: string | null;
  selectedIds?: string[];
  revealed?: string[];
  responses?: Record<string, string>;
  simulationTitle?: string;
  scrollY?: number;
};

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
  const [simulationTitle, setSimulationTitle] = useState("Simulado de Matemática — 6º ano");
  const [viewStateReady, setViewStateReady] = useState(false);
  const restoredScrollRef = useRef(0);

  useEffect(() => {
    try {
      const cached = JSON.parse(localStorage.getItem(QUESTIONS_VIEW_KEY) || "{}") as QuestionsViewState;
      queueMicrotask(() => {
        setQuery(cached.query || "");
        setSchool(cached.school || "");
        setYear(cached.year || "");
        setSubject(cached.subject || "");
        setStatus(cached.status || "");
        setSort(cached.sort || "recent");
        setPage(Math.max(1, Number(cached.page) || 1));
        setExpanded(cached.expanded || null);
        setSelectedIds(new Set(cached.selectedIds || []));
        setRevealed(new Set(cached.revealed || []));
        setResponses(cached.responses || {});
        setSimulationTitle(cached.simulationTitle || "Simulado de Matemática — 6º ano");
      });
      restoredScrollRef.current = Math.max(0, Number(cached.scrollY) || 0);
    } catch {
      localStorage.removeItem(QUESTIONS_VIEW_KEY);
    }
    loadQuestionCatalog()
      .then(setQuestions)
      .finally(() => {
        setLoading(false);
        requestAnimationFrame(() => requestAnimationFrame(() => {
          window.scrollTo({ top: restoredScrollRef.current });
          setViewStateReady(true);
        }));
      });
  }, []);

  useEffect(() => {
    if (!viewStateReady) return;
    const persist = () => localStorage.setItem(QUESTIONS_VIEW_KEY, JSON.stringify({
      query, school, year, subject, status, sort, page, expanded,
      selectedIds: [...selectedIds],
      revealed: [...revealed],
      responses,
      simulationTitle,
      scrollY: window.scrollY,
    } satisfies QuestionsViewState));
    let frame = 0;
    const schedulePersist = () => {
      cancelAnimationFrame(frame);
      frame = requestAnimationFrame(persist);
    };
    persist();
    window.addEventListener("scroll", schedulePersist, { passive: true });
    return () => {
      window.removeEventListener("scroll", schedulePersist);
      cancelAnimationFrame(frame);
      persist();
    };
  }, [viewStateReady, query, school, year, subject, status, sort, page, expanded, selectedIds, revealed, responses, simulationTitle]);

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
    const result = questions.flatMap((question) => {
      if (
        (school && question.school !== school)
        || (year && question.year !== Number(year))
        || (subject && !question.subjects.includes(subject))
        || (status && (status === "authenticated" ? !question.isLocked || !question.authenticatedAt : question.status !== status))
      ) return [];

      const relevance = searchRelevance(
        query,
        `${question.school} ${question.year} ${question.number} ${question.subjects.join(" ")} ${question.content} ${question.stem || ""} ${(question.alternatives || []).join(" ")}`,
      );
      return relevance === null ? [] : [{ question, relevance }];
    });

    return result.sort((left, right) => {
      if (left.relevance !== right.relevance) return left.relevance - right.relevance;
      const a = left.question;
      const b = right.question;
      if (sort === "oldest") return a.year - b.year || a.number - b.number;
      if (sort === "school") return a.school.localeCompare(b.school) || b.year - a.year || a.number - b.number;
      return b.year - a.year || a.school.localeCompare(b.school) || a.number - b.number;
    }).map(({ question }) => question);
  }, [questions, query, school, year, subject, status, sort]);

  const pageCount = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
  const currentPage = Math.min(page, pageCount);
  const visible = filtered.slice((currentPage - 1) * PAGE_SIZE, currentPage * PAGE_SIZE);
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

  function clearFilters() {
    setQuery("");
    setSchool("");
    setYear("");
    setSubject("");
    setStatus("");
    setPage(1);
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
                    onChange={(event) => { setQuery(event.target.value); setPage(1); }}
                    placeholder="Busque por palavra, assunto ou número da questão"
                    aria-label="Pesquisar questões"
                  />
                  <kbd>Ctrl K</kbd>
                </label>
                <button className="primary-button" onClick={() => setPage(1)}>Pesquisar</button>
              </div>
              <div className="filters" aria-label="Filtros da pesquisa">
                <label><span>Prova</span><select value={school} onChange={(e) => { setSchool(e.target.value); setPage(1); }}><option value="">Todas</option>{schools.map((item) => <option key={item}>{item}</option>)}</select></label>
                <label><span>Ano</span><select value={year} onChange={(e) => { setYear(e.target.value); setPage(1); }}><option value="">Todos</option>{years.map((item) => <option key={item}>{item}</option>)}</select></label>
                <label className="subject-filter"><span>Assunto</span><select value={subject} onChange={(e) => { setSubject(e.target.value); setPage(1); }}><option value="">Todos os assuntos</option>{subjects.map((item) => <option key={item}>{item}</option>)}</select></label>
                <label><span>Conteúdo</span><select value={status} onChange={(e) => { setStatus(e.target.value); setPage(1); }}><option value="">Todos</option><option value="authenticated">Autenticadas</option><option value="ready">Texto importado</option><option value="review">Em revisão</option></select></label>
                <button className="clear-button" onClick={clearFilters}>Limpar filtros</button>
              </div>
            </div>

            <div className="content-grid">
              <section className="results" aria-live="polite">
                <div className="results-heading">
                  <div><span className="section-kicker">BANCO DE QUESTÕES</span><h2>{loading ? "Carregando acervo…" : `${filtered.length.toLocaleString("pt-BR")} questões encontradas`}</h2></div>
                  <label className="sort-control">Ordenar por <select value={sort} onChange={(e) => { setSort(e.target.value); setPage(1); }}><option value="recent">Mais recentes</option><option value="oldest">Mais antigas</option><option value="school">Prova</option></select></label>
                </div>

                <div className="question-list">
                  {visible.map((question) => {
                    const isSelected = selectedIds.has(question.id);
                    const isExpanded = expanded === question.id;
                    const choiceMode = question.answerType || "ABCDE";
                    const response = responses[question.id] || "";
                    const questionParts = structureQuestion(question);
                    const officialAnswer = question.answer.trim().toUpperCase();
                    const isAuthenticated = Boolean(question.isLocked && question.authenticatedAt);
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
                          <span className={`quality ${isAuthenticated ? "authenticated" : question.status}`}>{isAuthenticated ? "Autenticada · Admin 🔒" : question.status === "ready" ? "Texto importado" : "Mídia em revisão"}</span>
                        </div>
                        <div className="topic-row">
                          {question.subjects.length ? question.subjects.map((item) => <span key={item}>{item}</span>) : <span>Sem classificação</span>}
                        </div>
                        {isExpanded ? (
                          <div className="question-content expanded">
                            <div className="question-blocks">
                              <QuestionBlocks question={question} />
                              <section className="question-section alternatives-section">
                                <div className="alternatives-heading"><span>Selecione uma alternativa</span></div>
                                <div className="alternatives-list" role="radiogroup" aria-label={`Alternativas da questão ${question.number}`}>
                                  {ANSWER_OPTIONS[choiceMode].map((option, optionIndex) => {
                                    const stateClass = response ? (option === officialAnswer ? "correct" : option === response ? "incorrect" : "") : "";
                                    const selectAlternative = () => markResponse(question.id, option);
                                    return <div
                                      key={option}
                                      className={`alternative-option ${stateClass}`.trim()}
                                      role="radio"
                                      aria-checked={response === option}
                                      tabIndex={0}
                                      onClick={selectAlternative}
                                      onKeyDown={(event) => {
                                        if ((event.key === "Enter" || event.key === " ") && event.target === event.currentTarget) {
                                          event.preventDefault();
                                          selectAlternative();
                                        }
                                      }}
                                    ><strong>{option}</strong><div className="alternative-content">{question.alternativeBlocks?.[optionIndex]?.length ? <QuestionBlocks question={question} blocks={question.alternativeBlocks[optionIndex]} compact /> : questionParts.alternatives[optionIndex] || defaultAlternativeText(choiceMode, option)}</div></div>;
                                  })}
                                </div>
                                {response && <span className={`answer-feedback ${response === officialAnswer ? "correct" : "incorrect"}`}>{response === officialAnswer ? "Resposta correta." : `Resposta incorreta. Gabarito: ${officialAnswer || "—"}.`}</span>}
                              </section>
                            </div>
                          </div>
                        ) : (
                          <div className="question-content">{question.preview || "Conteúdo pendente de conferência."}</div>
                        )}
                        {question.status === "review" && isExpanded && (
                          <p className="review-note">Esta questão contém {[
                            question.hasMedia && "imagem",
                            question.hasTable && "tabela",
                            question.hasMath && "fórmula",
                          ].filter(Boolean).join(", ")}. Confira a ordem e a fidelidade desses elementos no painel de Revisão.</p>
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
                    <button disabled={currentPage === 1} onClick={() => setPage(currentPage - 1)}>Anterior</button>
                    <span>Página <strong>{currentPage}</strong> de {pageCount}</span>
                    <button disabled={currentPage === pageCount} onClick={() => setPage(currentPage + 1)}>Próxima</button>
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
        {selected.map((question, index) => {
          const parts = structureQuestion(question);
          const mode = question.answerType || "ABCDE";
          return (
            <article key={question.id}>
              <h2>{index + 1}. <small>{question.school} · {question.year}</small></h2>
              <div className="print-question-blocks">
                <QuestionBlocks question={question} print />
                <ol type="A">{ANSWER_OPTIONS[mode].map((option, alternativeIndex) => <li key={option}>{question.alternativeBlocks?.[alternativeIndex]?.length ? <QuestionBlocks question={question} blocks={question.alternativeBlocks[alternativeIndex]} print compact /> : parts.alternatives[alternativeIndex] || defaultAlternativeText(mode, option)}</li>)}</ol>
              </div>
            </article>
          );
        })}
        <div className="answer-key"><h1>Gabarito</h1>{selected.map((question, index) => <span key={question.id}>{index + 1}. <strong>{question.answer || "—"}</strong></span>)}</div>
      </section>
    </>
  );
}
