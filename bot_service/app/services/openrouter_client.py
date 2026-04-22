import httpx
from typing import Any
from fastapi import status

from app.core.config import settings
from app.core.exceptions import ExternalServiceError

class OpenRouter:
    def __init__(self) -> None:
        self._api_key = settings.openrouter_api_key
        self._base_url = settings.openrouter_base_url
        self._model = settings.openrouter_model
        self._referer = settings.openrouter_site_url
        self._title = settings.openrouter_app_name
        self._client = httpx.Client(timeout=30)
    
    def _build_headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self._api_key}",
            "HTTP-Referer": self._referer,
            "X-Title": self._title,
            "Content-Type": "application/json"
        }
    
    def chat_completion(
            self,
            messages: str
    ) -> dict[str, Any]:
        payload = {
            "model": self._model,
            "messages": messages
        }

        url = f"{self._base_url}/chat/completions"

        try:
            response = self._client.post(
                    url,
                    headers=self._build_headers(),
                    json=payload
                )
            if response.status_code != 200:
                raise ExternalServiceError(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail="Ошибка внешнего сервиса."
                )
        except httpx.RequestError as e:
            raise ExternalServiceError(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Ошибка сети: {str(e)}"
            )
        
        try:
            return response.json()
        except ValueError:
            raise ExternalServiceError(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Некорректный ответ внешнего сервиса."
            )

openrouter_client = OpenRouter()
