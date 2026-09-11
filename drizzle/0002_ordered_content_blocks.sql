ALTER TABLE `question_revisions` ADD `content_blocks` text DEFAULT '[]' NOT NULL;--> statement-breakpoint
ALTER TABLE `question_revisions` ADD `alternative_blocks` text DEFAULT '[]' NOT NULL;
