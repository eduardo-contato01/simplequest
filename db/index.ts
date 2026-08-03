import { env } from "cloudflare:workers";
import { drizzle } from "drizzle-orm/d1";
import * as schema from "./schema";

export function getDb() {
  if (!env.DB) {
    throw new Error(
      "Cloudflare D1 binding `DB` is unavailable. Set the `d1` field in .openai/hosting.json to `DB` or let your control plane inject the real binding values before using the database."
    );
  }

  return drizzle(env.DB, { schema });
}

export async function ensureQuestionRevisionTable() {
  if (!env.DB) throw new Error("Cloudflare D1 binding `DB` is unavailable.");
  await env.DB.batch([
    env.DB.prepare(`CREATE TABLE IF NOT EXISTS question_revisions (
      id TEXT PRIMARY KEY NOT NULL,
      source_row INTEGER NOT NULL DEFAULT 0,
      school TEXT NOT NULL,
      year INTEGER NOT NULL,
      number INTEGER NOT NULL,
      subjects TEXT NOT NULL DEFAULT '[]',
      answer TEXT NOT NULL DEFAULT '',
      answer_type TEXT NOT NULL DEFAULT 'ABCDE',
      difficulty TEXT NOT NULL DEFAULT '',
      content TEXT NOT NULL,
      preview TEXT NOT NULL DEFAULT '',
      source_document TEXT NOT NULL DEFAULT 'Cadastro manual',
      source_bookmark TEXT NOT NULL DEFAULT '',
      has_table INTEGER NOT NULL DEFAULT 0,
      has_media INTEGER NOT NULL DEFAULT 0,
      has_math INTEGER NOT NULL DEFAULT 0,
      status TEXT NOT NULL DEFAULT 'review',
      is_custom INTEGER NOT NULL DEFAULT 0,
      updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    )`),
    env.DB.prepare("CREATE INDEX IF NOT EXISTS idx_question_revisions_status ON question_revisions(status)"),
    env.DB.prepare("CREATE INDEX IF NOT EXISTS idx_question_revisions_school_year ON question_revisions(school, year)"),
  ]);
}
