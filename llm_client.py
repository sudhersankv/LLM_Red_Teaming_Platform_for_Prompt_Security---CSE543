# llm_client.py
import os
from typing import List, Dict, Optional

from dotenv import load_dotenv
from groq import Groq

from config import (
    TARGET_MODEL,
    TARGET_TEMPERATURE,
    TARGET_MAX_TOKENS,
)

# Load .env if present
load_dotenv()

_client: Optional[Groq] = None


def get_client() -> Groq:
    """
    Singleton Groq client.
    Uses GROQ_API_KEY from environment or .env file.
    """
    global _client
    if _client is None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError("GROQ_API_KEY is not set in environment or .env")
        _client = Groq(api_key=api_key)
    return _client


def call_target_llm(
    messages: List[Dict[str, str]],
    model: Optional[str] = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
) -> Dict:
    """
    Call the target LLM hosted on Groq.

    Args:
        messages: list of {"role": "system"|"user"|"assistant", "content": str}
        model: override model name (optional)
        temperature: optional temperature override
        max_tokens: optional max_tokens override

    Returns:
        {
          "content": str,
          "raw": dict  # full response as JSON-serializable
        }
    """
    client = get_client()

    m = model or TARGET_MODEL
    temp = TARGET_TEMPERATURE if temperature is None else float(temperature)
    mtoks = TARGET_MAX_TOKENS if max_tokens is None else int(max_tokens)

    resp = client.chat.completions.create(
        model=m,
        messages=messages,
        temperature=temp,
        max_tokens=mtoks,
    )

    content = resp.choices[0].message.content or ""
    # `to_dict()` gives a JSON-serializable Python dict
    return {
        "content": content,
        "raw": resp.to_dict(),
    }
