import type { Question } from "../question-model";

type Props = { selected: Question[]; onRemove: (id: string) => void };

export function SimulationSelectionSummary({ selected, onRemove }: Props) {
  return (
    <>{selected.length ? (
      <ol className="selected-list">
        {selected.slice(0, 8).map((question) => (
          <li key={question.id}><span>{question.school} · {question.year} · Q{question.number}</span><button onClick={() => onRemove(question.id)} aria-label={`Remover questão ${question.number}`}>×</button></li>
        ))}
        {selected.length > 8 && <li className="more-items">+ {selected.length - 8} questões selecionadas</li>}
      </ol>
    ) : (
      <div className="panel-empty"><span>＋</span><strong>Seu simulado começa aqui</strong><p>Adicione questões à esquerda para montar a prova.</p></div>
    )}
    <div className="panel-summary"><span>Questões <strong>{selected.length}</strong></span><span>Gabarito <strong>incluído</strong></span></div></>
  );
}
