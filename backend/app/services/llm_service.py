"LangChain-compatible Groq LLM wrapper with tool calling support."""

import json
import urllib.request
from typing import Any, Iterator, List, Optional

from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from langchain_core.tools import BaseTool
from pydantic import Field

from app.core.settings import get_settings


class GroqChatModel(BaseChatModel):
    """LangChain-compatible chat model backed by Groq API with tool calling."""

    model_name: str = Field(default="llama-3.3-70b-versatile")
    temperature: float = Field(default=0.3)
    api_key: str = Field(default="")

    def __init__(self, **data: Any) -> None:
        settings = get_settings()
        data.setdefault("model_name", settings.groq_model)
        data.setdefault("api_key", settings.groq_api_key)
        super().__init__(**data)

    @property
    def _llm_type(self) -> str:
        return "groq-chat"

    def bind_tools(self, tools: List[Any], **kwargs: Any) -> "GroqChatModel":
        """Bind tools to the model for function calling."""
        from copy import deepcopy
        bound = deepcopy(self)
        bound._tools = tools
        return bound

    def _convert_messages(self, messages: List[BaseMessage]) -> List[dict]:
        result = []
        for msg in messages:
            if isinstance(msg, SystemMessage):
                result.append({"role": "system", "content": msg.content})
            elif isinstance(msg, HumanMessage):
                result.append({"role": "user", "content": msg.content})
            elif isinstance(msg, AIMessage):
                entry: dict = {"role": "assistant", "content": msg.content or ""}
                if hasattr(msg, "tool_calls") and msg.tool_calls:
                    entry["tool_calls"] = [
                        {
                            "id": tc.get("id", "call_1"),
                            "type": "function",
                            "function": {
                                "name": tc.get("name", ""),
                                "arguments": json.dumps(tc.get("args", {})),
                            },
                        }
                        for tc in msg.tool_calls
                    ]
                result.append(entry)
            elif isinstance(msg, ToolMessage):
                result.append({
                    "role": "tool",
                    "tool_call_id": getattr(msg, "tool_call_id", "call_1"),
                    "content": msg.content,
                })
            else:
                result.append({"role": "user", "content": str(msg.content)})
        return result

    def _build_tools_param(self) -> Optional[list]:
        if not hasattr(self, "_tools") or not self._tools:
            return None
        return [
            {
                "type": "function",
                "function": {
                    "name": t.name,
                    "description": t.description,
                    "parameters": t.args_schema.model_json_schema() if hasattr(t, "args_schema") and t.args_schema else {"type": "object", "properties": {}},
                },
            }
            for t in self._tools
        ]

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        if not self.api_key:
            raise RuntimeError("GROQ_API_KEY not configured")

        payload: dict[str, Any] = {
            "model": self.model_name,
            "messages": self._convert_messages(messages),
            "temperature": self.temperature,
        }
        if stop:
            payload["stop"] = stop

        tools = self._build_tools_param()
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"

        request = urllib.request.Request(
            url="https://api.groq.com/openai/v1/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
            method="POST",
        )

        with urllib.request.urlopen(request, timeout=90) as response:
            body = json.loads(response.read().decode("utf-8"))

        choice = body["choices"][0]
        msg_data = choice["message"]
        content = msg_data.get("content", "") or ""

        # Handle tool calls
        tool_calls = []
        if "tool_calls" in msg_data:
            for tc in msg_data["tool_calls"]:
                try:
                    args = json.loads(tc["function"]["arguments"])
                except (json.JSONDecodeError, KeyError):
                    args = {}
                tool_calls.append({
                    "id": tc.get("id", "call_1"),
                    "name": tc["function"]["name"],
                    "args": args,
                })

        message = AIMessage(content=content.strip())
        if tool_calls:
            message.tool_calls = tool_calls
            message.additional_kwargs = {"tool_calls": [
                {
                    "id": tc["id"],
                    "type": "function",
                    "function": {"name": tc["name"], "arguments": json.dumps(tc["args"])},
                }
                for tc in tool_calls
            ]}

        return ChatResult(generations=[ChatGeneration(message=message)])
