from typing import Optional

from groq import Groq
from my_firewall.fw_types import LLMGuardResult  # Assuming you renamed types.py to fw_types.py

from my_firewall import fw_config  # Updated from import config

_client: Optional[Groq] = None

def _get_client() -> Groq:
    global _client
    if _client is None:
        if not fw_config.GROQ_API_KEY:
            raise RuntimeError("GROQ_API_KEY is not set.")
        _client = Groq(api_key=fw_config.GROQ_API_KEY)
    return _client

def check_with_llm(prompt: str) -> LLMGuardResult:
    client = _get_client()
    # Updated to correct Groq SDK method, with lower max_tokens to avoid error
    completion = client.chat.completions.create(
        model=fw_config.GROQ_MODEL,  # e.g., "llama-guard-3-8b"
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0,
        max_tokens=512,  # Reduced to model max; adjust if needed
        top_p=1,
        stream=False,
        stop=None
    )

    # Get the full content
    content = completion.choices[0].message.content.strip()

    # Improved parsing for Llama Guard output (e.g., "safe" or "unsafe\nS1:Violence\nseverity:3\nreason:...")
    lines = content.split("\n")
    if lines[0].lower() == "safe":
        safe = True
        category = "none"
        severity = 0
        reason = ""
    else:
        safe = False
        category = lines[1] if len(lines) > 1 else "unknown"
        severity_str = lines[2] if len(lines) > 2 else "0"
        severity = int(severity_str.split(":")[-1].strip()) if ":" in severity_str else 0
        reason = " ".join(lines[3:]) if len(lines) > 3 else "Unsafe content detected"

    return LLMGuardResult(
        safe=safe,
        category=category,
        severity=severity,
        reason=reason,
    )