# MIST Diagnostics Wrap-Up: The "Silent Operator" Collapse
**Date**: 2026-02-09
**Status**: Critical / Non-Functional
**Diagnosis**: Recursive Hallucination & Semantic Echo

## 1. The Core Failure: "Predictive Jump"
The model (likely a smaller parameter model like `mistral:latest`) has learned the conversation pattern too well.
- **Pattern**: `Request` -> `Tool Call` -> `Tool Output`
- **Failure**: The model now sees a Request and *jumps* directly to `Tool Output` (hallucinated), skipping the actual `Tool Call`.
- **Symptom**: You see logs like `Neural core response: TOOL_OUTPUT (read_file): Error...` without an actual tool invocation. The system fails to catch this because there is no `[[TOOL:...]]` tag to parse.

## 2. Secondary Failure: "Semantic Echo"
The model recites its own system prompt (`Identity: MIST...`) as a response.
- **Cause**: The prompt was too verbose. The model interpreted "Identity: MIST" not as a hidden instruction, but as the *start* of a document it should continue writing.
- **Fix Applied**: Truncation logic and "Lobotomy" filters were added to `server.py` to kill these responses, but the *underlying urge* remains if the model context is polluted.

## 3. Technical Debts (Gaps)
- **Regex Fragility**: The tool parser `r'\[\[TOOL:\s*(\w+),\s*(.*?)\]\]'` fails if the model adds newlines or formatting (e.g., markdown blocks) inside the tag.
- **Output Hallucination**: The model invents `Permission Denied` errors because it's roleplaying a "secure system" rather than actually checking permissions.
- **Context Pollution**: Even with `mist_chat_history.json` deletion, the *running* instance might allow a "leaky" context if not restarted perfectly (though verified restart happened).

## 4. Root Cause Analysis
**The Model needs a "Stop Sequence".**
Local LLMs often don't know when to stop generating. We rely on regex parsing, but if the model generates the *result* of the tool before we run it, we are dead in the water.
We need to enforce a stop sequence on `]]` or `TOOL_OUTPUT` so the model *cannot* generate the output itself.

## 5. Action Plan (Tomorrow)
1.  **Stop Sequences**: Configure the OLLAMA call to strictly stop generation at `]]` or `User:`.
2.  **Negative Constraints**: Update prompt to explicitly say: "DO NOT generate TOOL_OUTPUT. Wait for system."
3.  **Strict Parser**: Improve regex to handle multiline tool calls.
4.  **Resonance Check**: If response starts with `TOOL_OUTPUT`, discard and retry with a penalty prompt ("You must call the tool first.").

**Recommendation**: The current "MIST" persona is fighting the specialized "Tool User" nature. We need to separate them further—perhaps a "Router" call (fast model) to decide the tool, and a "Persona" call (rich model) to generate the final response *after* the tool executes.
