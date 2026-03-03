import json
import httpx
from dotenv import load_dotenv
from .config import load_settings
from .prompts import SYSTEM_PROMPT, USER_TEMPLATE
from .schemas import ScanResult

def scan(content: str, *, language: str = "python", input_type: str = "file", path_hint: str = "unknown") -> dict:
    """
    Returns a dict validated against ScanResult.
    Raises on invalid JSON or invalid schema.
    """
    load_dotenv()
    s = load_settings()

    payload = {
        "model": s.model,
        "temperature": s.temperature,
        "max_tokens": s.max_tokens,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": USER_TEMPLATE.format(
                language=language, input_type=input_type, path_hint=path_hint, content=content
            )},
        ],
    }

    headers = {"Authorization": f"Bearer {s.api_key}"}

    with httpx.Client(base_url=s.base_url, headers=headers, timeout=60.0) as client:
        r = client.post("/chat/completions", json=payload)
        r.raise_for_status()
        data = r.json()

    text = data["choices"][0]["message"]["content"]

    try:
        obj = json.loads(text)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Model returned invalid JSON:\n{text}") from e

    # Validate schema
    ScanResult.model_validate(obj)
    return obj