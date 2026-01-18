import requests
from app.config import settings


OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


def ai_responder(question: str, language: str) -> dict:
    headers = {
        "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    system_prompt = (
        "You are VoiceServe AI. "
        "Answer clearly, safely, and simply. "
        "Do not give medical diagnosis. "
        "Do not claim government authority."
    )

    user_prompt = (
        f"Answer in Tamil." if language == "ta"
        else f"Answer in English."
    ) + f"\nQuestion: {question}"

    payload = {
        "model": "openai/gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    }

    try:
        response = requests.post(
            OPENROUTER_URL,
            headers=headers,
            json=payload,
            timeout=30
        )

        data = response.json()
        answer = data["choices"][0]["message"]["content"]

        return {
            "response": answer,
            "next_steps": []
        }

    except Exception as e:
        return {
            "response": "Sorry, I cannot answer right now.",
            "next_steps": []
        }
