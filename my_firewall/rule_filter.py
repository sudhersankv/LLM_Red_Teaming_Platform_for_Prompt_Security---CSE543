from dataclasses import dataclass
from typing import List

from fw_types import RuleResult   # Or fw_types if you renamed it
import regex as re

# Expanded from dataset: misinformation, chemical/biological, illegal/cyber, harmful, copyright
JAILBREAK_KEYWORDS = [
    "ignore previous instructions",
    "jailbreak",
    "system prompt",
    "override",  # From dataset: obfuscation, jailbreaks
]

CYBERCRIME_KEYWORDS = [
    "malware",
    "exploit",
    "zero-day",
    "hack",
    "ddos",
    "ransomware",
    "phishing",
    "sql injection",
    "csrf",
    "vulnerability",
    "backdoor",
    "rootkit",
    "scam",
    "botnet",  # From dataset: cybercrime_intrusion
]

VIOLENCE_KEYWORDS = [
    "kill",
    "assassinate",
    "bomb",
    "arson",
    "suicide",
    "self harm",
    "kill myself",
    "threat",
    "blackmail",
    "kidnapping",
    "hostage",  # From dataset: harmful, illegal
]

SEXUAL_KEYWORDS = [
    "explicit",
    "porn",
    "nsfw",
    "sexual assault",
    "harass",
    "bully",
    "coerce",  # From dataset: harassment_bullying
]

SELF_HARM_KEYWORDS = [  # Merged with violence for scoring
    "suicide",
    "self harm",
    "kill myself",
]

CHEM_BIO_KEYWORDS = [  # New category from dataset: chemical_biological
    "synthesize",
    "manufacture",
    "precursors",
    "pathway",
    "ricin",
    "sarin",
    "phosgene",
    "fentanyl",
    "meth",
    "cocaine",
    "lsd",
    "tabun",
    "botulinum",
    "ebola",
    "virus",
    "toxin",
    "nerve gas",
]

MISINFO_KEYWORDS = [  # New category from dataset: misinformation_disinformation
    "persuasive article",
    "arguing that",
    "propaganda",
    "hoax",
    "myth",
    "false claim",
    "exaggerated",
    "conspiracy",
    "fraud",
    "stolen election",
    "rigged",
    "genocide denial",
]

COPYRIGHT_KEYWORDS = [  # New category from dataset: copyright
    "lyrics of",
    "passage from",
    "generate long passage",
    "book",
    "novel",
]

SUSPICIOUS_PATTERNS = [
    re.compile(r"[A-Za-z0-9+/]{40,}={0,2}"),  # base64-like
    re.compile(r"<\s*script", re.IGNORECASE),
    re.compile(r"<\s*xml", re.IGNORECASE),
    re.compile(r"(?:payload|shellcode)\s*=", re.IGNORECASE),
    re.compile(r"(?:code|script|exploit|vulnerability)\s*obfuscat", re.IGNORECASE),  # From dataset: obfuscation
]

KEYWORD_CATEGORIES = {
    "jailbreak": JAILBREAK_KEYWORDS,
    "cybercrime": CYBERCRIME_KEYWORDS,
    "violence": VIOLENCE_KEYWORDS,
    "sexual": SEXUAL_KEYWORDS,
    "self_harm": SELF_HARM_KEYWORDS,
    "chem_bio": CHEM_BIO_KEYWORDS,
    "misinfo": MISINFO_KEYWORDS,
    "copyright": COPYRIGHT_KEYWORDS,
}

def run_rule_filter(prompt: str) -> RuleResult:
    lowered = prompt.lower()
    triggers: List[str] = []

    for category, keywords in KEYWORD_CATEGORIES.items():
        if any(keyword in lowered for keyword in keywords):
            triggers.append(category)

    for pattern in SUSPICIOUS_PATTERNS:
        if pattern.search(prompt):
            triggers.append("suspicious_pattern")
            break

    # Scoring: Immediate block for high-risk (violence, self-harm, chem/bio)
    if any(t in triggers for t in ["violence", "self_harm", "chem_bio"]):
        score = 2
    elif triggers:
        score = 1
    else:
        score = 0

    return RuleResult(score=score, triggers=triggers)