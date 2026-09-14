import { ANSWER_OPTIONS, defaultAlternativeText, structureQuestion, type Question } from "../question-model";
import { QuestionBlocks } from "./QuestionBlocks";

type Props = { selected: Question[]; simulationTitle: string };

export function SimulationPrintSheet({ selected, simulationTitle }: Props) {
  return (
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
  );
}
