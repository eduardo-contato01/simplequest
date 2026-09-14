"use client";

import { useCallback, useEffect, useState } from "react";
import { loadQuestionCatalogWithStatus, type Question, type QuestionCatalogResult } from "../question-model";

type CatalogState = QuestionCatalogResult
  | { status: "loading"; questions: Question[] }
  | { status: "base-error"; questions: Question[]; error: unknown };

export function useQuestionCatalog() {
  const [state, setState] = useState<CatalogState>({ status: "loading", questions: [] });
  const [attempt, setAttempt] = useState(0);

  useEffect(() => {
    let active = true;
    loadQuestionCatalogWithStatus().then(
      (result) => { if (active) setState(result); },
      (error: unknown) => { if (active) setState({ status: "base-error", questions: [], error }); },
    );
    return () => { active = false; };
  }, [attempt]);

  const reload = useCallback(() => {
    setState((current) => ({ status: "loading", questions: current.questions }));
    setAttempt((current) => current + 1);
  }, []);

  return { ...state, loading: state.status === "loading", reload };
}
