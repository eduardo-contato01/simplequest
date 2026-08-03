import { sql } from "drizzle-orm";
import { integer, sqliteTable, text } from "drizzle-orm/sqlite-core";

export const questionRevisions = sqliteTable("question_revisions", {
  id: text("id").primaryKey(),
  sourceRow: integer("source_row").notNull().default(0),
  school: text("school").notNull(),
  year: integer("year").notNull(),
  number: integer("number").notNull(),
  subjects: text("subjects").notNull().default("[]"),
  answer: text("answer").notNull().default(""),
  answerType: text("answer_type").notNull().default("ABCDE"),
  difficulty: text("difficulty").notNull().default(""),
  content: text("content").notNull(),
  preview: text("preview").notNull().default(""),
  sourceDocument: text("source_document").notNull().default("Cadastro manual"),
  sourceBookmark: text("source_bookmark").notNull().default(""),
  hasTable: integer("has_table", { mode: "boolean" }).notNull().default(false),
  hasMedia: integer("has_media", { mode: "boolean" }).notNull().default(false),
  hasMath: integer("has_math", { mode: "boolean" }).notNull().default(false),
  status: text("status").notNull().default("review"),
  isCustom: integer("is_custom", { mode: "boolean" }).notNull().default(false),
  updatedAt: text("updated_at").notNull().default(sql`CURRENT_TIMESTAMP`),
});
