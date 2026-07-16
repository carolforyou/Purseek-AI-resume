import  json
import urllib.request
from typing import Any

from app.core.settings import get_settings


class GroqService:
    def __init__(self) -> None:
        self.settings = get_settings()

    def is_configured(self) -> bool:
        return bool(self.settings.groq_api_key)

    def chat(self, system_prompt: str, user_prompt: str) -> str:
        if not self.is_configured():
            raise RuntimeError("GROQ_API_KEY 未配置。")

        payload: dict[str, Any] = {
            "model": self.settings.groq_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.7,
        }
        request = urllib.request.Request(
            url="https://api.groq.com/openai/v1/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.settings.groq_api_key}",
            },
            method="POST",
        )

        with urllib.request.urlopen(request, timeout=45) as response:
            body = json.loads(response.read().decode("utf-8"))

        return body["choices"][0]["message"]["content"].strip()