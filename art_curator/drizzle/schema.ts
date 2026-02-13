import { sqliteTable, text, integer } from "drizzle-orm/sqlite-core";
import { sql } from "drizzle-orm";

/**
 * Core user table backing auth flow.
 */
export const users = sqliteTable("users", {
  id: integer("id").primaryKey({ autoIncrement: true }),
  openId: text("openId").notNull().unique(),
  name: text("name"),
  email: text("email"),
  loginMethod: text("loginMethod"),
  role: text("role", { enum: ["user", "admin"] }).default("user").notNull(),
  createdAt: integer("createdAt", { mode: "timestamp" }).default(sql`(unixepoch())`).notNull(),
  updatedAt: integer("updatedAt", { mode: "timestamp" }).default(sql`(unixepoch())`).$onUpdate(() => new Date()).notNull(),
  lastSignedIn: integer("lastSignedIn", { mode: "timestamp" }).default(sql`(unixepoch())`).notNull(),
});

export type User = typeof users.$inferSelect;
export type InsertUser = typeof users.$inferInsert;

/**
 * Social media accounts connected to the app
 */
export const socialAccounts = sqliteTable("socialAccounts", {
  id: integer("id").primaryKey({ autoIncrement: true }),
  userId: integer("userId").notNull(),
  platform: text("platform", { enum: ["x", "instagram", "facebook"] }).notNull(),
  accountName: text("accountName").notNull(),
  accountId: text("accountId").notNull(),
  accessToken: text("accessToken").notNull(),
  refreshToken: text("refreshToken"),
  tokenExpiresAt: integer("tokenExpiresAt", { mode: "timestamp" }),
  isActive: integer("isActive", { mode: "boolean" }).default(true).notNull(),
  metadata: text("metadata", { mode: "json" }),
  createdAt: integer("createdAt", { mode: "timestamp" }).default(sql`(unixepoch())`).notNull(),
  updatedAt: integer("updatedAt", { mode: "timestamp" }).default(sql`(unixepoch())`).$onUpdate(() => new Date()).notNull(),
});

export type SocialAccount = typeof socialAccounts.$inferSelect;
export type InsertSocialAccount = typeof socialAccounts.$inferInsert;

/**
 * Original art pieces uploaded by user
 */
export const artPieces = sqliteTable("artPieces", {
  id: integer("id").primaryKey({ autoIncrement: true }),
  userId: integer("userId").notNull(),
  title: text("title").notNull(),
  description: text("description"),
  tags: text("tags"),
  originalImageUrl: text("originalImageUrl").notNull(),
  originalImageKey: text("originalImageKey").notNull(),
  width: integer("width"),
  height: integer("height"),
  fileSize: integer("fileSize"),
  mimeType: text("mimeType"),
  status: text("status", { enum: ["draft", "approved", "rejected", "archived"] }).default("draft").notNull(),
  createdAt: integer("createdAt", { mode: "timestamp" }).default(sql`(unixepoch())`).notNull(),
  updatedAt: integer("updatedAt", { mode: "timestamp" }).default(sql`(unixepoch())`).$onUpdate(() => new Date()).notNull(),
});

export type ArtPiece = typeof artPieces.$inferSelect;
export type InsertArtPiece = typeof artPieces.$inferInsert;

/**
 * Generated variants of art pieces
 */
export const artVariants = sqliteTable("artVariants", {
  id: integer("id").primaryKey({ autoIncrement: true }),
  artPieceId: integer("artPieceId").notNull(),
  variantType: text("variantType", {
    enum: ["original", "upscaled", "cropped", "inverted", "compressed_jpg", "compressed_webp", "instagram_portrait", "instagram_landscape", "x_square", "x_wide"]
  }).notNull(),
  imageUrl: text("imageUrl").notNull(),
  imageKey: text("imageKey").notNull(),
  width: integer("width"),
  height: integer("height"),
  fileSize: integer("fileSize"),
  mimeType: text("mimeType"),
  createdAt: integer("createdAt", { mode: "timestamp" }).default(sql`(unixepoch())`).notNull(),
});

export type ArtVariant = typeof artVariants.$inferSelect;
export type InsertArtVariant = typeof artVariants.$inferInsert;

/**
 * Scheduled posts ready to be published
 */
export const scheduledPosts = sqliteTable("scheduledPosts", {
  id: integer("id").primaryKey({ autoIncrement: true }),
  userId: integer("userId").notNull(),
  socialAccountId: integer("socialAccountId").notNull(),
  artPieceId: integer("artPieceId"),
  caption: text("caption").notNull(),
  hashtags: text("hashtags"),
  platforms: text("platforms").notNull(),
  scheduledAt: integer("scheduledAt", { mode: "timestamp" }).notNull(),
  status: text("status", { enum: ["draft", "scheduled", "published", "failed", "cancelled"] }).default("draft").notNull(),
  errorMessage: text("errorMessage"),
  publishedAt: integer("publishedAt", { mode: "timestamp" }),
  createdAt: integer("createdAt", { mode: "timestamp" }).default(sql`(unixepoch())`).notNull(),
  updatedAt: integer("updatedAt", { mode: "timestamp" }).default(sql`(unixepoch())`).$onUpdate(() => new Date()).notNull(),
});

export type ScheduledPost = typeof scheduledPosts.$inferSelect;
export type InsertScheduledPost = typeof scheduledPosts.$inferInsert;

/**
 * Published posts with platform-specific IDs and engagement data
 */
export const postHistory = sqliteTable("postHistory", {
  id: integer("id").primaryKey({ autoIncrement: true }),
  scheduledPostId: integer("scheduledPostId"),
  userId: integer("userId").notNull(),
  platform: text("platform", { enum: ["x", "instagram", "facebook"] }).notNull(),
  platformPostId: text("platformPostId").notNull(),
  artPieceId: integer("artPieceId"),
  caption: text("caption"),
  hashtags: text("hashtags"),
  status: text("status", { enum: ["published", "failed", "deleted"] }).default("published").notNull(),
  publishedAt: integer("publishedAt", { mode: "timestamp" }).notNull(),
  engagement: text("engagement", { mode: "json" }),
  errorMessage: text("errorMessage"),
  createdAt: integer("createdAt", { mode: "timestamp" }).default(sql`(unixepoch())`).notNull(),
});

export type PostHistory = typeof postHistory.$inferSelect;
export type InsertPostHistory = typeof postHistory.$inferInsert;

/**
 * Mapping between scheduled posts and their media files
 */
export const postMediaMapping = sqliteTable("postMediaMapping", {
  id: integer("id").primaryKey({ autoIncrement: true }),
  scheduledPostId: integer("scheduledPostId").notNull(),
  artVariantId: integer("artVariantId").notNull(),
  displayOrder: integer("displayOrder").default(0).notNull(),
  createdAt: integer("createdAt", { mode: "timestamp" }).default(sql`(unixepoch())`).notNull(),
});

export type PostMediaMapping = typeof postMediaMapping.$inferSelect;
export type InsertPostMediaMapping = typeof postMediaMapping.$inferInsert;
