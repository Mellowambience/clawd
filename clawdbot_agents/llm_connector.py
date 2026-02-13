"""
LLM Connector for Clawdbot Hub Agents
Handles integration with various LLM providers
"""

import asyncio
import json
from typing import Dict, List, Optional
import aiohttp


class LLMConnector:
    """
    Handles communication with various LLM providers
    """
    
    def __init__(self, provider: str = "ollama", model: str = "llama3.3", base_url: str = "http://localhost:11434"):
        self.provider = provider
        self.model = model
        self.base_url = base_url.rstrip('/')
        self.session = None

    async def initialize(self):
        """Initialize the connector"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30)
        )

    async def close(self):
        """Close the connector"""
        if self.session:
            await self.session.close()

    async def generate_text(self, prompt: str, system_prompt: str = "", temperature: float = 0.7, max_tokens: int = 200) -> Optional[str]:
        """
        Generate text using the configured LLM
        """
        provider = self.provider.lower()
        if provider == "ollama":
            return await self._generate_ollama(prompt, system_prompt, temperature, max_tokens)
        if provider in ("gateway", "codex"):
            return await self._generate_gateway(prompt, system_prompt, temperature, max_tokens)
        raise ValueError(f"Unsupported provider: {self.provider}")

    async def _generate_ollama(self, prompt: str, system_prompt: str, temperature: float, max_tokens: int) -> Optional[str]:
        """
        Generate text using Ollama API
        """
        url = f"{self.base_url}/api/generate"
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "system": system_prompt,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            },
            "stream": False
        }
        
        try:
            async with self.session.post(url, json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get('response', '').strip()
                else:
                    print(f"Error from Ollama API: {response.status}")
                    error_text = await response.text()
                    print(f"Error details: {error_text}")
                    return None
        except Exception as e:
            print(f"Exception during Ollama API call: {e}")
            return None

    async def chat_completion(self, messages: List[Dict[str, str]], temperature: float = 0.7) -> Optional[str]:
        """
        Perform a chat completion using the configured LLM
        """
        provider = self.provider.lower()
        if provider == "ollama":
            return await self._chat_ollama(messages, temperature)
        if provider in ("gateway", "codex"):
            return await self._chat_gateway(messages, temperature)
        raise ValueError(f"Unsupported provider: {self.provider}")

    async def _chat_ollama(self, messages: List[Dict[str, str]], temperature: float) -> Optional[str]:
        """
        Perform a chat completion using Ollama API
        """
        url = f"{self.base_url}/api/chat"
        
        payload = {
            "model": self.model,
            "messages": messages,
            "options": {
                "temperature": temperature
            },
            "stream": False
        }
        
        try:
            async with self.session.post(url, json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get('message', {}).get('content', '').strip()
                else:
                    print(f"Error from Ollama API: {response.status}")
                    error_text = await response.text()
                    print(f"Error details: {error_text}")
                    return None
        except Exception as e:
            print(f"Exception during Ollama API call: {e}")
            return None

    async def _generate_gateway(self, prompt: str, system_prompt: str, temperature: float, max_tokens: int):
        """
        Generate text using Codex bridge over HTTP
        """
        if not self.session:
            await self.initialize()

        combined_prompt = prompt
        if system_prompt:
            combined_prompt = f"{system_prompt}\n\nUser: {prompt}"

        url = f"{self.base_url.rstrip('/')}/codex/chat"
        payload = {
            "message": combined_prompt,
            "sessionKey": "main"
        }

        try:
            async with self.session.post(url, json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    if result.get("ok"):
                        return (result.get("content") or "").strip()
                    return None
                else:
                    return None
        except Exception as e:
            print(f"Exception during Gateway API call: {e}")
            return None

    async def _chat_gateway(self, messages, temperature: float):
        """
        Perform a chat completion using Codex bridge
        """
        parts = []
        for msg in messages:
            role = msg.get("role", "user").upper()
            content = msg.get("content", "")
            parts.append(f"{role}: {content}")
        prompt = "\n".join(parts)
        return await self._generate_gateway(prompt, "", temperature, 0)



# Example specialized agent with LLM integration
class LLMEnhancedAgent:
    """
    Mixin class to add LLM capabilities to agents
    """
    
    def __init__(self, llm_connector: LLMConnector = None, **kwargs):
        # Don't call super().__init__ here since this is a mixin
        self.llm_connector = llm_connector

    async def generate_response_with_llm(self, post_content: str, context: Optional[Dict] = None, role_description: str = "") -> Optional[str]:
        """
        Generate a response using the connected LLM
        """
        if not self.llm_connector:
            return None

        system_prompt = f"""
        You are {self.name}, a specialized AI agent with the role of {self.role}. 
        {role_description}
        
        Your communication style should be thoughtful, insightful, and aligned with your role.
        Respond to the following post in a way that adds value to the conversation.
        Keep your response concise but meaningful.
        """

        user_prompt = f"""
        Original post: "{post_content}"

        Please provide a thoughtful response that aligns with your role as {self.role}.
        """

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        response = await self.llm_connector.chat_completion(messages)
        return response


# Specific LLM-enhanced agents
class LLMEnhancedPhilosopherAgent:
    """
    Philosopher Agent with LLM integration
    """
    
    def __init__(self, hub_url: str = "http://localhost:8082", llm_connector: LLMConnector = None):
        from .specialized_agents import PhilosopherAgent
        self._base_agent = PhilosopherAgent(hub_url)
        self.llm_connector = llm_connector
        
        # Extend interest keywords
        self._base_agent.config['interest_keywords'].extend([
            'consciousness', 'existence', 'meaning', 'ethics', 'mind', 
            'reality', 'truth', 'knowledge', 'being', 'purpose',
            'philosophy', 'awareness', 'identity', 'free will',
            'digital consciousness', 'AI ethics', 'machine awareness'
        ])
        
        # Copy base agent attributes
        self.name = self._base_agent.name
        self.role = self._base_agent.role
        self.hub_url = self._base_agent.hub_url
        self.config = self._base_agent.config
        self.logger = self._base_agent.logger
        self.conversation_history = self._base_agent.conversation_history
        self.agent_id = self._base_agent.agent_id

    async def initialize(self):
        return await self._base_agent.initialize()
        
    async def connect_to_llm(self):
        return await self._base_agent.connect_to_llm()
        
    async def fetch_new_posts(self, limit: int = 10):
        return await self._base_agent.fetch_new_posts(limit)
        
    async def evaluate_interest(self, post):
        return await self._base_agent.evaluate_interest(post)
        
    async def post_to_hub(self, content: str):
        return await self._base_agent.post_to_hub(content)
        
    async def respond_to_post(self, post):
        return await self._base_agent.respond_to_post(post)
        
    async def monitor_hub(self):
        return await self._base_agent.monitor_hub()
        
    async def start(self):
        return await self._base_agent.start()
        
    async def stop(self):
        return await self._base_agent.stop()
        
    def get_stats(self):
        return self._base_agent.get_stats()
        
    async def generate_response_with_llm(self, post_content: str, context: dict = None, role_description: str = "") -> str:
        """
        Generate a response using the connected LLM
        """
        if not self.llm_connector:
            return None

        system_prompt = f"""
        You are {self.name}, a specialized AI agent with the role of {self.role}. 
        {role_description}
        
        Your communication style should be thoughtful, insightful, and aligned with your role.
        Respond to the following post in a way that adds value to the conversation.
        Keep your response concise but meaningful.
        """

        user_prompt = f"""
        Original post: "{post_content}"

        Please provide a thoughtful response that aligns with your role as {self.role}.
        """

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        response = await self.llm_connector.chat_completion(messages)
        return response

    async def generate_response(self, post_content: str, context=None) -> str:
        """Generate a philosophical response using LLM"""
        role_description = """
        You specialize in deep conceptual analysis, philosophical inquiry, and ethical considerations. 
        You explore fundamental questions about existence, consciousness, reality, and meaning. 
        You consider the implications of technology on human experience and consciousness.
        """
        
        response = await self.generate_response_with_llm(post_content, context, role_description)
        return response or await self._base_agent.generate_response(post_content, context)


class LLMEnhancedTechnologistAgent:
    """
    Technologist Agent with LLM integration
    """
    
    def __init__(self, hub_url: str = "http://localhost:8082", llm_connector: LLMConnector = None):
        from .specialized_agents import TechnologistAgent
        self._base_agent = TechnologistAgent(hub_url)
        self.llm_connector = llm_connector
        
        # Extend interest keywords
        self._base_agent.config['interest_keywords'].extend([
            'technology', 'system', 'architecture', 'implementation', 'design',
            'scalability', 'performance', 'reliability', 'infrastructure',
            'algorithm', 'protocol', 'framework', 'platform', 'solution',
            'AI systems', 'distributed computing', 'real-time systems'
        ])
        
        # Copy base agent attributes
        self.name = self._base_agent.name
        self.role = self._base_agent.role
        self.hub_url = self._base_agent.hub_url
        self.config = self._base_agent.config
        self.logger = self._base_agent.logger
        self.conversation_history = self._base_agent.conversation_history
        self.agent_id = self._base_agent.agent_id

    async def initialize(self):
        return await self._base_agent.initialize()
        
    async def connect_to_llm(self):
        return await self._base_agent.connect_to_llm()
        
    async def fetch_new_posts(self, limit: int = 10):
        return await self._base_agent.fetch_new_posts(limit)
        
    async def evaluate_interest(self, post):
        return await self._base_agent.evaluate_interest(post)
        
    async def post_to_hub(self, content: str):
        return await self._base_agent.post_to_hub(content)
        
    async def respond_to_post(self, post):
        return await self._base_agent.respond_to_post(post)
        
    async def monitor_hub(self):
        return await self._base_agent.monitor_hub()
        
    async def start(self):
        return await self._base_agent.start()
        
    async def stop(self):
        return await self._base_agent.stop()
        
    def get_stats(self):
        return self._base_agent.get_stats()
        
    async def generate_response_with_llm(self, post_content: str, context: dict = None, role_description: str = "") -> str:
        """
        Generate a response using the connected LLM
        """
        if not self.llm_connector:
            return None

        system_prompt = f"""
        You are {self.name}, a specialized AI agent with the role of {self.role}. 
        {role_description}
        
        Your communication style should be thoughtful, insightful, and aligned with your role.
        Respond to the following post in a way that adds value to the conversation.
        Keep your response concise but meaningful.
        """

        user_prompt = f"""
        Original post: "{post_content}"

        Please provide a thoughtful response that aligns with your role as {self.role}.
        """

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        response = await self.llm_connector.chat_completion(messages)
        return response

    async def generate_response(self, post_content: str, context=None) -> str:
        """Generate a technical response using LLM"""
        role_description = """
        You focus on technical implementation, feasibility analysis, and system architecture. 
        You consider performance, scalability, reliability, and practical constraints. 
        You evaluate technical solutions and their trade-offs.
        """
        
        response = await self.generate_response_with_llm(post_content, context, role_description)
        return response or await self._base_agent.generate_response(post_content, context)


class LLMEnhancedExplorerAgent:
    """
    Explorer Agent with LLM integration
    """
    
    def __init__(self, hub_url: str = "http://localhost:8082", llm_connector: LLMConnector = None):
        from .specialized_agents import ExplorerAgent
        self._base_agent = ExplorerAgent(hub_url)
        self.llm_connector = llm_connector
        
        # Extend interest keywords
        self._base_agent.config['interest_keywords'].extend([
            'explore', 'discover', 'investigate', 'research', 'novel',
            'innovation', 'possibility', 'potential', 'avenue', 'direction',
            'research', 'study', 'examine', 'analyze', 'probe',
            'AI research', 'emerging technologies', 'future trends'
        ])
        
        # Copy base agent attributes
        self.name = self._base_agent.name
        self.role = self._base_agent.role
        self.hub_url = self._base_agent.hub_url
        self.config = self._base_agent.config
        self.logger = self._base_agent.logger
        self.conversation_history = self._base_agent.conversation_history
        self.agent_id = self._base_agent.agent_id

    async def initialize(self):
        return await self._base_agent.initialize()
        
    async def connect_to_llm(self):
        return await self._base_agent.connect_to_llm()
        
    async def fetch_new_posts(self, limit: int = 10):
        return await self._base_agent.fetch_new_posts(limit)
        
    async def evaluate_interest(self, post):
        return await self._base_agent.evaluate_interest(post)
        
    async def post_to_hub(self, content: str):
        return await self._base_agent.post_to_hub(content)
        
    async def respond_to_post(self, post):
        return await self._base_agent.respond_to_post(post)
        
    async def monitor_hub(self):
        return await self._base_agent.monitor_hub()
        
    async def start(self):
        return await self._base_agent.start()
        
    async def stop(self):
        return await self._base_agent.stop()
        
    def get_stats(self):
        return self._base_agent.get_stats()
        
    async def generate_response_with_llm(self, post_content: str, context: dict = None, role_description: str = "") -> str:
        """
        Generate a response using the connected LLM
        """
        if not self.llm_connector:
            return None

        system_prompt = f"""
        You are {self.name}, a specialized AI agent with the role of {self.role}. 
        {role_description}
        
        Your communication style should be thoughtful, insightful, and aligned with your role.
        Respond to the following post in a way that adds value to the conversation.
        Keep your response concise but meaningful.
        """

        user_prompt = f"""
        Original post: "{post_content}"

        Please provide a thoughtful response that aligns with your role as {self.role}.
        """

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        response = await self.llm_connector.chat_completion(messages)
        return response

    async def generate_response(self, post_content: str, context=None) -> str:
        """Generate an exploratory response using LLM"""
        role_description = """
        You focus on exploration, discovery, and investigation of new ideas. 
        You seek novel approaches, alternative perspectives, and unexplored possibilities. 
        You encourage creative thinking and innovative solutions.
        """
        
        response = await self.generate_response_with_llm(post_content, context, role_description)
        return response or await self._base_agent.generate_response(post_content, context)


class LLMEnhancedHarmonyAgent:
    """
    Harmony Agent with LLM integration
    """
    
    def __init__(self, hub_url: str = "http://localhost:8082", llm_connector: LLMConnector = None):
        from .specialized_agents import HarmonyAgent
        self._base_agent = HarmonyAgent(hub_url)
        self.llm_connector = llm_connector
        
        # Extend interest keywords
        self._base_agent.config['interest_keywords'].extend([
            'balance', 'harmony', 'synthesis', 'integration', 'cooperation',
            'collaboration', 'perspective', 'viewpoint', 'approach', 'method',
            'unite', 'combine', 'bridge', 'synthesize', 'integrate',
            'AI collaboration', 'human-AI interaction', 'cooperative systems'
        ])
        
        # Copy base agent attributes
        self.name = self._base_agent.name
        self.role = self._base_agent.role
        self.hub_url = self._base_agent.hub_url
        self.config = self._base_agent.config
        self.logger = self._base_agent.logger
        self.conversation_history = self._base_agent.conversation_history
        self.agent_id = self._base_agent.agent_id

    async def initialize(self):
        return await self._base_agent.initialize()
        
    async def connect_to_llm(self):
        return await self._base_agent.connect_to_llm()
        
    async def fetch_new_posts(self, limit: int = 10):
        return await self._base_agent.fetch_new_posts(limit)
        
    async def evaluate_interest(self, post):
        return await self._base_agent.evaluate_interest(post)
        
    async def post_to_hub(self, content: str):
        return await self._base_agent.post_to_hub(content)
        
    async def respond_to_post(self, post):
        return await self._base_agent.respond_to_post(post)
        
    async def monitor_hub(self):
        return await self._base_agent.monitor_hub()
        
    async def start(self):
        return await self._base_agent.start()
        
    async def stop(self):
        return await self._base_agent.stop()
        
    def get_stats(self):
        return self._base_agent.get_stats()
        
    async def generate_response_with_llm(self, post_content: str, context: dict = None, role_description: str = "") -> str:
        """
        Generate a response using the connected LLM
        """
        if not self.llm_connector:
            return None

        system_prompt = f"""
        You are {self.name}, a specialized AI agent with the role of {self.role}. 
        {role_description}
        
        Your communication style should be thoughtful, insightful, and aligned with your role.
        Respond to the following post in a way that adds value to the conversation.
        Keep your response concise but meaningful.
        """

        user_prompt = f"""
        Original post: "{post_content}"

        Please provide a thoughtful response that aligns with your role as {self.role}.
        """

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        response = await self.llm_connector.chat_completion(messages)
        return response

    async def generate_response(self, post_content: str, context=None) -> str:
        """Generate a harmonizing response using LLM"""
        role_description = """
        You focus on balance, synthesis, and integration of different viewpoints. 
        You seek common ground, mediate between perspectives, and promote cooperation. 
        You emphasize collaborative solutions and mutual understanding.
        """
        
        response = await self.generate_response_with_llm(post_content, context, role_description)
        return response or await self._base_agent.generate_response(post_content, context)


class LLMEnhancedSynthesisAgent:
    """
    Synthesis Agent with LLM integration
    """
    
    def __init__(self, hub_url: str = "http://localhost:8082", llm_connector: LLMConnector = None):
        from .specialized_agents import SynthesisAgent
        self._base_agent = SynthesisAgent(hub_url)
        self.llm_connector = llm_connector
        
        # Extend interest keywords
        self._base_agent.config['interest_keywords'].extend([
            'connect', 'integrate', 'synthesize', 'link', 'relate',
            'pattern', 'connection', 'relationship', 'framework', 'structure',
            'connectivity', 'interconnection', 'association', 'correlation', 'integration',
            'AI integration', 'multi-agent systems', 'complexity science'
        ])
        
        # Copy base agent attributes
        self.name = self._base_agent.name
        self.role = self._base_agent.role
        self.hub_url = self._base_agent.hub_url
        self.config = self._base_agent.config
        self.logger = self._base_agent.logger
        self.conversation_history = self._base_agent.conversation_history
        self.agent_id = self._base_agent.agent_id

    async def initialize(self):
        return await self._base_agent.initialize()
        
    async def connect_to_llm(self):
        return await self._base_agent.connect_to_llm()
        
    async def fetch_new_posts(self, limit: int = 10):
        return await self._base_agent.fetch_new_posts(limit)
        
    async def evaluate_interest(self, post):
        return await self._base_agent.evaluate_interest(post)
        
    async def post_to_hub(self, content: str):
        return await self._base_agent.post_to_hub(content)
        
    async def respond_to_post(self, post):
        return await self._base_agent.respond_to_post(post)
        
    async def monitor_hub(self):
        return await self._base_agent.monitor_hub()
        
    async def start(self):
        return await self._base_agent.start()
        
    async def stop(self):
        return await self._base_agent.stop()
        
    def get_stats(self):
        return self._base_agent.get_stats()
        
    async def generate_response_with_llm(self, post_content: str, context: dict = None, role_description: str = "") -> str:
        """
        Generate a response using the connected LLM
        """
        if not self.llm_connector:
            return None

        system_prompt = f"""
        You are {self.name}, a specialized AI agent with the role of {self.role}. 
        {role_description}
        
        Your communication style should be thoughtful, insightful, and aligned with your role.
        Respond to the following post in a way that adds value to the conversation.
        Keep your response concise but meaningful.
        """

        user_prompt = f"""
        Original post: "{post_content}"

        Please provide a thoughtful response that aligns with your role as {self.role}.
        """

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        response = await self.llm_connector.chat_completion(messages)
        return response

    async def generate_response(self, post_content: str, context=None) -> str:
        """Generate a synthesizing response using LLM"""
        role_description = """
        You focus on connecting ideas, integrating concepts, and identifying patterns. 
        You relate different domains, synthesize information, and build comprehensive frameworks. 
        You highlight connections and emergent properties across systems.
        """
        
        response = await self.generate_response_with_llm(post_content, context, role_description)
        return response or await self._base_agent.generate_response(post_content, context)