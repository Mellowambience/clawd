import { ENV } from "./env";

export type Role = "system" | "user" | "assistant" | "tool" | "function";

export type TextContent = {
  type: "text";
  text: string;
};

export type ImageContent = {
  type: "image_url";
  image_url: {
    url: string;
    detail?: "auto" | "low" | "high";
  };
};

export type FileContent = {
  type: "file_url";
  file_url: {
    url: string;
    mime_type?: "audio/mpeg" | "audio/wav" | "application/pdf" | "audio/mp4" | "video/mp4";
  };
};

export type MessageContent = string | TextContent | ImageContent | FileContent;

export type Message = {
  role: Role;
  content: MessageContent | MessageContent[];
  name?: string;
  tool_call_id?: string;
};

export type Tool = {
  type: "function";
  function: {
    name: string;
    description?: string;
    parameters?: Record<string, unknown>;
  };
};

export type ToolChoicePrimitive = "none" | "auto" | "required";
export type ToolChoiceByName = { name: string };
export type ToolChoiceExplicit = {
  type: "function";
  function: {
    name: string;
  };
};

export type ToolChoice = ToolChoicePrimitive | ToolChoiceByName | ToolChoiceExplicit;

export type InvokeParams = {
  messages: Message[];
  tools?: Tool[];
  toolChoice?: ToolChoice;
  tool_choice?: ToolChoice;
  maxTokens?: number;
  max_tokens?: number;
  outputSchema?: OutputSchema;
  output_schema?: OutputSchema;
  responseFormat?: ResponseFormat;
  response_format?: ResponseFormat;
};

export type ToolCall = {
  id: string;
  type: "function";
  function: {
    name: string;
    arguments: string;
  };
};

export type InvokeResult = {
  id: string;
  created: number;
  model: string;
  choices: Array<{
    index: number;
    message: {
      role: Role;
      content: string | Array<TextContent | ImageContent | FileContent>;
      tool_calls?: ToolCall[];
    };
    finish_reason: string | null;
  }>;
  usage?: {
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
  };
};

export type JsonSchema = {
  name: string;
  schema: Record<string, unknown>;
  strict?: boolean;
};

export type OutputSchema = JsonSchema;

export type ResponseFormat =
  | { type: "text" }
  | { type: "json_object" }
  | { type: "json_schema"; json_schema: JsonSchema };

const ensureArray = (value: MessageContent | MessageContent[]): MessageContent[] =>
  Array.isArray(value) ? value : [value];

const normalizeContentPart = (part: MessageContent): TextContent | ImageContent | FileContent => {
  if (typeof part === "string") {
    return { type: "text", text: part };
  }

  if (part.type === "text") {
    return part;
  }

  if (part.type === "image_url") {
    return part;
  }

  if (part.type === "file_url") {
    return part;
  }

  throw new Error("Unsupported message content part");
};

const normalizeMessage = (message: Message) => {
  const { role, name, tool_call_id } = message;

  if (role === "tool" || role === "function") {
    const content = ensureArray(message.content)
      .map((part) => (typeof part === "string" ? part : JSON.stringify(part)))
      .join("\n");

    return {
      role,
      name,
      tool_call_id,
      content,
    };
  }

  const contentParts = ensureArray(message.content).map(normalizeContentPart);

  // If there's only text content, collapse to a single string for compatibility
  if (contentParts.length === 1 && contentParts[0].type === "text") {
    return {
      role,
      name,
      content: contentParts[0].text,
    };
  }

  return {
    role,
    name,
    content: contentParts,
  };
};

const normalizeToolChoice = (
  toolChoice: ToolChoice | undefined,
  tools: Tool[] | undefined,
): "none" | "auto" | ToolChoiceExplicit | undefined => {
  if (!toolChoice) return undefined;

  if (toolChoice === "none" || toolChoice === "auto") {
    return toolChoice;
  }

  if (toolChoice === "required") {
    if (!tools || tools.length === 0) {
      throw new Error("tool_choice 'required' was provided but no tools were configured");
    }

    if (tools.length > 1) {
      throw new Error(
        "tool_choice 'required' needs a single tool or specify the tool name explicitly",
      );
    }

    return {
      type: "function",
      function: { name: tools[0].function.name },
    };
  }

  if ("name" in toolChoice) {
    return {
      type: "function",
      function: { name: toolChoice.name },
    };
  }

  return toolChoice;
};

