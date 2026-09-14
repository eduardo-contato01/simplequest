"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { searchRelevance } from "../search-utils";
import { useQuestionCatalog } from "./useQuestionCatalog";

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

export function useQuestionsWorkspace() {
  const catalog = useQuestionCatalog();
  const { questions, loading } = catalog;
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
  }, []);

  useEffect(() => {
    if (loading || viewStateReady) return;
    let secondFrame = 0;
    const firstFrame = requestAnimationFrame(() => {
      secondFrame = requestAnimationFrame(() => {
        window.scrollTo({ top: restoredScrollRef.current });
        setViewStateReady(true);
      });
    });
    return () => { cancelAnimationFrame(firstFrame); cancelAnimationFrame(secondFrame); };
  }, [loading, viewStateReady]);

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

  return {
    selected, simulationTitle, setSimulationTitle,
    clearSelection: () => setSelectedIds(new Set()),
    workspace: {
      filters: { query, school, year, subject, status, schools, years, subjects, setQuery, setSchool, setYear, setSubject, setStatus, setPage, clearFilters },
      loading, catalogStatus: catalog.status, onReload: catalog.reload,
      total: filtered.length, visible, sort, setSort, currentPage, pageCount,
      selectedIds, expanded, revealed, responses, toggleSelected, setExpanded, toggleAnswer, markResponse,
    },
  };
}
