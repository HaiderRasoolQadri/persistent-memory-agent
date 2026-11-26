import json
import re
import os

from langchain_ollama import ChatOllama
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from memory import EpisodicMemory, SemanticMemory
from dotenv import load_dotenv

load_dotenv()

class PersistentMemoryAgent:
    def __init__(self):
        provider = os.getenv("LLM_PROVIDER", "ollama")
        
        if provider == "groq":
            api_key=os.getenv("GROQ_API_KEY")
            if not api_key:
                raise ValueError("Insert API key.")
            self.llm = ChatGroq(
                model="openai/gpt-oss-120b",
                temperature=0.3,
                api_key=api_key
            )
            print(f"[LLM] Using Groq API {self.llm.model}")
        else:
            self.llm = ChatOllama(
                model="qwen2.5:1.5b",
                temperature=0.3
            )
            print(f"[LLM] Using local Ollama (qwen2.5:1.5b)")
        
        self.episodic = EpisodicMemory()
        self.semantic = SemanticMemory()

    def _build_context(self, user_input):
        # 1. Episodic se related conversations
        past = self.episodic.retrieve(user_input, top_k=3)

        # 2. Semantic se saare facts
        facts = self.semantic.get_all_facts()

        # 3. String banao
        parts = []
        if facts:
            parts.append("Known facts:\n" + "\n".join(f"- {k}: {v}" for k, v in facts.items()))
        if past:
            parts.append("Past conversations:\n" + "\n".join(f"- {p}" for p in past))

        return "\n\n".join(parts) if parts else "No prior context."

    def _extract_facts(self, conversation: str) -> dict:
        """Use LLM to extract facts from conversation."""
        
        # Current facts lo
        current_facts = self.semantic.get_all_facts()
        if current_facts:
            current_str = "\n".join(f"- {k}: {v}" for k, v in current_facts.items())
        else:
            current_str = "(none)"
        
        prompt = f"""Extract personal facts from this conversation.

    Current stored facts:
    {current_str}

    Rules:
    1. Return ONLY a JSON object. If no new/changed facts, return {{}}.
    2. Use the SAME key names as above (e.g., if "profession" exists, use "profession").
    3. If user corrects a fact, output the NEW value with the same key.
    4. Do NOT create new keys for the same concept.

    Example: If current facts have "profession: Developer"
    and user says "I'm not a developer, I'm a data scientist",
    output: {{"profession": "data scientist"}}

    Conversation:
    {conversation}

    JSON:"""

        response = self.llm.invoke([HumanMessage(content=prompt)])

        match = re.search(r'\{.*\}', response.content, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                return {}
        return {}

    def chat(self, user_input: str) -> str:
        """Main chat with memory."""    

        # 1. PEHLE user ke message se facts extract karo aur save karo
        facts = self._extract_facts(f"User: {user_input}")
        for key, value in facts.items():
            self.semantic.store_fact(key, str(value))

        # 2. AB context banao (fresh facts ke saath)
        context = self._build_context(user_input)

        # 3. System prompt
        system_prompt = f"""You are a helpful assistant with memory.

            Context about the user:
            {context}

            Rules:
            1. Answer in 1-3 sentences. Be direct.
            2. Trust the user's current statement over stored facts.
            3. If the user corrects a fact, accept it.
            4. Do NOT make up information."""

        # 4. LLM call
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_input)
        ]
        response = self.llm.invoke(messages)
        agent_reply = response.content

        # 5. Episodic mein store
        interaction = f"User: {user_input}\nAgent: {agent_reply}"
        self.episodic.store(interaction)

        return agent_reply