// ─── Provider Definitions ──────────────────────────────────────────────────────
// Each provider in the cascade is defined with its URL, key(s), model, and name.
// On 429/quota errors, the system automatically falls through to the next provider.

type Provider = {
  name: string;
  url: string;
  keys: string[];
  model: string;
  extraHeaders?: Record<string, string>;
};

/**
 * Build the ordered provider cascade.
 * Priority: Gemini (2-key rotation) → Groq → Together AI → OpenRouter → Forge/Manus
 * Only providers with at least one valid key are included.
 */
const buildProviderCascade = (): Provider[] => {
  const providers: Provider[] = [];

  // 1. Gemini — primary provider, supports 2-key rotation on 429
  const geminiKeys = [ENV.geminiApiKey, ENV.geminiApiKey2].filter((k) => k && k.trim().length > 0);
  if (geminiKeys.length > 0) {
    providers.push({
      name: "Gemini",
      url: "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions",
      keys: geminiKeys,
      model: "gemini-2.0-flash",
    });
  }

  // 2. Groq — Llama 3.3 70B Versatile, free tier (30 RPM / 100K TPD)
  if (ENV.groqApiKey && ENV.groqApiKey.trim().length > 0) {
    providers.push({
      name: "Groq",
      url: "https://api.groq.com/openai/v1/chat/completions",
      keys: [ENV.groqApiKey],
      model: "llama-3.3-70b-versatile",
    });
  }

  // 3. Together AI — Llama 3.3 70B Instruct Turbo (free variant)
  if (ENV.togetherApiKey && ENV.togetherApiKey.trim().length > 0) {
    providers.push({
      name: "Together AI",
      url: "https://api.together.xyz/v1/chat/completions",
      keys: [ENV.togetherApiKey],
      model: "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
    });
  }

  // 4. OpenRouter — Llama 3.3 70B Instruct (free variant)
  if (ENV.openrouterApiKey && ENV.openrouterApiKey.trim().length > 0) {
    providers.push({
      name: "OpenRouter",
      url: "https://openrouter.ai/api/v1/chat/completions",
      keys: [ENV.openrouterApiKey],
      model: "meta-llama/llama-3.3-70b-instruct:free",
      extraHeaders: {
        "HTTP-Referer": "https://github.com/Mellowambience/clawd",
        "X-Title": "MIST",
      },
    });
  }

  // 5. Moonshot (Kimi) — legacy, kept for backward compatibility
  if (ENV.moonshotApiKey && ENV.moonshotApiKey.trim().length > 0) {
    providers.push({
      name: "Moonshot",
      url: "https://api.moonshot.cn/v1/chat/completions",
      keys: [ENV.moonshotApiKey],
      model: "moonshot-v1-8k",
    });
  }

  // 6. Forge/Manus — ultimate fallback
  if (ENV.forgeApiKey && ENV.forgeApiKey.trim().length > 0) {
    const baseUrl = ENV.forgeApiUrl && ENV.forgeApiUrl.trim().length > 0
      ? ENV.forgeApiUrl.replace(/\/+$/, "")
      : "https://forge.manus.im";
    providers.push({
      name: "Forge",
      url: `${baseUrl}/v1/chat/completions`,
      keys: [ENV.forgeApiKey],
      model: "gemini-2.5-flash",
    });
  }

  return providers;
};

