export const COOKIE_NAME = "app_session_id";
export const ONE_YEAR_MS = 1000 * 60 * 60 * 24 * 365;
export const AXIOS_TIMEOUT_MS = 30_000;
export const UNAUTHED_ERR_MSG = "Please login (10001)";
export const NOT_ADMIN_ERR_MSG = "You do not have required permission (10002)";

/** MIST gateway (WebSocket). Use localhost for simulator; set to machine IP for physical device. */
export const MIST_GATEWAY_HOST =
  process.env.EXPO_PUBLIC_MIST_GATEWAY_HOST ?? "localhost";
export const MIST_GATEWAY_PORT = 18789;

/**
 * MIST API base URL for tRPC chat.
 * Set EXPO_PUBLIC_MIST_API_BASE_URL when deploying the Express server to a cloud host.
 * Example: "https://clawd-api.onrender.com" or "https://clawd.up.railway.app"
 * When empty, the client tries http://localhost:3000 as fallback.
 */
export const MIST_API_BASE_URL =
  process.env.EXPO_PUBLIC_MIST_API_BASE_URL ?? "";
