import { z } from "zod";
import { publicProcedure, router } from "../_core/trpc";
import { ENV } from "../_core/env";

// ── Integration registry ─────────────────────────────────────────────────────
interface Integration {
  id: string;
  name: string;
  category: string;
  icon: string;
  connected: boolean;
  description: string;
  configurable: boolean;
}

/**
 * Build the live integration status based on actual server config.
 * Returns which services are actually available vs. which are stubs.
 */
function getIntegrations(): Integration[] {
  return [
    {
      id: "gemini",
      name: "Gemini AI",
      category: "AI",
      icon: "\uD83E\uDDE0",
      connected: !!(ENV.geminiApiKey && ENV.geminiApiKey.trim().length > 0),
      description: "Google Gemini for MIST's cloud intelligence",
      configurable: false,
    },
    {
      id: "ollama",
      name: "Ollama (Local)",
      category: "AI",
      icon: "\uD83E\uDD99",
      connected: false,
      description: "Local LLM via Ollama for offline MIST",
      configurable: false,
    },
    {
      id: "forge",
      name: "Forge / Manus",
      category: "AI",
      icon: "\uD83D\uDD28",
      connected: !!(ENV.forgeApiKey && ENV.forgeApiKey.trim().length > 0),
      description: "Forge API for tool execution",
      configurable: false,
    },
    {
      id: "database",
      name: "MySQL Database",
      category: "Storage",
      icon: "\uD83D\uDDC4\uFE0F",
      connected: !!(ENV.databaseUrl && ENV.databaseUrl.trim().length > 0),
      description: "Persistent storage for users, tasks, and chat history",
      configurable: false,
    },
    {
      id: "gateway",
      name: "MIST Gateway",
      category: "Core",
      icon: "\uD83C\uDF10",
      connected: false,
      description: "Python WebSocket gateway to local OpenClaw Engine",
      configurable: false,
    },
    {
      id: "calendar",
      name: "Calendar",
      category: "Productivity",
      icon: "\uD83D\uDCC5",
      connected: false,
      description: "Manage your events and schedule",
      configurable: true,
    },
    {
      id: "email",
      name: "Email",
      category: "Communication",
      icon: "\uD83D\uDCE7",
      connected: false,
      description: "Send and read emails",
      configurable: true,
    },
    {
      id: "github",
      name: "GitHub",
      category: "Development",
      icon: "\uD83D\uDC19",
      connected: true,
      description: "Repository management and bounty tracking",
      configurable: false,
    },
  ];
}

// ── Integrations router ──────────────────────────────────────────────────────
export const integrationsRouter = router({
  /** List all integrations with live status */
  list: publicProcedure.query(() => {
    return {
      integrations: getIntegrations(),
      connectedCount: getIntegrations().filter((i) => i.connected).length,
      totalCount: getIntegrations().length,
    };
  }),

  /** Check health of a specific integration */
  health: publicProcedure
    .input(z.object({ integrationId: z.string() }))
    .query(async ({ input }) => {
      const integration = getIntegrations().find(
        (i) => i.id === input.integrationId,
      );
      if (!integration) {
        return { found: false, healthy: false, message: "Integration not found" };
      }

      // For Gemini, do a real health check
      if (integration.id === "gemini" && integration.connected) {
        try {
          const resp = await fetch(
            "https://generativelanguage.googleapis.com/v1beta/openai/models",
            {
              headers: {
                authorization: `Bearer ${ENV.geminiApiKey}`,
              },
            },
          );
          return {
            found: true,
            healthy: resp.ok,
            message: resp.ok ? "Gemini API responding" : `Status ${resp.status}`,
          };
        } catch (err) {
          return {
            found: true,
            healthy: false,
            message: err instanceof Error ? err.message : "Connection failed",
          };
        }
      }

      return {
        found: true,
        healthy: integration.connected,
        message: integration.connected
          ? "Connected"
          : "Not configured",
      };
    }),

  /** Server info — returns runtime environment details */
  serverInfo: publicProcedure.query(() => {
    return {
      nodeVersion: process.version,
      uptime: Math.floor(process.uptime()),
      memoryUsage: Math.floor(process.memoryUsage().heapUsed / 1024 / 1024),
      environment: ENV.isProduction ? "production" : "development",
    };
  }),
});
