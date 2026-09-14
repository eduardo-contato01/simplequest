"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import Link from "next/link";
import { ANSWER_OPTIONS, composeQuestionContent, contentBlocksPlainText, defaultAlternativeText, mergeQuestionCatalog, normalizeQuestionContent, questionContentBlocks, structureQuestion, type ChoiceMode, type Question, type QuestionAuditEvent, type QuestionContentBlock, type QuestionStatus, type TextAlignment } from "../question-model";
import { ContentBlocksEditor } from "../components/ContentBlocksEditor";
import { type TextFormat } from "../components/InlineMathEditor";
import { searchRelevance } from "../search-utils";

type QueueFilter = "all" | QuestionStatus | "revised" | "authenticated" | "unauthenticated";

const ADMINISTRATOR_NAME = "Administrador";
const REVIEW_VIEW_KEY = "simplequest:review-view:v1";

type ReviewViewState = {
  query?: string;
  queueFilter?: QueueFilter;
  school?: string;
  editingId?: string;
  scrollY?: number;
  queueScrollTop?: number;
};

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
  stem: "",
  alternatives: ANSWER_OPTIONS.ABCDE.map(() => ""),
  formula: "",
  tableData: "",
  imageUrls: [],
  contentBlocks: [{ id: "manual-text", type: "text", text: "" }],
  alternativeBlocks: ANSWER_OPTIONS.ABCDE.map((_, index) => [{ id: `manual-alternative-${index + 1}`, type: "text", text: "" }]),
  isLocked: false,
  auditTrail: [],
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
  const [showUnlock, setShowUnlock] = useState(false);
  const [unlockReason, setUnlockReason] = useState("");
  const [hasFormulaCursor, setHasFormulaCursor] = useState(false);
  const [activeTextFormats, setActiveTextFormats] = useState<TextFormat[]>([]);
  const [activeTextAlignment, setActiveTextAlignment] = useState<TextAlignment | null>(null);
  const [undoStack, setUndoStack] = useState<Question[]>([]);
  const [redoStack, setRedoStack] = useState<Question[]>([]);
  const formulaInsertionRef = useRef<(() => void) | null>(null);
  const textFormattingRef = useRef<((format: TextFormat) => void) | null>(null);
  const textAlignmentRef = useRef<((alignment: TextAlignment) => void) | null>(null);
  const queueListRef = useRef<HTMLDivElement>(null);
  const restoredWindowScrollRef = useRef(0);
  const restoredQueueScrollRef = useRef(0);
  const [viewStateReady, setViewStateReady] = useState(false);

  const questions = useMemo(() => mergeQuestionCatalog(baseQuestions, revisions), [baseQuestions, revisions]);
  const revisionIds = useMemo(() => new Set(revisions.map((question) => question.id)), [revisions]);
  const schools = useMemo(() => [...new Set(questions.map((question) => question.school).filter(Boolean))].sort(), [questions]);

  const filtered = useMemo(() => {
    return questions.flatMap((question) => {
      const matchesQueue = queueFilter === "all" || (queueFilter === "revised"
        ? revisionIds.has(question.id)
        : queueFilter === "authenticated"
          ? Boolean(question.isLocked && question.authenticatedAt)
          : queueFilter === "unauthenticated"
            ? !question.isLocked || !question.authenticatedAt
            : question.status === queueFilter);
      if (!matchesQueue || (school && question.school !== school)) return [];

      const relevance = searchRelevance(
        query,
        `${question.school} ${question.year} ${question.number} ${question.subjects.join(" ")} ${question.content} ${question.stem || ""} ${(question.alternatives || []).join(" ")}`,
      );
      return relevance === null ? [] : [{ question, relevance }];
    }).sort((left, right) => left.relevance - right.relevance)
      .map(({ question }) => question);
  }, [questions, query, queueFilter, school, revisionIds]);

  useEffect(() => {
    let preferredQuestionId = "";
    try {
      const cached = JSON.parse(localStorage.getItem(REVIEW_VIEW_KEY) || "{}") as ReviewViewState;
      queueMicrotask(() => {
        setQuery(cached.query || "");
        setQueueFilter(cached.queueFilter || "review");
        setSchool(cached.school || "");
      });
      preferredQuestionId = cached.editingId || "";
      restoredWindowScrollRef.current = Math.max(0, Number(cached.scrollY) || 0);
      restoredQueueScrollRef.current = Math.max(0, Number(cached.queueScrollTop) || 0);
    } catch {
      localStorage.removeItem(REVIEW_VIEW_KEY);
    }
    Promise.all([
      fetch("/data/questions.json").then((response) => response.json() as Promise<Question[]>),
      fetch("/api/questions/revisions").then(async (response) => response.ok ? ((await response.json()) as { questions: Question[] }).questions : []),
    ]).then(([base, saved]) => {
      setBaseQuestions(base);
      setRevisions(saved);
      const merged = mergeQuestionCatalog(base, saved);
      const first = merged.find((question) => question.id === preferredQuestionId) || merged.find((question) => question.status === "review") || merged[0];
      setEditing(first ? prepareForEditing(first) : null);
    }).finally(() => {
      setLoading(false);
      requestAnimationFrame(() => requestAnimationFrame(() => {
        window.scrollTo({ top: restoredWindowScrollRef.current });
        if (queueListRef.current) queueListRef.current.scrollTop = restoredQueueScrollRef.current;
        setViewStateReady(true);
      }));
    });
  }, []);

  useEffect(() => {
    if (!viewStateReady || loading) return;
    const persist = () => localStorage.setItem(REVIEW_VIEW_KEY, JSON.stringify({
      query,
      queueFilter,
      school,
      editingId: editing?.id || "",
      scrollY: window.scrollY,
      queueScrollTop: queueListRef.current?.scrollTop || 0,
    } satisfies ReviewViewState));
    let frame = 0;
    const schedulePersist = () => {
      cancelAnimationFrame(frame);
      frame = requestAnimationFrame(persist);
    };
    const queueList = queueListRef.current;
    persist();
    window.addEventListener("scroll", schedulePersist, { passive: true });
    queueList?.addEventListener("scroll", schedulePersist, { passive: true });
    return () => {
      window.removeEventListener("scroll", schedulePersist);
      queueList?.removeEventListener("scroll", schedulePersist);
      cancelAnimationFrame(frame);
      persist();
    };
  }, [viewStateReady, loading, query, queueFilter, school, editing?.id]);

  function chooseQuestion(question: Question) {
    setEditing({ ...prepareForEditing(question), subjects: [...question.subjects] });
    setDirty(false);
    setMessage("");
    setShowUnlock(false);
    setUnlockReason("");
    formulaInsertionRef.current = null;
    textFormattingRef.current = null;
    textAlignmentRef.current = null;
    setHasFormulaCursor(false);
    setActiveTextFormats([]);
    setActiveTextAlignment(null);
    setUndoStack([]);
    setRedoStack([]);
  }

  function commitEditing(next: Question) {
    if (!editing) return;
    setUndoStack((current) => [...current.slice(-199), structuredClone(editing)]);
    setRedoStack([]);
    setEditing(next);
    setDirty(true);
    setMessage("");
  }

  function undoEditing() {
    if (!editing || !undoStack.length) return;
    const previous = undoStack[undoStack.length - 1];
    setUndoStack((current) => current.slice(0, -1));
    setRedoStack((current) => [...current.slice(-199), structuredClone(editing)]);
    setEditing(structuredClone(previous));
    formulaInsertionRef.current = null;
    textFormattingRef.current = null;
    textAlignmentRef.current = null;
    setHasFormulaCursor(false);
    setActiveTextFormats([]);
    setActiveTextAlignment(null);
    setDirty(true);
    setMessage("Alteração desfeita.");
  }

  function redoEditing() {
    if (!editing || !redoStack.length) return;
    const next = redoStack[redoStack.length - 1];
    setRedoStack((current) => current.slice(0, -1));
    setUndoStack((current) => [...current.slice(-199), structuredClone(editing)]);
    setEditing(structuredClone(next));
    formulaInsertionRef.current = null;
    textFormattingRef.current = null;
    textAlignmentRef.current = null;
    setHasFormulaCursor(false);
    setActiveTextFormats([]);
    setActiveTextAlignment(null);
    setDirty(true);
    setMessage("Alteração refeita.");
  }

  function activateFormulaInsertion(insert: () => void) {
    formulaInsertionRef.current = insert;
    setHasFormulaCursor(true);
  }

  function activateTextFormatting(apply: (format: TextFormat) => void, activeFormats: TextFormat[]) {
    textFormattingRef.current = apply;
    setActiveTextFormats((current) => current.length === activeFormats.length && current.every((format) => activeFormats.includes(format)) ? current : activeFormats);
    setHasFormulaCursor(true);
  }

  function activateTextAlignment(apply: (alignment: TextAlignment) => void, activeAlignment: TextAlignment) {
    textAlignmentRef.current = apply;
    setActiveTextAlignment(activeAlignment);
    setHasFormulaCursor(true);
  }

  function applyTextFormatting(format: TextFormat) {
    if (!textFormattingRef.current) return;
    textFormattingRef.current(format);
    setActiveTextFormats((current) => current.includes(format) ? current.filter((item) => item !== format) : [...current, format]);
  }

  function applyTextAlignment(alignment: TextAlignment) {
    if (!textAlignmentRef.current) return;
    textAlignmentRef.current(alignment);
    setActiveTextAlignment(alignment);
  }

  function changeAnswerType(mode: ChoiceMode) {
    if (!editing) return;
    const current = editing.alternatives || [];
    const alternatives = ANSWER_OPTIONS[mode].map((option, index) => mode === "CE" ? defaultAlternativeText(mode, option) : current[index] || "");
    const alternativeBlocks = ANSWER_OPTIONS[mode].map((_, index) => mode !== "CE" && editing.alternativeBlocks?.[index]?.length ? editing.alternativeBlocks[index] : [{ id: `alternative-${index + 1}-text`, type: "text" as const, text: alternatives[index] }]);
    commitEditing({ ...editing, answerType: mode, alternatives, alternativeBlocks, ...contentFlags(questionContentBlocks(editing), alternativeBlocks) });
  }

  function updateAlternativeBlocks(index: number, blocks: QuestionContentBlock[]) {
    if (!editing) return;
    const groups = [...(editing.alternativeBlocks || ANSWER_OPTIONS[editing.answerType || "ABCDE"].map(() => []))];
    groups[index] = blocks;
    const alternatives = [...(editing.alternatives || [])];
    alternatives[index] = contentBlocksPlainText(blocks);
    const flags = contentFlags(questionContentBlocks(editing), groups);
    commitEditing({ ...editing, alternatives, alternativeBlocks: groups, ...flags });
  }

  function update<K extends keyof Question>(field: K, value: Question[K]) {
    if (!editing) return;
    commitEditing({ ...editing, [field]: value });
  }

  function updateBlocks(blocks: QuestionContentBlock[]) {
    if (!editing) return;
    const flags = contentFlags(blocks, editing.alternativeBlocks || []);
    commitEditing({
      ...editing,
      contentBlocks: blocks,
      ...flags,
    });
  }

  function insertFormulaFromToolbar() {
    if (!editing || editing.isLocked) return;
    if (formulaInsertionRef.current) {
      formulaInsertionRef.current();
      return;
    }
    addContentBlock("formula");
  }

  function deactivateInlineEditor() {
    formulaInsertionRef.current = null;
    textFormattingRef.current = null;
    textAlignmentRef.current = null;
    setHasFormulaCursor(false);
    setActiveTextFormats([]);
    setActiveTextAlignment(null);
  }

  function addContentBlock(type: "text" | "formula" | "table" | "image") {
    if (!editing) return;
    const id = `${type}-${Date.now()}`;
    const block: QuestionContentBlock = type === "text" ? { id, type, text: "", section: true }
      : type === "formula" ? { id, type, latex: "", display: "block" }
        : type === "table" ? { id, type, data: "", hasHeader: true, headerRows: 1, fontSize: 11 }
          : { id, type, urls: [], displayScale: 50 };
    const blocks = [...questionContentBlocks(editing), block];
    commitEditing({ ...editing, contentBlocks: blocks, hasMath: editing.hasMath || type === "formula", hasTable: editing.hasTable || type === "table", hasMedia: editing.hasMedia || type === "image" });
  }

  function addAlternativeBlock(index: number, type: "text" | "formula" | "table" | "image") {
    if (!editing) return;
    const current = editing.alternativeBlocks?.[index] || [];
    const prefix = `alternative-${index + 1}-${type}`;
    let sequence = current.length + 1;
    while (current.some((item) => item.id === `${prefix}-${sequence}`)) sequence += 1;
    const id = `${prefix}-${sequence}`;
    const block: QuestionContentBlock = type === "text" ? { id, type, text: "", section: true }
      : type === "formula" ? { id, type, latex: "", display: "block" }
        : type === "table" ? { id, type, data: "", hasHeader: true, headerRows: 1, fontSize: 11 }
          : { id, type, urls: [], displayScale: 50 };
    updateAlternativeBlocks(index, [...current, block]);
  }

  async function saveQuestion(status?: QuestionStatus, overrides: Partial<Question> = {}, successMessage?: string) {
    if (!editing) return;
    const source = { ...editing, ...overrides };
    const blocks = questionContentBlocks(source);
    const normalized = {
      ...source,
      contentBlocks: blocks,
      ...contentFlags(blocks, source.alternativeBlocks || []),
      stem: contentBlocksPlainText(blocks.filter((block) => block.type === "text" || block.type === "formula" || block.type === "script")),
      formula: blocks.filter((block): block is Extract<QuestionContentBlock, { type: "formula" }> => block.type === "formula").map((block) => block.latex).filter(Boolean).join("\\\\[0.55em]"),
      tableData: blocks.filter((block): block is Extract<QuestionContentBlock, { type: "table" }> => block.type === "table").map((block) => block.data).filter(Boolean).join("\n\n"),
      imageUrls: blocks.filter((block): block is Extract<QuestionContentBlock, { type: "image" }> => block.type === "image").flatMap((block) => block.urls),
    };
    const content = composeQuestionContent(normalized);
    const payload = { ...normalized, content, status: status || source.status, preview: content.slice(0, 480) };
    if (!payload.school.trim() || !payload.year || !payload.number || !payload.stem?.trim()) {
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
      setEditing(prepareForEditing(result.question));
      if (!result.question.isLocked) { setShowUnlock(false); setUnlockReason(""); }
      setDirty(false);
      setMessage(successMessage || (status === "ready" ? "Questão revisada e marcada como pronta." : "Alterações salvas no acervo."));
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Não foi possível salvar.");
    } finally {
      setSaving(false);
    }
  }

  function authenticateAndLock() {
    if (!editing) return;
    const allBlocks = [...questionContentBlocks(editing), ...(editing.alternativeBlocks || []).flat()];
    if (!editing.answer.trim()) {
      setMessage("Informe o gabarito antes de autenticar a questão.");
      return;
    }
    if (allBlocks.some((block) => block.type === "pending-media")) {
      setMessage("Converta ou confira as mídias pendentes antes de autenticar esta questão.");
      return;
    }
    const now = new Date().toISOString();
    const event: QuestionAuditEvent = { type: "authenticated", actor: ADMINISTRATOR_NAME, at: now };
    void saveQuestion("ready", {
      authenticatedAt: now,
      authenticatedBy: ADMINISTRATOR_NAME,
      isLocked: true,
      lockedAt: now,
      lockedBy: ADMINISTRATOR_NAME,
      lastUnlockReason: "",
      auditTrail: [...(editing.auditTrail || []), event],
    }, "Questão autenticada e travada pelo administrador.");
  }

  function unlockQuestion() {
    if (!editing) return;
    const reason = unlockReason.trim();
    if (reason.length < 5) {
      setMessage("Informe um motivo de desbloqueio com pelo menos 5 caracteres.");
      return;
    }
    const now = new Date().toISOString();
    const event: QuestionAuditEvent = { type: "unlocked", actor: ADMINISTRATOR_NAME, at: now, reason };
    void saveQuestion("review", {
      authenticatedAt: "",
      authenticatedBy: "",
      isLocked: false,
      lockedAt: "",
      lockedBy: "",
      lastUnlockReason: reason,
      auditTrail: [...(editing.auditTrail || []), event],
    }, "Questão desbloqueada. A autenticação anterior foi invalidada.");
  }

  async function restoreOriginal() {
    if (!editing || !revisionIds.has(editing.id)) return;
    setSaving(true);
    try {
      const response = await fetch(`/api/questions/revisions?id=${encodeURIComponent(editing.id)}`, { method: "DELETE" });
      if (!response.ok) throw new Error("Não foi possível restaurar.");
      setRevisions((current) => current.filter((question) => question.id !== editing.id));
      const original = baseQuestions.find((question) => question.id === editing.id);
      if (original) setEditing(prepareForEditing(original));
      else setEditing({ ...emptyQuestion() });
      formulaInsertionRef.current = null;
      textFormattingRef.current = null;
      textAlignmentRef.current = null;
      setHasFormulaCursor(false);
      setActiveTextFormats([]);
      setActiveTextAlignment(null);
      setUndoStack([]);
      setRedoStack([]);
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
    formulaInsertionRef.current = null;
    textFormattingRef.current = null;
    textAlignmentRef.current = null;
    setHasFormulaCursor(false);
    setActiveTextFormats([]);
    setActiveTextAlignment(null);
    setUndoStack([]);
    setRedoStack([]);
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

  const readyCount = questions.filter((question) => question.status === "ready").length;
  const pendingCount = questions.length - readyCount;
  const authenticatedCount = questions.filter((question) => question.isLocked && question.authenticatedAt).length;
  const isEditingLocked = Boolean(editing?.isLocked);

  return (
    <div className="review-app">
      <header className="topbar review-topbar">
        <Link className="brand" href="/" aria-label="SimpleQuest — início">
          <span className="brand-mark">SQ</span>
          <span><strong>SimpleQuest</strong><small>Banco de questões</small></span>
        </Link>
        <nav aria-label="Navegação principal">
          <Link href="/">Questões</Link>
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
            <article><strong>{authenticatedCount.toLocaleString("pt-BR")}</strong><span>autenticadas</span></article>
          </div>
        </section>

        <section className="review-workspace">
          <aside className="review-queue">
            <div className="queue-title"><div><span>FILA DE QUESTÕES</span><strong>{filtered.length.toLocaleString("pt-BR")}</strong></div><small>{readyCount.toLocaleString("pt-BR")} prontas</small></div>
            <label className="queue-search"><span>⌕</span><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Buscar na fila" /></label>
            <div className="queue-filters">
              <select value={queueFilter} onChange={(event) => setQueueFilter(event.target.value as QueueFilter)} aria-label="Situação da revisão">
                <option value="review">Para revisar</option><option value="unauthenticated">Não autenticadas</option><option value="authenticated">Autenticadas</option><option value="revised">Já alteradas</option><option value="ready">Prontas</option><option value="all">Todas</option>
              </select>
              <select value={school} onChange={(event) => setSchool(event.target.value)} aria-label="Filtrar instituição"><option value="">Todas as instituições</option>{schools.map((item) => <option key={item}>{item}</option>)}</select>
            </div>
            <div className="queue-list" ref={queueListRef}>
              {loading && <p className="queue-empty">Carregando acervo…</p>}
              {!loading && filtered.slice(0, 100).map((question) => (
                <button className={editing?.id === question.id ? "active" : ""} key={question.id} onClick={() => chooseQuestion(question)}>
                  <span className={`queue-status ${question.isLocked ? "authenticated" : question.status}`} />
                  <span><strong>{question.school} · {question.year}</strong><small>Questão {question.number} · {question.subjects[0] || "Sem assunto"}</small></span>
                  {question.isLocked ? <i className="authenticated">autenticada</i> : revisionIds.has(question.id) && <i>editada</i>}
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
                  <span className={`editor-state ${isEditingLocked ? "authenticated" : editing.status}`}>{isEditingLocked ? "Autenticada 🔒" : editing.status === "ready" ? "Pronta" : "Em revisão"}</span>
                </div>

                {isEditingLocked && (
                  <section className="authentication-banner">
                    <div><strong>Questão autenticada e travada</strong><span>Conferida por {editing.authenticatedBy || ADMINISTRATOR_NAME} em {editing.authenticatedAt ? new Date(editing.authenticatedAt).toLocaleString("pt-BR") : "data não registrada"}.</span></div>
                    <button type="button" onClick={() => setShowUnlock((value) => !value)}>Desbloquear para edição</button>
                  </section>
                )}
                {isEditingLocked && showUnlock && (
                  <section className="unlock-panel">
                    <label><span>Motivo do desbloqueio *</span><textarea rows={2} value={unlockReason} onChange={(event) => setUnlockReason(event.target.value)} placeholder="Ex.: corrigir uma alternativa após nova conferência" /></label>
                    <div><button type="button" className="secondary-button" onClick={() => { setShowUnlock(false); setUnlockReason(""); }}>Cancelar</button><button type="button" className="danger-button" onClick={unlockQuestion} disabled={saving}>Confirmar desbloqueio</button></div>
                  </section>
                )}

                <div className="editor-grid">
                  <label><span>Instituição *</span><input disabled={isEditingLocked} value={editing.school} onChange={(event) => update("school", event.target.value)} placeholder="Ex.: CMB" /></label>
                  <label><span>Ano *</span><input disabled={isEditingLocked} type="number" value={editing.year} onChange={(event) => update("year", Number(event.target.value))} /></label>
                  <label><span>Número *</span><input disabled={isEditingLocked} type="number" value={editing.number} onChange={(event) => update("number", Number(event.target.value))} /></label>
                  <label><span>Formato</span><select disabled={isEditingLocked} value={editing.answerType || "ABCDE"} onChange={(event) => changeAnswerType(event.target.value as ChoiceMode)}><option value="ABCDE">A–E</option><option value="ABCD">A–D</option><option value="CE">Certo / Errado</option></select></label>
                  <label className="editor-subjects"><span>Assuntos</span><input value={editing.subjects.join(", ")} onChange={(event) => update("subjects", event.target.value.split(",").map((item) => item.trim()).filter(Boolean))} placeholder="Frações, Porcentagem" /></label>
                  <label><span>Gabarito</span><input disabled={isEditingLocked} className="answer-input" value={editing.answer} onChange={(event) => update("answer", event.target.value.toUpperCase().slice(0, 1))} placeholder="A" /></label>
                  <label><span>Dificuldade</span><select value={editing.difficulty} onChange={(event) => update("difficulty", event.target.value)}><option value="">Não definida</option><option value="Fácil">Fácil</option><option value="Média">Média</option><option value="Difícil">Difícil</option></select></label>
                </div>

                <div className="editor-flags">
                  <span>Elementos da questão</span>
                  <div className="element-add-buttons" aria-label="Adicionar elemento ao enunciado">
                    <button type="button" disabled={isEditingLocked} onClick={() => addContentBlock("text")}>＋ Texto</button>
                    <button type="button" disabled={isEditingLocked} onClick={() => addContentBlock("image")}>＋ Imagem ou gráfico</button>
                    <button type="button" disabled={isEditingLocked} onClick={() => addContentBlock("table")}>＋ Tabela</button>
                    <button
                      type="button"
                      className="global-formula-button"
                      disabled={isEditingLocked}
                      onMouseDown={(event) => event.preventDefault()}
                      onClick={insertFormulaFromToolbar}
                      title={hasFormulaCursor ? "Inserir fórmula na posição selecionada" : "Adicionar uma fórmula separada ao enunciado"}
                    >＋ Inserir fórmula{hasFormulaCursor ? " no cursor" : ""}</button>
                  </div>
                  <div className="text-format-buttons" aria-label="Formatação do texto">
                    <button type="button" className={activeTextFormats.includes("bold") ? "active" : ""} aria-pressed={activeTextFormats.includes("bold")} disabled={isEditingLocked || !hasFormulaCursor} onMouseDown={(event) => event.preventDefault()} onClick={() => applyTextFormatting("bold")} title="Aplicar ou remover negrito"><strong>B</strong></button>
                    <button type="button" className={activeTextFormats.includes("italic") ? "active" : ""} aria-pressed={activeTextFormats.includes("italic")} disabled={isEditingLocked || !hasFormulaCursor} onMouseDown={(event) => event.preventDefault()} onClick={() => applyTextFormatting("italic")} title="Aplicar ou remover itálico"><em>I</em></button>
                    <button type="button" className={activeTextFormats.includes("underline") ? "active" : ""} aria-pressed={activeTextFormats.includes("underline")} disabled={isEditingLocked || !hasFormulaCursor} onMouseDown={(event) => event.preventDefault()} onClick={() => applyTextFormatting("underline")} title="Aplicar ou remover sublinhado"><u>U</u></button>
                    <span className="format-divider" aria-hidden="true" />
                    {(["left", "center", "right", "justify"] as TextAlignment[]).map((alignment) => {
                      const labels: Record<TextAlignment, string> = { left: "Alinhar à esquerda", center: "Centralizar", right: "Alinhar à direita", justify: "Justificar" };
                      return <button type="button" className={`alignment-button align-${alignment}${activeTextAlignment === alignment ? " active" : ""}`} aria-label={labels[alignment]} title={labels[alignment]} aria-pressed={activeTextAlignment === alignment} disabled={isEditingLocked || !hasFormulaCursor || !activeTextAlignment} onMouseDown={(event) => event.preventDefault()} onClick={() => applyTextAlignment(alignment)} key={alignment}><span className="alignment-icon" aria-hidden="true"><i /><i /><i /></span></button>;
                    })}
                  </div>
                  <div className="history-buttons" aria-label="Histórico de alterações">
                    <button type="button" disabled={isEditingLocked || !undoStack.length} onClick={undoEditing} title="Desfazer última alteração" aria-label="Desfazer última alteração">↶</button>
                    <button type="button" disabled={isEditingLocked || !redoStack.length} onClick={redoEditing} title="Refazer alteração desfeita" aria-label="Refazer alteração desfeita">↷</button>
                  </div>
                </div>

                <ContentBlocksEditor disabled={isEditingLocked} blocks={questionContentBlocks(editing)} showFormula={editing.hasMath} showTable={editing.hasTable} showMedia={editing.hasMedia} onChange={updateBlocks} onActivateFormulaInsertion={activateFormulaInsertion} onActivateTextFormatting={activateTextFormatting} onActivateTextAlignment={activateTextAlignment} onDeactivateEditor={deactivateInlineEditor} />

                <section className="alternatives-editor">
                  <div><span>Alternativas</span><small>Cada opção pode combinar texto, fórmula, imagem e tabela.</small></div>
                  {ANSWER_OPTIONS[editing.answerType || "ABCDE"].map((option, index) => {
                    const alternative = editing.alternatives?.[index] || "";
                    const alternativeContent = editing.alternativeBlocks?.[index]?.length ? editing.alternativeBlocks[index] : [{ id: `alternative-${index + 1}-text`, type: "text" as const, text: alternative }];
                    const hasFormula = alternativeContent.some((block) => block.type === "formula" || block.type === "script");
                    const hasTable = alternativeContent.some((block) => block.type === "table");
                    const hasMedia = alternativeContent.some((block) => block.type === "image" || block.type === "pending-media");
                    return <article className="alternative-editor-card" key={`${editing.id}-${option}`}>
                      <header className="alternative-editor-header">
                        <strong className="alternative-editor-letter">{option}</strong>
                        <div className="alternative-add-buttons" aria-label={`Adicionar conteúdo à alternativa ${option}`}>
                          <button type="button" disabled={isEditingLocked} onClick={() => addAlternativeBlock(index, "text")}>＋ Texto</button>
                          <button type="button" disabled={isEditingLocked} onClick={() => addAlternativeBlock(index, "formula")}>＋ Fórmula</button>
                          <button type="button" disabled={isEditingLocked} onClick={() => addAlternativeBlock(index, "image")}>＋ Imagem</button>
                          <button type="button" disabled={isEditingLocked} onClick={() => addAlternativeBlock(index, "table")}>＋ Tabela</button>
                        </div>
                      </header>
                      <ContentBlocksEditor compact disabled={isEditingLocked} blocks={alternativeContent} showFormula={hasFormula} showTable={hasTable} showMedia={hasMedia} onChange={(blocks) => updateAlternativeBlocks(index, blocks)} onActivateFormulaInsertion={activateFormulaInsertion} onActivateTextFormatting={activateTextFormatting} onActivateTextAlignment={activateTextAlignment} onDeactivateEditor={deactivateInlineEditor} imagePlaceholder={alternativeImagePlaceholder(editing, option)} />
                    </article>;
                  })}
                </section>

                {!!editing.auditTrail?.length && (
                  <section className="audit-trail">
                    <div><span>Histórico de confiança</span><small>Os registros permanecem mesmo após um desbloqueio.</small></div>
                    {[...editing.auditTrail].reverse().slice(0, 5).map((event, index) => <p key={`${event.at}-${index}`}><strong>{event.type === "authenticated" ? "Autenticada" : "Desbloqueada"}</strong><span>{event.actor} · {new Date(event.at).toLocaleString("pt-BR")}{event.reason ? ` · ${event.reason}` : ""}</span></p>)}
                  </section>
                )}

                <div className="editor-footer">
                  <div>{message && <p className="editor-message">{message}</p>}{dirty && !message && <p className="editor-unsaved">Há alterações ainda não salvas.</p>}</div>
                  {!isEditingLocked && revisionIds.has(editing.id) && <button className="restore-button" onClick={restoreOriginal} disabled={saving}>{editing.isCustom ? "Excluir cadastro" : "Restaurar original"}</button>}
                  {isEditingLocked ? <button className="secondary-button" onClick={() => saveQuestion(undefined, {}, "Classificação da questão atualizada.")} disabled={saving || !dirty}>{saving ? "Salvando…" : "Salvar classificação"}</button> : <>
                    <button className="secondary-button" onClick={() => saveQuestion("review")} disabled={saving}>{saving ? "Salvando…" : "Salvar rascunho"}</button>
                    <button className="primary-button" onClick={() => saveQuestion("ready")} disabled={saving}>{saving ? "Salvando…" : "Salvar e marcar como pronta"}</button>
                    <button className="authenticate-button" onClick={authenticateAndLock} disabled={saving}>{saving ? "Autenticando…" : "✓ Autenticar e travar"}</button>
                  </>}
                </div>
              </>
            ) : <div className="editor-empty">Selecione uma questão para começar a revisão.</div>}
          </section>
        </section>
      </main>
    </div>
  );
}
  function prepareForEditing(question: Question): Question {
    const normalized = normalizeQuestionContent(question);
    const structured = structureQuestion(normalized);
    const mode = normalized.answerType || "ABCDE";
    const alternatives = ANSWER_OPTIONS[mode].map((option, index) => normalized.alternatives?.[index] || (mode === "CE" ? defaultAlternativeText(mode, option) : ""));
    const alternativeBlocks = ANSWER_OPTIONS[mode].map<QuestionContentBlock[]>((_, index) => {
      const existing = normalized.alternativeBlocks?.[index] || [];
      return existing.length ? [...existing] : [{ id: `alternative-${index + 1}-text`, type: "text", text: alternatives[index] }];
    });
    return { ...normalized, stem: structured.stem, alternatives, contentBlocks: questionContentBlocks(normalized), alternativeBlocks };
  }

function contentFlags(contentBlocks: QuestionContentBlock[], alternativeBlocks: QuestionContentBlock[][]) {
  const blocks = [...contentBlocks, ...alternativeBlocks.flat()];
  return {
    hasMath: blocks.some((block) => block.type === "formula" || block.type === "script"),
    hasTable: blocks.some((block) => block.type === "table"),
    hasMedia: blocks.some((block) => block.type === "image" || block.type === "pending-media"),
  };
}

function alternativeImagePlaceholder(question: Question, option: string) {
  const school = question.school.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "") || "instituicao";
  const base = `${school}-${question.year}-${question.number}_${option.toLowerCase()}`;
  return `/question-media/${base}.webp\n/question-media/${base}_1.webp`;
}
