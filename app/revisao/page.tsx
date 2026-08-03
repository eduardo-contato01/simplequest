"use client";

import { useEffect, useMemo, useState } from "react";
import { mergeQuestionCatalog, type ChoiceMode, type Question, type QuestionStatus } from "../question-model";

type QueueFilter = "all" | QuestionStatus | "revised";

const emptyQuestion = (): Question => ({
  id: `manual-${Date.now()}`,
  sourceRow: 0,
  school: "",
  year: new Date().getFullYear(),
  number: 1,
  subjects: [],
  answer: "",
  answerType: "ABCDE",
  difficulty: "",
  content: "",
  preview: "",
  sourceDocument: "Cadastro manual",
  sourceBookmark: "",
  hasTable: false,
  hasMedia: false,
  hasMath: false,
  status: "review",
  isCustom: true,
});

export default function ReviewPage() {
  const [baseQuestions, setBaseQuestions] = useState<Question[]>([]);
  const [revisions, setRevisions] = useState<Question[]>([]);
  const [editing, setEditing] = useState<Question | null>(null);
  const [query, setQuery] = useState("");
  const [queueFilter, setQueueFilter] = useState<QueueFilter>("review");
  const [school, setSchool] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [dirty, setDirty] = useState(false);
  const [message, setMessage] = useState("");

  const questions = useMemo(() => mergeQuestionCatalog(baseQuestions, revisions), [baseQuestions, revisions]);
  const revisionIds = useMemo(() => new Set(revisions.map((question) => question.id)), [revisions]);
  const schools = useMemo(() => [...new Set(questions.map((question) => question.school).filter(Boolean))].sort(), [questions]);

  const filtered = useMemo(() => {
    const needle = query.trim().toLocaleLowerCase("pt-BR");
    return questions.filter((question) => {
      const searchable = `${question.school} ${question.year} ${question.number} ${question.subjects.join(" ")} ${question.content}`.toLocaleLowerCase("pt-BR");
      const matchesQueue = queueFilter === "all" || (queueFilter === "revised" ? revisionIds.has(question.id) : question.status === queueFilter);
      return matchesQueue && (!school || question.school === school) && (!needle || searchable.includes(needle));
    });
  }, [questions, query, queueFilter, school, revisionIds]);

  useEffect(() => {
    Promise.all([
      fetch("/data/questions.json").then((response) => response.json() as Promise<Question[]>),
      fetch("/api/questions/revisions").then(async (response) => response.ok ? ((await response.json()) as { questions: Question[] }).questions : []),
    ]).then(([base, saved]) => {
      setBaseQuestions(base);
      setRevisions(saved);
      const merged = mergeQuestionCatalog(base, saved);
      setEditing({ ...(merged.find((question) => question.status === "review") || merged[0]) });
    }).finally(() => setLoading(false));
  }, []);

  function chooseQuestion(question: Question) {
    setEditing({ ...question, subjects: [...question.subjects] });
    setDirty(false);
    setMessage("");
  }

  function update<K extends keyof Question>(field: K, value: Question[K]) {
    setEditing((current) => current ? { ...current, [field]: value } : current);
    setDirty(true);
    setMessage("");
  }

  async function saveQuestion(status?: QuestionStatus) {
    if (!editing) return;
    const payload = { ...editing, status: status || editing.status, preview: editing.content.slice(0, 480) };
    if (!payload.school.trim() || !payload.year || !payload.number || !payload.content.trim()) {
      setMessage("Preencha instituição, ano, número e enunciado.");
      return;
    }
    setSaving(true);
    setMessage("");
    try {
      const response = await fetch("/api/questions/revisions", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const result = (await response.json()) as { question?: Question; error?: string };
      if (!response.ok || !result.question) throw new Error(result.error || "Não foi possível salvar.");
      setRevisions((current) => [result.question!, ...current.filter((question) => question.id !== result.question!.id)]);
      setEditing({ ...result.question });
      setDirty(false);
      setMessage(status === "ready" ? "Questão revisada e marcada como pronta." : "Alterações salvas no acervo.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Não foi possível salvar.");
    } finally {
      setSaving(false);
    }
  }

  async function restoreOriginal() {
    if (!editing || !revisionIds.has(editing.id)) return;
    setSaving(true);
    try {
      const response = await fetch(`/api/questions/revisions?id=${encodeURIComponent(editing.id)}`, { method: "DELETE" });
      if (!response.ok) throw new Error("Não foi possível restaurar.");
      setRevisions((current) => current.filter((question) => question.id !== editing.id));
      const original = baseQuestions.find((question) => question.id === editing.id);
      if (original) setEditing({ ...original });
      else setEditing({ ...emptyQuestion() });
      setDirty(false);
      setMessage(original ? "Versão original restaurada." : "Cadastro removido.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Não foi possível restaurar.");
    } finally {
      setSaving(false);
    }
  }

  function createQuestion() {
    setEditing(emptyQuestion());
    setDirty(true);
    setMessage("");
  }

  function exportCatalog() {
    const blob = new Blob([JSON.stringify(questions, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `simplequest-acervo-${new Date().toISOString().slice(0, 10)}.json`;
    link.click();
    URL.revokeObjectURL(url);
  }

  const reviewedCount = revisionIds.size;
  const readyCount = questions.filter((question) => question.status === "ready").length;
  const pendingCount = questions.length - readyCount;

  return (
    <div className="review-app">
      <header className="topbar review-topbar">
        <a className="brand" href="/" aria-label="SimpleQuest — início">
          <span className="brand-mark">SQ</span>
          <span><strong>SimpleQuest</strong><small>Banco de questões</small></span>
        </a>
        <nav aria-label="Navegação principal">
          <a href="/">Questões</a>
          <a className="nav-active" href="/revisao">Revisão</a>
        </nav>
        <div className="review-header-actions">
          <button className="secondary-button" onClick={exportCatalog} disabled={!questions.length}>Exportar acervo</button>
          <button className="primary-button" onClick={createQuestion}>＋ Nova questão</button>
        </div>
      </header>

      <main className="review-main">
        <section className="review-intro">
          <div><span className="eyebrow">CURADORIA DO ACERVO</span><h1>Painel de revisão</h1><p>Corrija, classifique e prepare cada questão antes de liberá-la para os professores.</p></div>
          <div className="review-metrics">
            <article><strong>{questions.length.toLocaleString("pt-BR")}</strong><span>no acervo</span></article>
            <article><strong>{pendingCount.toLocaleString("pt-BR")}</strong><span>para revisar</span></article>
            <article><strong>{reviewedCount.toLocaleString("pt-BR")}</strong><span>alteradas</span></article>
          </div>
        </section>

        <section className="review-workspace">
          <aside className="review-queue">
            <div className="queue-title"><div><span>FILA DE QUESTÕES</span><strong>{filtered.length.toLocaleString("pt-BR")}</strong></div><small>{readyCount.toLocaleString("pt-BR")} prontas</small></div>
            <label className="queue-search"><span>⌕</span><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Buscar na fila" /></label>
            <div className="queue-filters">
              <select value={queueFilter} onChange={(event) => setQueueFilter(event.target.value as QueueFilter)} aria-label="Situação da revisão">
                <option value="review">Para revisar</option><option value="revised">Já alteradas</option><option value="ready">Prontas</option><option value="all">Todas</option>
              </select>
              <select value={school} onChange={(event) => setSchool(event.target.value)} aria-label="Filtrar instituição"><option value="">Todas as instituições</option>{schools.map((item) => <option key={item}>{item}</option>)}</select>
            </div>
            <div className="queue-list">
              {loading && <p className="queue-empty">Carregando acervo…</p>}
              {!loading && filtered.slice(0, 100).map((question) => (
                <button className={editing?.id === question.id ? "active" : ""} key={question.id} onClick={() => chooseQuestion(question)}>
                  <span className={`queue-status ${question.status}`} />
                  <span><strong>{question.school} · {question.year}</strong><small>Questão {question.number} · {question.subjects[0] || "Sem assunto"}</small></span>
                  {revisionIds.has(question.id) && <i>editada</i>}
                </button>
              ))}
              {!loading && !filtered.length && <p className="queue-empty">Nenhuma questão nesta fila.</p>}
              {filtered.length > 100 && <p className="queue-limit">Mostrando 100 de {filtered.length}. Use a busca para localizar outra questão.</p>}
            </div>
          </aside>

          <section className="review-editor">
            {editing ? (
              <>
                <div className="editor-heading">
                  <div><span>{editing.isCustom ? "CADASTRO MANUAL" : editing.sourceDocument}</span><h2>{editing.school || "Nova questão"} {editing.year ? `· ${editing.year}` : ""} {editing.number ? `· Questão ${editing.number}` : ""}</h2></div>
                  <span className={`editor-state ${editing.status}`}>{editing.status === "ready" ? "Pronta" : "Em revisão"}</span>
                </div>

                <div className="editor-grid">
                  <label><span>Instituição *</span><input value={editing.school} onChange={(event) => update("school", event.target.value)} placeholder="Ex.: CMB" /></label>
                  <label><span>Ano *</span><input type="number" value={editing.year} onChange={(event) => update("year", Number(event.target.value))} /></label>
                  <label><span>Número *</span><input type="number" value={editing.number} onChange={(event) => update("number", Number(event.target.value))} /></label>
                  <label><span>Formato</span><select value={editing.answerType || "ABCDE"} onChange={(event) => update("answerType", event.target.value as ChoiceMode)}><option value="ABCDE">A–E</option><option value="ABCD">A–D</option><option value="CE">Certo / Errado</option></select></label>
                  <label className="editor-subjects"><span>Assuntos</span><input value={editing.subjects.join(", ")} onChange={(event) => update("subjects", event.target.value.split(",").map((item) => item.trim()).filter(Boolean))} placeholder="Frações, Porcentagem" /></label>
                  <label><span>Gabarito</span><input className="answer-input" value={editing.answer} onChange={(event) => update("answer", event.target.value.toUpperCase().slice(0, 1))} placeholder="A" /></label>
                  <label><span>Dificuldade</span><select value={editing.difficulty} onChange={(event) => update("difficulty", event.target.value)}><option value="">Não definida</option><option value="Fácil">Fácil</option><option value="Média">Média</option><option value="Difícil">Difícil</option></select></label>
                </div>

                <label className="editor-content"><span>Enunciado e alternativas *</span><textarea value={editing.content} onChange={(event) => update("content", event.target.value)} rows={15} /><small>Mantenha cada alternativa em uma linha separada. As últimas linhas serão identificadas como alternativas na visualização completa.</small></label>

                <div className="editor-flags">
                  <span>Elementos que exigem conferência</span>
                  <label><input type="checkbox" checked={editing.hasMedia} onChange={(event) => update("hasMedia", event.target.checked)} /> Imagem ou gráfico</label>
                  <label><input type="checkbox" checked={editing.hasTable} onChange={(event) => update("hasTable", event.target.checked)} /> Tabela</label>
                  <label><input type="checkbox" checked={editing.hasMath} onChange={(event) => update("hasMath", event.target.checked)} /> Fórmula matemática</label>
                </div>

                <div className="editor-footer">
                  <div>{message && <p className="editor-message">{message}</p>}{dirty && !message && <p className="editor-unsaved">Há alterações ainda não salvas.</p>}</div>
                  {revisionIds.has(editing.id) && <button className="restore-button" onClick={restoreOriginal} disabled={saving}>{editing.isCustom ? "Excluir cadastro" : "Restaurar original"}</button>}
                  <button className="secondary-button" onClick={() => saveQuestion("review")} disabled={saving}>{saving ? "Salvando…" : "Salvar rascunho"}</button>
                  <button className="primary-button" onClick={() => saveQuestion("ready")} disabled={saving}>{saving ? "Salvando…" : "Salvar e marcar como pronta"}</button>
                </div>
              </>
            ) : <div className="editor-empty">Selecione uma questão para começar a revisão.</div>}
          </section>
        </section>
      </main>
    </div>
  );
}
