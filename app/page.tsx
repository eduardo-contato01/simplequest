"use client";

import { QuestionsWorkspace } from "./components/QuestionsWorkspace";
import { SimulationComposer } from "./components/SimulationComposer";
import { SimulationPrintSheet } from "./components/SimulationPrintSheet";
import { useQuestionsWorkspace } from "./hooks/useQuestionsWorkspace";

export default function Home() {
  const { workspace, selected, simulationTitle, setSimulationTitle, clearSelection } = useQuestionsWorkspace();
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

          <QuestionsWorkspace {...workspace}>
            <SimulationComposer selected={selected} simulationTitle={simulationTitle}
              onTitleChange={setSimulationTitle} onRemove={workspace.toggleSelected} onClear={clearSelection} />
          </QuestionsWorkspace>

          <section className="migration-note">
            <span>PRÓXIMA ETAPA</span>
            <div><h2>O acervo continua crescendo sem trabalho duplicado.</h2><p>Há 1.253 registros catalogados sem conteúdo vinculado. Eles entrarão numa fila de importação assistida, junto às provas digitadas que ainda não possuem indicadores.</p></div>
            <strong>1.253<br /><small>itens no backlog</small></strong>
          </section>
        </main>
      </div>

      <SimulationPrintSheet selected={selected} simulationTitle={simulationTitle} />
    </>
  );
}
