import { sqliteTable, text, integer } from "drizzle-orm/sqlite-core";
export const snapshots = sqliteTable("snapshots", { id: text("id").primaryKey(), at: integer("at").notNull(), payload: text("payload").notNull() });
export const events = sqliteTable("events", { id: text("id").primaryKey(), at: integer("at").notNull(), payload: text("payload").notNull() });
