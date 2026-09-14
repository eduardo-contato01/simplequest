import type { ReactNode } from "react";
import type { Question } from "../question-model";
import { QuestionFilters, type QuestionFiltersProps } from "./QuestionFilters";
import { QuestionCard } from "./QuestionCard";
import { QuestionsPagination } from "./QuestionsPagination";

export type QuestionsWorkspaceProps = {
  filters: QuestionFiltersProps;
  loading: boolean;
  catalogStatus: "loading" | "available" | "base-error" | "revisions-unavailable";
  onReload: () => void;
  total: number;
  visible: Question[];
  sort: string;
  setSort: (sort: string) => void;
  currentPage: number;
  pageCount: number;
  selectedIds: Set<string>;
  expanded: string | null;
  revealed: Set<string>;
  responses: Record<string, string>;
  toggleSelected: (id: string) => void;
  setExpanded: (id: string | null) => void;
  toggleAnswer: (id: string) => void;
  markResponse: (id: string, option: string) => void;
  children: ReactNode;
};

export function QuestionsWorkspace({ filters, loading, catalogStatus, onReload, total, visible, sort, setSort, currentPage, pageCount, selectedIds, expanded, revealed, responses, toggleSelected, setExpanded, toggleAnswer, markResponse, children }: QuestionsWorkspaceProps) {
  return (
    <section className="workspace" id="questoes">
      <QuestionFilters {...filters} />
      <div className="content-grid">
        <section className="results" aria-live="polite">
          <div className="results-heading">
            <div><span className="section-kicker">BANCO DE QUESTÕES</span><h2>{loading ? "Carregando acervo…" : catalogStatus === "base-error" ? "Acervo indisponível" : `${total.toLocaleString("pt-BR")} questões encontradas`}</h2></div>
            <label className="sort-control">Ordenar por <select value={sort} onChange={(e) => { setSort(e.target.value); filters.setPage(1); }}><option value="recent">Mais recentes</option><option value="oldest">Mais antigas</option><option value="school">Prova</option></select></label>
          </div>
          {catalogStatus === "revisions-unavailable" && <p className="review-note" role="status">Revisões indisponíveis. Exibindo o catálogo base. <button onClick={onReload}>Tentar novamente</button></p>}
          <div className="question-list">
            {visible.map((question) => (
              <QuestionCard key={question.id} question={question}
                isSelected={selectedIds.has(question.id)} isExpanded={expanded === question.id}
                isRevealed={revealed.has(question.id)} response={responses[question.id] || ""}
                onToggleSelected={() => toggleSelected(question.id)}
                onToggleExpanded={() => setExpanded(expanded === question.id ? null : question.id)}
                onToggleAnswer={() => toggleAnswer(question.id)}
                onResponseChange={(option) => markResponse(question.id, option)} />
            ))}
            {catalogStatus === "base-error" ? (
              <div className="empty-state" role="alert"><strong>Não foi possível carregar o acervo</strong><p>Tente novamente para carregar as questões.</p><button onClick={onReload}>Tentar novamente</button></div>
            ) : !loading && !visible.length && (
              <div className="empty-state"><strong>Nenhuma questão encontrada</strong><p>Tente retirar um filtro ou pesquisar por outro termo.</p></div>
            )}
          </div>
          <QuestionsPagination currentPage={currentPage} pageCount={pageCount} setPage={filters.setPage} />
        </section>
        {children}
      </div>
    </section>
  );
}
