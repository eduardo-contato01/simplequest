export type ChoiceMode = "ABCDE" | "ABCD" | "CE";

export type QuestionStatus = "ready" | "review";

export type QuestionAuditEvent = {
  type: "authenticated" | "unlocked";
  actor: string;
  at: string;
  reason?: string;
};

export type QuestionTextSegment = {
  text: string;
  bold?: boolean;
  italic?: boolean;
  underline?: boolean;
};

export type TextAlignment = "left" | "center" | "right" | "justify";

export type ImageDisplayScale = 25 | 50 | 75 | 100;

export type QuestionInlineContentBlock =
  | { id: string; type: "text"; text: string; segments?: QuestionTextSegment[]; section?: boolean; alignment?: TextAlignment }
  | { id: string; type: "formula"; latex: string; display?: "inline" | "block" }
  | { id: string; type: "script"; base: string; value: string; position: "superscript" | "subscript" };

export type QuestionContentBlock =
  | QuestionInlineContentBlock
  | { id: string; type: "table"; data: string; hasHeader?: boolean; headerRows?: number; fontSize?: number; content?: QuestionInlineContentBlock[] }
  | { id: string; type: "image"; urls: string[]; dimensions?: Array<{ width: number; height: number }>; displayScale?: ImageDisplayScale; hiddenByDefault?: boolean }
  | { id: string; type: "pending-media"; label: string; format: string };

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
  stem?: string;
  alternatives?: string[];
  formula?: string;
  tableData?: string;
  imageUrls?: string[];
  contentBlocks?: QuestionContentBlock[];
  alternativeBlocks?: QuestionContentBlock[][];
  authenticatedAt?: string;
  authenticatedBy?: string;
  isLocked?: boolean;
  lockedAt?: string;
  lockedBy?: string;
  lastUnlockReason?: string;
  auditTrail?: QuestionAuditEvent[];
};

export const ANSWER_OPTIONS: Record<ChoiceMode, string[]> = {
  ABCDE: ["A", "B", "C", "D", "E"],
  ABCD: ["A", "B", "C", "D"],
  CE: ["C", "E"],
};

export function defaultAlternativeText(mode: ChoiceMode, option: string) {
  if (mode === "CE") return option === "C" ? "Certo" : "Errado";
  return `Alternativa ${option}`;
}

export function structureQuestion(question: Question) {
  if (question.stem || question.alternatives?.length) {
    return {
      stem: question.stem || question.content,
      alternatives: question.alternatives || [],
    };
  }

  const mode = question.answerType || "ABCDE";
  if (mode === "CE") return { stem: question.content, alternatives: ANSWER_OPTIONS[mode].map((option) => defaultAlternativeText(mode, option)) };
  const lines = question.content.split(/\r?\n/).map((line) => line.trim()).filter(Boolean);
  const count = ANSWER_OPTIONS[mode].length;
  if (lines.length <= count) return { stem: question.content, alternatives: ANSWER_OPTIONS[mode].map((option) => defaultAlternativeText(mode, option)) };
  return {
    stem: lines.slice(0, -count).join("\n"),
    alternatives: lines.slice(-count).map((line) => line.replace(/^[A-E]\s*[).:\-–—]\s*/i, "")),
  };
}

export function composeQuestionContent(question: Question) {
  const structured = structureQuestion(question);
  return [structured.stem, ...structured.alternatives].filter(Boolean).join("\n");
}

export function questionContentBlocks(question: Question): QuestionContentBlock[] {
  if (question.contentBlocks?.length) return question.contentBlocks;
  const { stem } = structureQuestion(question);
  const blocks: QuestionContentBlock[] = [{ id: "legacy-text", type: "text", text: stem }];
  if (question.formula) blocks.push({ id: "legacy-formula", type: "formula", latex: question.formula });
  if (question.tableData) blocks.push({ id: "legacy-table", type: "table", data: question.tableData, hasHeader: true, fontSize: 11 });
  if (question.imageUrls?.length) blocks.push({ id: "legacy-image", type: "image", urls: question.imageUrls });
  return blocks;
}

