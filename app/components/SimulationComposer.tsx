import type { Question } from "../question-model";
import { SimulationSelectionSummary } from "./SimulationSelectionSummary";

export type SimulationComposerProps = { selected: Question[]; simulationTitle: string; onTitleChange: (title: string) => void; onRemove: (id: string) => void; onClear: () => void };

export function SimulationComposer({ selected, simulationTitle, onTitleChange, onRemove, onClear }: SimulationComposerProps) {
  return (
    <aside className="simulation-panel" id="simulado">
      <div className="panel-title"><span>SIMULADO ATUAL</span><strong>{selected.length}</strong></div>
      <input className="simulation-name" value={simulationTitle} onChange={(e) => onTitleChange(e.target.value)} aria-label="Título do simulado" />
      <SimulationSelectionSummary selected={selected} onRemove={onRemove} />
      <button className="generate-button" disabled={!selected.length} onClick={() => window.print()}>Gerar simulado / PDF</button>
      {!!selected.length && <button className="remove-all" onClick={onClear}>Remover todas</button>}
      <p className="panel-tip">A impressão gera a versão do aluno e uma página separada com o gabarito.</p>
    </aside>
  );
}
