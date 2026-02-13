export const CLOUD_LIMIT_RE = /(cloud-based|don't have direct access|cannot access your (?:device|computer|files)|can't access your local files|no direct access to your .*storage)/i;
export const LOCAL_REQUEST_RE = /(create|make|write|read|open|show|delete|remove|find|list|run|execute|edit|modify).*(file|\.md|desktop|computer|workspace|path|command)/i;

export function normalizeGatewayReply(message, userMessage) {
    const raw = typeof message === 'string' ? message.trim() : '';
    if (!raw) {
        return { text: '', rewritten: false };
    }
    if (CLOUD_LIMIT_RE.test(raw) && LOCAL_REQUEST_RE.test(userMessage || '')) {
        return {
            text: 'Local runtime override: this session can execute verified local actions. Use an explicit command like `create MIST.md on my desktop with ...`, `read MIST.md on my desktop`, or `run command: whoami`.',
            rewritten: true,
        };
    }
    return { text: raw, rewritten: false };
}

export async function resolveGatewayReply({ userMessage, assistantMessage, validateFn }) {
    let text = assistantMessage;
    let rewritten = false;
    let violations = [];
    let source = 'server_validator';

    try {
        const validation = await validateFn(userMessage, assistantMessage);
        if (!validation.valid) {
            rewritten = true;
            violations = Array.isArray(validation.violations) ? validation.violations : [];
        }
        text = validation.normalized_message || assistantMessage;
    } catch (_error) {
        const fallback = normalizeGatewayReply(assistantMessage, userMessage);
        text = fallback.text;
        rewritten = fallback.rewritten;
        if (rewritten) {
            violations = ['client_fallback_guardrail'];
        }
        source = 'client_fallback';
    }

    return { text, rewritten, violations, source };
}
