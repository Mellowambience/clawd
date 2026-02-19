import { z } from "zod";
import { publicProcedure, router } from "../_core/trpc";

// ── In-memory settings storage ───────────────────────────────────────────────
interface UserSettings {
  notifications: boolean;
  haptics: boolean;
  aiModel: "gemini" | "ollama" | "auto";
  theme: "system" | "light" | "dark";
}

const DEFAULT_SETTINGS: UserSettings = {
  notifications: true,
  haptics: true,
  aiModel: "auto",
  theme: "system",
};

const userSettings = new Map<string, UserSettings>();

function getSettings(userId: string): UserSettings {
  if (!userSettings.has(userId)) {
    userSettings.set(userId, { ...DEFAULT_SETTINGS });
  }
  return userSettings.get(userId)!;
}

// ── Settings router ──────────────────────────────────────────────────────────
export const settingsRouter = router({
  /** Get current settings */
  get: publicProcedure
    .input(z.object({ userId: z.string().default("default") }))
    .query(({ input }) => {
      return getSettings(input.userId);
    }),

  /** Update one or more settings */
  update: publicProcedure
    .input(
      z.object({
        userId: z.string().default("default"),
        notifications: z.boolean().optional(),
        haptics: z.boolean().optional(),
        aiModel: z.enum(["gemini", "ollama", "auto"]).optional(),
        theme: z.enum(["system", "light", "dark"]).optional(),
      }),
    )
    .mutation(({ input }) => {
      const { userId, ...updates } = input;
      const current = getSettings(userId);
      const filtered = Object.fromEntries(
        Object.entries(updates).filter(([_, v]) => v !== undefined),
      );
      Object.assign(current, filtered);
      return current;
    }),

  /** Reset to defaults */
  reset: publicProcedure
    .input(z.object({ userId: z.string().default("default") }))
    .mutation(({ input }) => {
      userSettings.set(input.userId, { ...DEFAULT_SETTINGS });
      return DEFAULT_SETTINGS;
    }),
});
