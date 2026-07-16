"LangChain Agent orchestration for AI Job Hunt Assistant.

Builds a tool-calling agent that can:
- Search the knowledge base
- Analyze job descriptions
- Generate custom resumes
- Polish resume content
- Access user profile
"""

from typing import Any, Dict, List, Optional

from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from app.services.llm_service import GroqChatModel
from app.services.rag_tools import ALL_TOOLS

SYSTEM_PROMPT = """You are an AI career assistant helping users with their job search.

You have access to the following tools:
- search_knowledge_base: Search the user's personal knowledge base for relevant documents
- analyze_jd: Parse and analyze a job description to extract requirements
- generate_custom_resume: Generate a resume tailored to a specific job
- polish_content: Improve the wording of resume sections
- get_profile_summary: Get a summary of the user's current profile/resume

When responding:
1. Use tools to get accurate information before answering
2. Be concise and professional
3. After generating a custom resume, explain what modifications were made
4. If the user asks to polish something, explain what was improved
5. Always use Chinese when the user communicates in Chinese

The current date is 2026-07-15."""


class AgentService:
    """LangChain Agent service for resume and job search assistance."""

    def __init__(self) -> None:
        self.llm = GroqChatModel(temperature=0.3)
        self.agent_executor: Optional[AgentExecutor] = None
        self._build_agent()

    def _build_agent(self) -> None:
        prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            MessagesPlaceholder(variable_name="chat_history", optional=True),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

        agent = create_tool_calling_agent(self.llm, ALL_TOOLS, prompt)
        self.agent_executor = AgentExecutor(
            agent=agent,
            tools=ALL_TOOLS,
            verbose=False,
            handle_parsing_errors=True,
            max_iterations=5,
            return_intermediate_steps=False,
        )

    def chat(
        self,
        message: str,
        chat_history: Optional[List[Any]] = None,
    ) -> str:
        """Send a message to the agent and get a response."""
        if self.agent_executor is None:
            self._build_agent()

        try:
            result = self.agent_executor.invoke({
                "input": message,
                "chat_history": chat_history or [],
            })
            return result.get("output", "Sorry, I could not process that request.")
        except Exception as e:
            # Fallback: direct LLM call without tools
            try:
                messages = [
                    SystemMessage(content=SYSTEM_PROMPT),
                    HumanMessage(content=message),
                ]
                response = self.llm.invoke(messages)
                return response.content
            except Exception:
                return f"Unable to process your request: {str(e)}"

    def chat_with_context(
        self,
        message: str,
        context: str = "",
        chat_history: Optional[List[Any]] = None,
    ) -> str:
        """Chat with additional context prepended."""
        if context:
            message = f"Relevant context from knowledge base:\n{context}\n\nUser message: {message}"
        return self.chat(message, chat_history)


# Singleton
_agent_instance: Optional[AgentService] = None


def get_agent() -> AgentService:
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = AgentService()
    return _agent_instance