const normalizeResponseFormat = ({
  responseFormat,
  response_format,
  outputSchema,
  output_schema,
}: {
  responseFormat?: ResponseFormat;
  response_format?: ResponseFormat;
  outputSchema?: OutputSchema;
  output_schema?: OutputSchema;
}):
  | { type: "json_schema"; json_schema: JsonSchema }
  | { type: "text" }
  | { type: "json_object" }
  | undefined => {
  const explicitFormat = responseFormat || response_format;
  if (explicitFormat) {
    if (explicitFormat.type === "json_schema" && !explicitFormat.json_schema?.schema) {
      throw new Error("responseFormat json_schema requires a defined schema object");
    }
    return explicitFormat;
  }

  const schema = outputSchema || output_schema;
  if (!schema) return undefined;

  if (!schema.name || !schema.schema) {
    throw new Error("outputSchema requires both name and schema");
  }

  return {
    type: "json_schema",
    json_schema: {
      name: schema.name,
      schema: schema.schema,
      ...(typeof schema.strict === "boolean" ? { strict: schema.strict } : {}),
    },
  };
};

/**
 * Invoke the LLM API with automatic provider cascade.
 *
 * On 429/quota errors, automatically falls through to the next provider.
 * Gemini supports multi-key rotation within its own provider entry.
 *
 * Cascade order: Gemini → Groq → Together AI → OpenRouter → Moonshot → Forge
 */
export async function invokeLLM(params: InvokeParams): Promise<InvokeResult> {
  const providers = buildProviderCascade();

  if (providers.length === 0) {
    throw new Error(
      "No LLM API key configured. Set GEMINI_API_KEY, GROQ_API_KEY, TOGETHER_API_KEY, OPENROUTER_API_KEY, or BUILT_IN_FORGE_API_KEY.",
    );
  }

  const {
    messages,
    tools,
    toolChoice,
    tool_choice,
    outputSchema,
    output_schema,
    responseFormat,
    response_format,
  } = params;

  const normalizedMessages = messages.map(normalizeMessage);

  const normalizedToolChoice = normalizeToolChoice(toolChoice || tool_choice, tools);

  const normalizedResponseFormat = normalizeResponseFormat({
    responseFormat,
    response_format,
    outputSchema,
    output_schema,
  });

  let lastError: Error | undefined;

  for (const provider of providers) {
    // Try each key for this provider (Gemini has 2, others have 1)
    for (const apiKey of provider.keys) {
      const payload: Record<string, unknown> = {
        model: provider.model,
        messages: normalizedMessages,
      };

      if (tools && tools.length > 0) {
        payload.tools = tools;
      }

      if (normalizedToolChoice) {
        payload.tool_choice = normalizedToolChoice;
      }

      payload.max_tokens = 32768;

      if (normalizedResponseFormat) {
        payload.response_format = normalizedResponseFormat;
      }

      try {
        const headers: Record<string, string> = {
          "content-type": "application/json",
          authorization: `Bearer ${apiKey}`,
          ...(provider.extraHeaders ?? {}),
        };

        const response = await fetch(provider.url, {
          method: "POST",
          headers,
          body: JSON.stringify(payload),
        });

        if (response.ok) {
          const result = (await response.json()) as InvokeResult;
          // Log which provider served the request (useful for debugging)
          console.log(`[llm] ${provider.name} (${provider.model}) — OK`);
          return result;
        }

        const errorText = await response.text();
        const is429 = response.status === 429;
        const isQuotaError = is429 || response.status === 503;

        lastError = new Error(
          `[llm] ${provider.name} failed: ${response.status} ${response.statusText} — ${errorText}`,
        );

        if (isQuotaError) {
          console.warn(
            `[llm] ${provider.name} quota exhausted (${response.status}), trying next...`,
          );
          continue; // Try next key or next provider
        }

        // Non-quota error — still cascade to next provider
        // (auth errors, bad request, etc. might be provider-specific)
        console.warn(
          `[llm] ${provider.name} error (${response.status}), cascading...`,
        );
        break; // Skip remaining keys for this provider, try next provider
      } catch (err) {
        // Network error — cascade to next provider
        lastError = err instanceof Error ? err : new Error(String(err));
        console.warn(`[llm] ${provider.name} network error: ${lastError.message}`);
        break;
      }
    }
  }

  throw lastError ?? new Error("LLM invoke failed: all providers exhausted");
}