export function normalizeImportedFormulaAlternatives(question: Question): Question {
  const mode = question.answerType || "ABCDE";
  const optionCount = ANSWER_OPTIONS[mode].length;
  const hasAlternatives = Boolean(question.alternatives?.some((alternative) => alternative.trim()) || question.alternativeBlocks?.some((group) => group?.length));
  if (hasAlternatives) return question;
  const blocks = questionContentBlocks(question);
  if (blocks.length <= optionCount) return question;
  const candidates = blocks.slice(-optionCount);
  if (!candidates.every((block) => block.type === "formula" || block.type === "script")) return question;
  const stemBlocks = blocks.slice(0, -optionCount);
  if (!stemBlocks.some((block) => block.type === "text" && block.text.trim())) return question;
  const alternativeBlocks = candidates.map((block, index): QuestionContentBlock[] => [
    { id: `a${index + 1}-text-before`, type: "text", text: "" },
    block.type === "formula" ? { ...block, id: `a${index + 1}-formula`, display: "inline" } : { ...block, id: `a${index + 1}-script` },
    { id: `a${index + 1}-text-after`, type: "text", text: "" },
  ]);
  return {
    ...question,
    stem: contentBlocksPlainText(stemBlocks),
    alternatives: ANSWER_OPTIONS[mode].map(() => ""),
    contentBlocks: stemBlocks,
    alternativeBlocks,
    hasMath: true,
  };
}

function normalizeFormulaBlocks(blocks: QuestionContentBlock[]) {
  return blocks.map((block, index): QuestionContentBlock => {
    if (block.type !== "formula" || block.display) return block;
    const previous = blocks[index - 1];
    const next = blocks[index + 1];
    const continuesSentence = previous?.type === "text" && next?.type === "text"
      && (/\s$/.test(previous.text) || /^(?:\s|[,.;:!?\)\]])/.test(next.text));
    return { ...block, display: continuesSentence ? "inline" : "block" };
  });
}

function repairCmb2004Question3(question: Question): Question {
  if (question.id !== "cmb-2004-3-34") return question;
  const blocks = question.contentBlocks || [];
  const matchesBrokenImport = blocks.length === 13
    && blocks[0]?.type === "text" && blocks[0].text === "(CMB – 2004) Considere as afirmativas:"
    && blocks[1]?.type === "formula" && blocks[1].latex === "\\frac{11}{4}-\\frac{13}{8}"
    && blocks[2]?.type === "formula" && blocks[2].latex === "=1,125"
    && blocks[4]?.type === "formula" && blocks[4].latex === "\\frac{3}{5}";
  if (!matchesBrokenImport) return question;
  const contentBlocks: QuestionContentBlock[] = [
    { id: "b1", type: "text", text: "(CMB – 2004) Considere as afirmativas:\nI- " },
    { id: "b2", type: "formula", latex: "\\frac{11}{4}-\\frac{13}{8}=1,125", display: "inline" },
    { id: "b3", type: "text", text: "\nII- 10% de 25 é maior que 5% de 50.\nIII- " },
    { id: "b4", type: "formula", latex: "\\frac{3}{5}", display: "inline" },
    { id: "b5", type: "text", text: " de 1500 " },
    { id: "b6", type: "script", base: "cm", value: "3", position: "superscript" },
    { id: "b7", type: "text", text: " = 90 dℓ.\nIV- 650 " },
    { id: "b8", type: "script", base: "dam", value: "2", position: "superscript" },
    { id: "b9", type: "text", text: " = 65 000 " },
    { id: "b10", type: "script", base: "m", value: "2", position: "superscript" },
    { id: "b11", type: "text", text: ".\nV- 2584 em algarismos romanos é MMDXXCIV.\n\nPode-se concluir que apenas são falsas as afirmativas de números:" },
  ];
  return {
    ...question,
    contentBlocks,
    stem: contentBlocksPlainText(contentBlocks),
    formula: "\\frac{11}{4}-\\frac{13}{8}=1,125\\\\[0.55em]\\frac{3}{5}",
    hasMath: true,
    status: "review",
  };
}

function mergeAdjacentTextBlocks(blocks: QuestionContentBlock[]) {
  const merged: QuestionContentBlock[] = [];
  for (const block of blocks) {
    const previous = merged[merged.length - 1];
    if (block.type !== "text" || previous?.type !== "text" || block.section || block.alignment !== previous.alignment) {
      merged.push(block);
      continue;
    }
    const segments = [
      ...(previous.segments?.length ? previous.segments : [{ text: previous.text }]),
      ...(block.segments?.length ? block.segments : [{ text: block.text }]),
    ].reduce<QuestionTextSegment[]>((result, segment) => {
      if (!segment.text) return result;
      const last = result[result.length - 1];
      if (last && Boolean(last.bold) === Boolean(segment.bold) && Boolean(last.italic) === Boolean(segment.italic) && Boolean(last.underline) === Boolean(segment.underline)) last.text += segment.text;
      else result.push({ ...segment });
      return result;
    }, []);
    merged[merged.length - 1] = {
      ...previous,
      text: previous.text + block.text,
      segments: segments.some((segment) => segment.bold || segment.italic || segment.underline) ? segments : undefined,
    };
  }
  return merged;
}

