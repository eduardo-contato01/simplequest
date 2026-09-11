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
      stem TEXT NOT NULL DEFAULT '',
      alternatives TEXT NOT NULL DEFAULT '[]',
      formula TEXT NOT NULL DEFAULT '',
      table_data TEXT NOT NULL DEFAULT '',
      image_urls TEXT NOT NULL DEFAULT '[]',
      content_blocks TEXT NOT NULL DEFAULT '[]',
      alternative_blocks TEXT NOT NULL DEFAULT '[]',
      authenticated_at TEXT NOT NULL DEFAULT '',
      authenticated_by TEXT NOT NULL DEFAULT '',
      is_locked INTEGER NOT NULL DEFAULT 0,
      locked_at TEXT NOT NULL DEFAULT '',
      locked_by TEXT NOT NULL DEFAULT '',
      last_unlock_reason TEXT NOT NULL DEFAULT '',
      audit_trail TEXT NOT NULL DEFAULT '[]',
      updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    )`),
    env.DB.prepare("CREATE INDEX IF NOT EXISTS idx_question_revisions_status ON question_revisions(status)"),
    env.DB.prepare("CREATE INDEX IF NOT EXISTS idx_question_revisions_school_year ON question_revisions(school, year)"),
  ]);

  const tableInfo = await env.DB.prepare("PRAGMA table_info(question_revisions)").all<{ name: string }>();
  const existingColumns = new Set(tableInfo.results.map((column) => column.name));
  const additions = [
    ["stem", "ALTER TABLE question_revisions ADD COLUMN stem TEXT NOT NULL DEFAULT ''"],
    ["alternatives", "ALTER TABLE question_revisions ADD COLUMN alternatives TEXT NOT NULL DEFAULT '[]'"],
    ["formula", "ALTER TABLE question_revisions ADD COLUMN formula TEXT NOT NULL DEFAULT ''"],
    ["table_data", "ALTER TABLE question_revisions ADD COLUMN table_data TEXT NOT NULL DEFAULT ''"],
    ["image_urls", "ALTER TABLE question_revisions ADD COLUMN image_urls TEXT NOT NULL DEFAULT '[]'"],
    ["content_blocks", "ALTER TABLE question_revisions ADD COLUMN content_blocks TEXT NOT NULL DEFAULT '[]'"],
    ["alternative_blocks", "ALTER TABLE question_revisions ADD COLUMN alternative_blocks TEXT NOT NULL DEFAULT '[]'"],
    ["authenticated_at", "ALTER TABLE question_revisions ADD COLUMN authenticated_at TEXT NOT NULL DEFAULT ''"],
    ["authenticated_by", "ALTER TABLE question_revisions ADD COLUMN authenticated_by TEXT NOT NULL DEFAULT ''"],
    ["is_locked", "ALTER TABLE question_revisions ADD COLUMN is_locked INTEGER NOT NULL DEFAULT 0"],
    ["locked_at", "ALTER TABLE question_revisions ADD COLUMN locked_at TEXT NOT NULL DEFAULT ''"],
    ["locked_by", "ALTER TABLE question_revisions ADD COLUMN locked_by TEXT NOT NULL DEFAULT ''"],
    ["last_unlock_reason", "ALTER TABLE question_revisions ADD COLUMN last_unlock_reason TEXT NOT NULL DEFAULT ''"],
    ["audit_trail", "ALTER TABLE question_revisions ADD COLUMN audit_trail TEXT NOT NULL DEFAULT '[]'"],
  ].filter(([name]) => !existingColumns.has(name));
  if (additions.length) await env.DB.batch(additions.map(([, statement]) => env.DB.prepare(statement)));
}
