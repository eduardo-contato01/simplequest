import { desc, eq } from "drizzle-orm";
import { ensureQuestionRevisionTable, getDb } from "../../../../db";
import { questionRevisions } from "../../../../db/schema";
import type { ChoiceMode, Question, QuestionStatus } from "../../../question-model";

function parseRow(row: typeof questionRevisions.$inferSelect): Question {
  return {
    ...row,
    subjects: JSON.parse(row.subjects) as string[],
    alternatives: JSON.parse(row.alternatives) as string[],
    imageUrls: JSON.parse(row.imageUrls) as string[],
    contentBlocks: JSON.parse(row.contentBlocks),
    alternativeBlocks: JSON.parse(row.alternativeBlocks),
    auditTrail: JSON.parse(row.auditTrail),
    answerType: row.answerType as ChoiceMode,
    status: row.status as QuestionStatus,
  };
}

export async function GET() {
  try {
    await ensureQuestionRevisionTable();
    const rows = await getDb().select().from(questionRevisions).orderBy(desc(questionRevisions.updatedAt));
    return Response.json({ questions: rows.map(parseRow) });
  } catch (error) {
    return Response.json({ error: error instanceof Error ? error.message : "Não foi possível carregar as revisões." }, { status: 500 });
  }
}

export async function POST(request: Request) {
  try {
    const question = (await request.json()) as Question;
    if (!question.id || !question.school?.trim() || !question.year || !question.number || !question.content?.trim()) {
      return Response.json({ error: "Instituição, ano, número e enunciado são obrigatórios." }, { status: 400 });
    }

    await ensureQuestionRevisionTable();
    const values = {
      id: question.id,
      sourceRow: question.sourceRow || 0,
      school: question.school.trim(),
      year: Number(question.year),
      number: Number(question.number),
      subjects: JSON.stringify(question.subjects || []),
      answer: question.answer?.trim().toUpperCase() || "",
      answerType: question.answerType || "ABCDE",
      difficulty: question.difficulty || "",
      content: question.content.trim(),
      preview: question.content.trim().slice(0, 480),
      sourceDocument: question.sourceDocument || "Cadastro manual",
      sourceBookmark: question.sourceBookmark || "",
      hasTable: Boolean(question.hasTable),
      hasMedia: Boolean(question.hasMedia),
      hasMath: Boolean(question.hasMath),
      status: question.status || "review",
      isCustom: Boolean(question.isCustom),
      stem: question.stem || "",
      alternatives: JSON.stringify(question.alternatives || []),
      formula: question.formula || "",
      tableData: question.tableData || "",
      imageUrls: JSON.stringify(question.imageUrls || []),
      contentBlocks: JSON.stringify(question.contentBlocks || []),
      alternativeBlocks: JSON.stringify(question.alternativeBlocks || []),
      authenticatedAt: question.authenticatedAt || "",
      authenticatedBy: question.authenticatedBy || "",
      isLocked: Boolean(question.isLocked),
      lockedAt: question.lockedAt || "",
      lockedBy: question.lockedBy || "",
      lastUnlockReason: question.lastUnlockReason || "",
      auditTrail: JSON.stringify(question.auditTrail || []),
      updatedAt: new Date().toISOString(),
    };
    if (values.isLocked && (!values.authenticatedAt || !values.authenticatedBy || !values.lockedAt || !values.lockedBy)) {
      return Response.json({ error: "Uma questão travada precisa possuir os dados da autenticação administrativa." }, { status: 400 });
    }
    const existing = (await getDb().select().from(questionRevisions).where(eq(questionRevisions.id, question.id)).limit(1))[0];
    if (existing?.isLocked) {
      const protectedFields = ["school", "year", "number", "answer", "answerType", "content", "sourceDocument", "sourceBookmark", "hasTable", "hasMedia", "hasMath", "stem", "alternatives", "formula", "tableData", "imageUrls", "contentBlocks", "alternativeBlocks"] as const;
      const changedProtectedContent = protectedFields.some((field) => existing[field] !== values[field]);
      if (changedProtectedContent) {
        return Response.json({ error: "A questão está autenticada e travada. Desbloqueie-a antes de alterar o conteúdo." }, { status: 423 });
      }
      if (!values.isLocked && values.lastUnlockReason.trim().length < 5) {
        return Response.json({ error: "Informe um motivo de desbloqueio com pelo menos 5 caracteres." }, { status: 400 });
      }
    }
    await getDb().insert(questionRevisions).values(values).onConflictDoUpdate({
      target: questionRevisions.id,
      set: values,
    });
    return Response.json({ question: parseRow(values) });
  } catch (error) {
    return Response.json({ error: error instanceof Error ? error.message : "Não foi possível salvar a questão." }, { status: 500 });
  }
}

export async function DELETE(request: Request) {
  try {
    const id = new URL(request.url).searchParams.get("id");
    if (!id) return Response.json({ error: "Questão não informada." }, { status: 400 });
    await ensureQuestionRevisionTable();
    const existing = (await getDb().select().from(questionRevisions).where(eq(questionRevisions.id, id)).limit(1))[0];
    if (existing?.isLocked) return Response.json({ error: "Questões autenticadas precisam ser desbloqueadas antes da restauração." }, { status: 423 });
    await getDb().delete(questionRevisions).where(eq(questionRevisions.id, id));
    return Response.json({ ok: true });
  } catch (error) {
    return Response.json({ error: error instanceof Error ? error.message : "Não foi possível restaurar a questão." }, { status: 500 });
  }
}
