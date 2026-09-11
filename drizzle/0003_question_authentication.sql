ALTER TABLE `question_revisions` ADD `authenticated_at` text DEFAULT '' NOT NULL;--> statement-breakpoint
ALTER TABLE `question_revisions` ADD `authenticated_by` text DEFAULT '' NOT NULL;--> statement-breakpoint
ALTER TABLE `question_revisions` ADD `is_locked` integer DEFAULT 0 NOT NULL;--> statement-breakpoint
ALTER TABLE `question_revisions` ADD `locked_at` text DEFAULT '' NOT NULL;--> statement-breakpoint
ALTER TABLE `question_revisions` ADD `locked_by` text DEFAULT '' NOT NULL;--> statement-breakpoint
ALTER TABLE `question_revisions` ADD `last_unlock_reason` text DEFAULT '' NOT NULL;--> statement-breakpoint
ALTER TABLE `question_revisions` ADD `audit_trail` text DEFAULT '[]' NOT NULL;
