import { ANSWER_OPTIONS, defaultAlternativeText, structureQuestion, questionAnswerFeedback, type Question } from "../question-model";
import { QuestionBlocks } from "./QuestionBlocks";

type Props = { question: Question; response: string; onResponseChange: (option: string) => void };

export function QuestionAlternatives({ question, response, onResponseChange }: Props) {
  const { choiceMode, officialAnswer, isCorrect } = questionAnswerFeedback(question, response);
  const questionParts = structureQuestion(question);
  return (
    <section className="question-section alternatives-section">
      <div className="alternatives-heading"><span>Selecione uma alternativa</span></div>
      <div className="alternatives-list" role="radiogroup" aria-label={`Alternativas da questão ${question.number}`}>
        {ANSWER_OPTIONS[choiceMode].map((option, optionIndex) => {
          const stateClass = response ? (option === officialAnswer ? "correct" : option === response ? "incorrect" : "") : "";
          const selectAlternative = () => onResponseChange(option);
          return <div
            key={option}
            className={`alternative-option ${stateClass}`.trim()}
            role="radio"
            aria-checked={response === option}
            tabIndex={0}
            onClick={selectAlternative}
            onKeyDown={(event) => {
              if ((event.key === "Enter" || event.key === " ") && event.target === event.currentTarget) {
                event.preventDefault();
                selectAlternative();
              }
            }}
          ><strong>{option}</strong><div className="alternative-content">{question.alternativeBlocks?.[optionIndex]?.length ? <QuestionBlocks question={question} blocks={question.alternativeBlocks[optionIndex]} compact /> : questionParts.alternatives[optionIndex] || defaultAlternativeText(choiceMode, option)}</div></div>;
        })}
      </div>
      {response && <span className={`answer-feedback ${isCorrect ? "correct" : "incorrect"}`}>{isCorrect ? "Resposta correta." : `Resposta incorreta. Gabarito: ${officialAnswer || "—"}.`}</span>}
    </section>
  );
}
