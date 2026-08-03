export type ChoiceMode = "ABCDE" | "ABCD" | "CE";

export type QuestionStatus = "ready" | "review";

export type Question = {
  id: string;
  sourceRow: number;
  school: string;
  year: number;
  number: number;
  subjects: string[];
  answer: string;
  answerType?: ChoiceMode;
  difficulty: string;
  content: string;
  preview: string;
  sourceDocument: string;
  sourceBookmark: string;
  hasTable: boolean;
  hasMedia: boolean;
  hasMath: boolean;
  status: QuestionStatus;
  isCustom?: boolean;
  updatedAt?: string;
};

export function mergeQuestionCatalog(base: Question[], revisions: Question[]) {
  const byId = new Map(base.map((question) => [question.id, question]));
  for (const revision of revisions) {
    byId.set(revision.id, { ...byId.get(revision.id), ...revision });
  }
  return [...byId.values()];
}

export async function loadQuestionCatalog() {
  const baseResponse = await fetch("/data/questions.json");
  const base = (await baseResponse.json()) as Question[];
  try {
    const revisionResponse = await fetch("/api/questions/revisions");
    if (!revisionResponse.ok) return base;
    const payload = (await revisionResponse.json()) as { questions: Question[] };
    return mergeQuestionCatalog(base, payload.questions || []);
  } catch {
    return base;
  }
}