export function normalizeQuestionContent(question: Question): Question {
  const normalized = normalizeImportedFormulaAlternatives(repairCmb2004Question3(question));
  return {
    ...normalized,
    contentBlocks: normalized.contentBlocks ? mergeAdjacentTextBlocks(normalizeFormulaBlocks(normalized.contentBlocks)) : normalized.contentBlocks,
    alternativeBlocks: normalized.alternativeBlocks?.map((blocks) => mergeAdjacentTextBlocks(normalizeFormulaBlocks(blocks))),
  };
}

export function visibleQuestionContentBlocks(question: Question) {
  return questionContentBlocks(question).filter((block) => {
    if (block.type === "formula" || block.type === "script") return question.hasMath;
    if (block.type === "table") return question.hasTable;
    if (block.type === "image" || block.type === "pending-media") return question.hasMedia;
    return true;
  });
}

export function contentBlocksPlainText(blocks: QuestionContentBlock[]) {
  const superscript: Record<string, string> = { "0": "⁰", "1": "¹", "2": "²", "3": "³", "4": "⁴", "5": "⁵", "6": "⁶", "7": "⁷", "8": "⁸", "9": "⁹", "+": "⁺", "-": "⁻", "=": "⁼", "(": "⁽", ")": "⁾" };
  const subscript: Record<string, string> = { "0": "₀", "1": "₁", "2": "₂", "3": "₃", "4": "₄", "5": "₅", "6": "₆", "7": "₇", "8": "₈", "9": "₉", "+": "₊", "-": "₋", "=": "₌", "(": "₍", ")": "₎" };
  return blocks.map((block) => {
    if (block.type === "text") return block.text;
    if (block.type === "formula") return `\\(${block.latex}\\)`;
    if (block.type !== "script") return "";
    const map = block.position === "superscript" ? superscript : subscript;
    const value = block.position === "superscript" && block.value === "o" ? "º" : block.position === "superscript" && block.value === "a" ? "ª" : block.position === "superscript" && block.value === "os" ? "ºs" : block.position === "superscript" && block.value === "as" ? "ªs" : [...block.value].map((character) => map[character] || character).join("");
    return block.base + value;
  }).reduce((content, value, index) => content + (index > 0 && blocks[index]?.type === "text" && blocks[index].section ? "\n" : "") + value, "").trim();
}

export function mergeQuestionCatalog(base: Question[], revisions: Question[]) {
  const byId = new Map(base.map((question) => [question.id, question]));
  for (const revision of revisions) {
    byId.set(revision.id, { ...byId.get(revision.id), ...revision });
  }
  return [...byId.values()].map(normalizeQuestionContent);
}

export function questionAnswerFeedback(question: Question, response: string) {
  const officialAnswer = question.answer.trim().toUpperCase();
  return { choiceMode: question.answerType || "ABCDE", officialAnswer, isCorrect: Boolean(response && response === officialAnswer) };
}

export type QuestionCatalogResult = {
  questions: Question[];
  status: "available" | "revisions-unavailable";
};

export async function loadQuestionCatalogWithStatus(): Promise<QuestionCatalogResult> {
  const baseResponse = await fetch("/data/questions.json");
  if (!baseResponse.ok) throw new Error(`Falha ao carregar a base (${baseResponse.status}).`);
  const base = (await baseResponse.json()) as Question[];
  if (!Array.isArray(base)) throw new Error("Formato inválido do catálogo base.");
  try {
    const revisionResponse = await fetch("/api/questions/revisions");
    if (!revisionResponse.ok) return { questions: base.map(normalizeQuestionContent), status: "revisions-unavailable" };
    const payload = (await revisionResponse.json()) as { questions: Question[] };
    return { questions: mergeQuestionCatalog(base, payload.questions || []), status: "available" };
  } catch {
    return { questions: base.map(normalizeQuestionContent), status: "revisions-unavailable" };
  }
}

// Preserve the array-returning contract used by the editorial page.
export async function loadQuestionCatalog() {
  return (await loadQuestionCatalogWithStatus()).questions;
}
