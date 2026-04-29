# интеграционные тесты 
import respx
from httpx import Response

from app.services.openrouter_client import openrouter_client

# тестирование клиента openrouter
@respx.mock
def test_openrouter_called():
    route = respx.post("https://openrouter.ai/api/v1/chat/completions").mock(
        return_value=Response(
            200,
            json={
                "choices": [
                    {
                        "message": {
                            "content": "test response"
                        }
                    }
                ]
            }
        )
    )

    messages = [{
        "role": "user",
        "content": "hello llm"
    }]

    result = openrouter_client.chat_completion(messages)
    assert result["choices"][0]["message"]["content"] == "test response"
    assert route.called
