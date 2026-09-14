import type { Question } from "../question-model";
import { QuestionBlocks } from "./QuestionBlocks";
import { QuestionAlternatives } from "./QuestionAlternatives";

export type QuestionCardProps = {
  question: Question; isSelected: boolean; isExpanded: boolean; isRevealed: boolean; response: string;
  onToggleSelected: () => void; onToggleExpanded: () => void; onToggleAnswer: () => void;
  onResponseChange: (option: string) => void;
};

export function QuestionCard({ question, isSelected, isExpanded, isRevealed, response, onToggleSelected, onToggleExpanded, onToggleAnswer, onResponseChange }: QuestionCardProps) {
  const isAuthenticated = Boolean(question.isLocked && question.authenticatedAt);
  return (
    <article className={`question-card ${isSelected ? "selected" : ""}`} key={question.id}>
      <div className="card-topline">
        <label className="select-question">
          <input type="checkbox" checked={isSelected} onChange={onToggleSelected} />
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
            <QuestionAlternatives question={question} response={response} onResponseChange={onResponseChange} />
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
        <button onClick={onToggleExpanded}>{isExpanded ? "Recolher" : "Ver questão completa"}</button>
        <button onClick={onToggleAnswer}>{isRevealed ? `Gabarito: ${question.answer || "—"}` : "Mostrar gabarito"}</button>
        <span>Fonte: {question.sourceDocument}</span>
      </footer>
    </article>
  );
}
