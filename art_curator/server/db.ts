import { eq, sql } from "drizzle-orm";
import { drizzle } from "drizzle-orm/better-sqlite3";
import Database from "better-sqlite3";
import { InsertUser, users, artPieces, InsertArtPiece, artVariants, InsertArtVariant, socialAccounts, InsertSocialAccount, scheduledPosts, InsertScheduledPost, postHistory, InsertPostHistory } from "../drizzle/schema";
import { ENV } from './_core/env';

let _db: ReturnType<typeof drizzle> | null = null;

// Lazily create the drizzle instance so local tooling can run without a DB.
export async function getDb() {
  if (!_db) {
    try {
      const dbPath = process.env.DATABASE_URL || "sqlite.db";
      const sqlite = new Database(dbPath);
      _db = drizzle(sqlite);
    } catch (error) {
      console.warn("[Database] Failed to connect:", error);
      _db = null;
    }
  }
  return _db;
}

export async function upsertUser(user: InsertUser): Promise<void> {
  if (!user.openId) {
    throw new Error("User openId is required for upsert");
  }

  const db = await getDb();
  if (!db) {
    console.warn("[Database] Cannot upsert user: database not available");
    return;
  }

  try {
    const values: InsertUser = {
      openId: user.openId,
    };
    const updateSet: Record<string, unknown> = {};

    const textFields = ["name", "email", "loginMethod"] as const;
    type TextField = (typeof textFields)[number];

    const assignNullable = (field: TextField) => {
      const value = user[field];
      if (value === undefined) return;
      const normalized = value ?? null;
      values[field] = normalized;
      updateSet[field] = normalized;
    };

    textFields.forEach(assignNullable);

    if (user.lastSignedIn !== undefined) {
      values.lastSignedIn = user.lastSignedIn;
      updateSet.lastSignedIn = user.lastSignedIn;
    }
    if (user.role !== undefined) {
      values.role = user.role;
      updateSet.role = user.role;
    } else if (user.openId === ENV.ownerOpenId) {
      values.role = 'admin';
      updateSet.role = 'admin';
    }

    if (!values.lastSignedIn) {
      values.lastSignedIn = new Date();
    }

    if (Object.keys(updateSet).length === 0) {
      updateSet.lastSignedIn = new Date();
    }

    await db.insert(users).values(values).onConflictDoUpdate({
      target: users.openId,
      set: updateSet,
    });
  } catch (error) {
    console.error("[Database] Failed to upsert user:", error);
    throw error;
  }
}

export async function getUserByOpenId(openId: string) {
  const db = await getDb();
  if (!db) {
    console.warn("[Database] Cannot get user: database not available");
    return undefined;
  }

  const result = await db.select().from(users).where(eq(users.openId, openId)).limit(1);

  return result.length > 0 ? result[0] : undefined;
}

// Art piece queries
export async function getArtPiecesByUserId(userId: number) {
  const db = await getDb();
  if (!db) return [];
  return db.select().from(artPieces).where(eq(artPieces.userId, userId));
}

export async function getArtPieceById(id: number) {
  const db = await getDb();
  if (!db) return undefined;
  const result = await db.select().from(artPieces).where(eq(artPieces.id, id)).limit(1);
  return result[0];
}

export async function createArtPiece(piece: InsertArtPiece) {
  const db = await getDb();
  if (!db) throw new Error("Database not available");
  const result = await db.insert(artPieces).values(piece).returning();
  return result;
}

// Art variant queries
export async function getArtVariantsByPieceId(artPieceId: number) {
  const db = await getDb();
  if (!db) return [];
  return db.select().from(artVariants).where(eq(artVariants.artPieceId, artPieceId));
}

export async function createArtVariant(variant: InsertArtVariant) {
  const db = await getDb();
  if (!db) throw new Error("Database not available");
  return db.insert(artVariants).values(variant).returning();
}

// Social account queries
export async function getSocialAccountsByUserId(userId: number) {
  const db = await getDb();
  if (!db) return [];
  return db.select().from(socialAccounts).where(eq(socialAccounts.userId, userId));
}

export async function getSocialAccountById(id: number) {
  const db = await getDb();
  if (!db) return undefined;
  const result = await db.select().from(socialAccounts).where(eq(socialAccounts.id, id)).limit(1);
  return result[0];
}

export async function createSocialAccount(account: InsertSocialAccount) {
  const db = await getDb();
  if (!db) throw new Error("Database not available");
  return db.insert(socialAccounts).values(account).returning();
}

// Scheduled post queries
export async function getScheduledPostsByUserId(userId: number) {
  const db = await getDb();
  if (!db) return [];
  return db.select().from(scheduledPosts).where(eq(scheduledPosts.userId, userId));
}

export async function getScheduledPostsForPublishing() {
  const db = await getDb();
  if (!db) return [];
  return db.select().from(scheduledPosts)
    .where(eq(scheduledPosts.status, "scheduled"));
}

export async function createScheduledPost(post: InsertScheduledPost) {
  const db = await getDb();
  if (!db) throw new Error("Database not available");
  return db.insert(scheduledPosts).values(post).returning();
}

export async function updateScheduledPostStatus(id: number, status: string, errorMessage?: string) {
  const db = await getDb();
  if (!db) throw new Error("Database not available");
  return db.update(scheduledPosts).set({ status: status as any, errorMessage }).where(eq(scheduledPosts.id, id)).returning();
}

// Post history queries
export async function getPostHistoryByUserId(userId: number) {
  const db = await getDb();
  if (!db) return [];
  return db.select().from(postHistory).where(eq(postHistory.userId, userId));
}

export async function createPostHistory(post: InsertPostHistory) {
  const db = await getDb();
  if (!db) throw new Error("Database not available");
  return db.insert(postHistory).values(post).returning();
}
