import os
from dataclasses import dataclass

@dataclass(frozen=True)
class Settings:
    base_url: str
    api_key: str
    model: str
    temperature: float
    max_tokens: int

def load_settings() -> Settings:
    api_key = os.getenv("API_KEY")
    if not api_key:
        raise RuntimeError("Missing API_KEY. Create a .env file (see .env.example).")

    return Settings(
        base_url=os.getenv("BASE_URL", "https://api.openai.com/v1"),
        api_key=api_key,
        model=os.getenv("MODEL", "gpt-4.1-mini"),
        temperature=float(os.getenv("TEMPERATURE", "0.2")),
        max_tokens=int(os.getenv("MAX_TOKENS", "1600")),
    )