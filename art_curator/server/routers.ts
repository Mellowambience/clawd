import { COOKIE_NAME } from "@shared/const";
import { getSessionCookieOptions } from "./_core/cookies";
import { systemRouter } from "./_core/systemRouter";
import { publicProcedure, router, protectedProcedure } from "./_core/trpc";
import { getArtPiecesByUserId, getArtPieceById, getSocialAccountsByUserId, getScheduledPostsByUserId, getPostHistoryByUserId } from "./db";

export const appRouter = router({
  system: systemRouter,
  auth: router({
    me: publicProcedure.query(opts => opts.ctx.user),
    logout: publicProcedure.mutation(({ ctx }) => {
      const cookieOptions = getSessionCookieOptions(ctx.req);
      ctx.res.clearCookie(COOKIE_NAME, { ...cookieOptions, maxAge: -1 });
      return {
        success: true,
      } as const;
    }),
  }),

  artPieces: router({
    list: protectedProcedure.query(({ ctx }) => {
      return getArtPiecesByUserId(ctx.user.id);
    }),
    getById: protectedProcedure.input((val: any) => val.id).query(({ input }) => {
      return getArtPieceById(input);
    }),
  }),

  socialAccounts: router({
    list: protectedProcedure.query(({ ctx }) => {
      return getSocialAccountsByUserId(ctx.user.id);
    }),
  }),

  scheduledPosts: router({
    list: protectedProcedure.query(({ ctx }) => {
      return getScheduledPostsByUserId(ctx.user.id);
    }),
  }),

  postHistory: router({
    list: protectedProcedure.query(({ ctx }) => {
      return getPostHistoryByUserId(ctx.user.id);
    }),
  }),
});

export type AppRouter = typeof appRouter;
