CREATE TABLE `events` (
	`id` text PRIMARY KEY NOT NULL,
	`at` integer NOT NULL,
	`payload` text NOT NULL
);
--> statement-breakpoint
CREATE TABLE `snapshots` (
	`id` text PRIMARY KEY NOT NULL,
	`at` integer NOT NULL,
	`payload` text NOT NULL
);
