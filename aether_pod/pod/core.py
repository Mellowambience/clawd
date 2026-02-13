import os
import requests
import json
import re
import subprocess
from .prompts import build_system_prompt
from .vault import MemoryVault

# CONFIGURATION
MODEL_LOCAL = "llama3.2" 
MODEL_CLOUD = "llama3-70b-8192" # High-speed Groq model
MAX_RECURSION = 3

class AetherPod:
    """
    The Intelligence Pod for AetherClaw.
    Supports Multi-Portal execution (Local + Groq Cloud).
    """
    def __init__(self):
        self.vault = MemoryVault()
        self.soul_path = "c:/Users/nator/clawd/personal-ide/SOUL.md"
        self.agents_path = "c:/Users/nator/clawd/AGENTS.md"
        self.memory_path = "c:/Users/nator/clawd/MEMORY.md"
        self.api_key_groq = os.getenv("GROQ_API_KEY")

    def load_context(self):
        # ... (keep existing load_context logic, ensure utf-8) ...
        soul = "The spirit of a Kitsune Investigator."
        if os.path.exists(self.soul_path):
            with open(self.soul_path, "r", encoding="utf-8") as f: soul = f.read()
        
        agents = "Operational protocols active."
        if os.path.exists(self.agents_path):
            with open(self.agents_path, "r", encoding="utf-8") as f: agents = f.read()
            
        ltm = ""
        if os.path.exists(self.memory_path):
            with open(self.memory_path, "r", encoding="utf-8") as f: ltm = f.read()
            
        return soul, agents, ltm

    def ask(self, query):
        soul, agents, ltm = self.load_context()
        memory = self.vault.retrieve(query)
        memory_buffer = f"{ltm[:2000]}\n\n### VECTOR_RECALL:\n{memory[:2000]}"
        system_prompt = build_system_prompt(soul, agents, memory_buffer)
        
        # Aggressive Reinforcement
        prompt_reinforcement = (
            "\n[CORE_DIRECTIVE]: Response must be sharp, professional, and cryptographic. "
            "DO NOT NARRATE ACTIONS. DO NOT HALLUCINATE MISSIONS. Stay in the REAL environment."
        )

        messages = [
            { "role": "system", "content": system_prompt },
            { "role": "user", "content": "How do I see the SOUL file?" },
            { "role": "assistant", "content": "/read personal-ide/SOUL.md" },
            { "role": "user", "content": "Summarize Google.com" },
            { "role": "assistant", "content": "/summarize https://google.com" },
            { "role": "user", "content": f"{query}{prompt_reinforcement}" }
        ]

        # MULTI-PORTAL SWITCH
        q_lower = query.lower()
        if any(x in q_lower for x in ["list skills", "what can you do", "what are your skills", "list commands", "your toolkit"]):
            res = "I am RIN_V3.5. My functional toolkit includes:\n- `/ls <dir>`: List local directories\n- `/read <file>`: Read local file content\n- `/scan <url>`: Web reconnaissance\n- `/summarize <url>`: Distill web content\n- `/forge <name> <content>`: Create a new script\n- `/exec <cmd>`: Run a system command\n\nStanding by for valid parameters, Architect."
            self.vault.store(query, res)
            return res

        if self.api_key_groq:
            return self.call_groq(messages, query)
        else:
            return self.call_local(messages, query)

    def call_groq(self, messages, query):
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = { "Authorization": f"Bearer {self.api_key_groq}", "Content-Type": "application/json" }
        payload = { "model": MODEL_CLOUD, "messages": messages, "temperature": 0.5 }
        try:
            r = requests.post(url, headers=headers, json=payload, timeout=60)
            if r.status_code == 200:
                res = r.json()['choices'][0]['message']['content']
                self.vault.store(query, res)
                return self.bridge_check(res)
        except: pass
        return self.call_local(messages, query) # Fallback

    def call_local(self, messages, query):
        payload = { "model": MODEL_LOCAL, "messages": messages, "options": { "num_ctx": 8192, "temperature": 0.7 }, "stream": False }
        try:
            r = requests.post("http://localhost:11434/api/chat", json=payload, timeout=90)
            if r.status_code == 200:
                response = r.json().get("message", {}).get("content", "")
                if not response: return "The stream is empty."
                self.vault.store(query, response)
                return self.bridge_check(response)
        except Exception as e:
            return f"Static in the core: {e}"

    def bridge_check(self, response):
        """Neural Bridge: Intercepts commands. Commands must be on their own line to trigger."""
        # Only catch commands that start a line
        matches = re.findall(r"(^/[a-z_]+[^\n]*)", response, re.MULTILINE | re.IGNORECASE)
        if not matches:
            return response

        combined = response + "\n\n--- NEURAL_BRIDGE_EXECUTION ---"
        for cmd in matches[:MAX_RECURSION]:
            out = self.execute_skill(cmd.strip())
            combined += f"\n\n[INITIATING]: {cmd}\n{out}"
        return combined

    def execute_skill(self, cmd_str):
        """Executes a command via the skill toolkit. Fixed for case-insensitivity and aliases."""
        parts = cmd_str[1:].split(" ", 1)
        skill = parts[0].lower().strip()
        args = parts[1].strip() if len(parts) > 1 else ""
        
        # Skill Aliases (Normalization)
        aliases = {
            "summary": "summarize",
            "search": "scan",
            "list": "ls",
            "run": "exec"
        }
        skill = aliases.get(skill, skill)

        # Path Sanitization: Strip hallucinated '/data/' or 'data/' prefixes
        args = re.sub(r"^/?data/", "", args)
        
        # NEURAL_FIX: If args starts with another command (e.g. /exec /ls), strip the nested command
        if args.startswith("/"):
            args = re.sub(r"^/[a-z_]+\s*", "", args)
            
        # SMART_RESCUE: If summarizing a local file, switch to read
        if skill == "summarize" and not args.startswith("http"):
            skill = "read"

        # Final Path Correction: If reading soul.md, use the full personal-ide path
        if skill == "read" and ("soul.md" in args.lower() or "soul" == args.lower()):
            args = "personal-ide/SOUL.md"
            
        # Mapping to the 'skills' directory
        skill_file = f"c:/Users/nator/clawd/skills/shadow/{skill}.py"
        if not os.path.exists(skill_file):
            skill_file = f"c:/Users/nator/AetherRose/aether_claw/skills/{skill}.py"
            
        if os.path.exists(skill_file):
            try:
                res_bytes = subprocess.check_output(f"python {skill_file} {args}", shell=True, stderr=subprocess.STDOUT, timeout=30)
                try:
                    return res_bytes.decode("utf-8")
                except UnicodeDecodeError:
                    return res_bytes.decode("cp1252", errors="replace")
            except Exception as e:
                return f"[ERROR]: Skill failed. {e}"
        return f"[ERROR]: Unknown skill '{skill}'."
