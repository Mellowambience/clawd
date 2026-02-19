import { COOKIE_NAME } from "../shared/const.js";
import { getSessionCookieOptions } from "./_core/cookies";
import { systemRouter } from "./_core/systemRouter";
import { publicProcedure, router } from "./_core/trpc";
import { chatRouter } from "./routes/chat";
import { taskRouter } from "./routes/tasks";
import { settingsRouter } from "./routes/settings";
import { integrationsRouter } from "./routes/integrations";

export const appRouter = router({
  // if you need to use socket.io, read and register route in server/_core/index.ts, all api should start with '/api/' so that the gateway can route correctly
  system: systemRouter,
  auth: router({
    me: publicProcedure.query((opts) => opts.ctx.user),
    logout: publicProcedure.mutation(({ ctx }) => {
      const cookieOptions = getSessionCookieOptions(ctx.req);
      ctx.res.clearCookie(COOKIE_NAME, { ...cookieOptions, maxAge: -1 });
      return {
        success: true,
      } as const;
    }),
  }),

  // ── MIST chat ─────────────────────────────────────────────────────────
  chat: chatRouter,

  // ── Tasks ─────────────────────────────────────────────────────────────
  tasks: taskRouter,

  // ── Settings ──────────────────────────────────────────────────────────
  settings: settingsRouter,

  // ── Integrations ──────────────────────────────────────────────────────
  integrations: integrationsRouter,
});

export type AppRouter = typeof appRouter;
