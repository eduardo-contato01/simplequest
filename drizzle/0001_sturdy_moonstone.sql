ALTER TABLE `question_revisions` ADD `stem` text DEFAULT '' NOT NULL;--> statement-breakpoint
ALTER TABLE `question_revisions` ADD `alternatives` text DEFAULT '[]' NOT NULL;--> statement-breakpoint
ALTER TABLE `question_revisions` ADD `formula` text DEFAULT '' NOT NULL;--> statement-breakpoint
ALTER TABLE `question_revisions` ADD `table_data` text DEFAULT '' NOT NULL;--> statement-breakpoint
ALTER TABLE `question_revisions` ADD `image_urls` text DEFAULT '[]' NOT NULL;