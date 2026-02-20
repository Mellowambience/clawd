export const ENV = {
  appId: process.env.VITE_APP_ID ?? "",
  cookieSecret: process.env.JWT_SECRET ?? "",
  databaseUrl: process.env.DATABASE_URL ?? "",
  oAuthServerUrl: process.env.OAUTH_SERVER_URL ?? "",
  ownerOpenId: process.env.OWNER_OPEN_ID ?? "",
  isProduction: process.env.NODE_ENV === "production",

  // LLM provider — supports Forge (Manus) or direct Gemini
  forgeApiUrl: process.env.BUILT_IN_FORGE_API_URL ?? "",
  forgeApiKey: process.env.BUILT_IN_FORGE_API_KEY ?? "",

  // Direct Gemini support — used when Forge keys are not set
  // GEMINI_API_KEY_2 is a fallback key for when the primary hits daily quota
  geminiApiKey: process.env.GEMINI_API_KEY ?? "",
  geminiApiKey2: process.env.GEMINI_API_KEY_2 ?? "",

  // Moonshot (Kimi) support
  moonshotApiKey: process.env.MOONSHOT_API_KEY ?? "",

  // Fallback LLM providers — cascade on quota exhaustion
  groqApiKey: process.env.GROQ_API_KEY ?? "",
  togetherApiKey: process.env.TOGETHER_API_KEY ?? "",
  openrouterApiKey: process.env.OPENROUTER_API_KEY ?? "",
};
