from dataclasses import dataclass
from typing import List


@dataclass
class RuleResult:
    score: int  # 0 safe, 1 suspicious, 2 malicious
    triggers: List[str]


@dataclass
class ClassifierResult:
    label: str
    confidence: float


@dataclass
class LLMGuardResult:
    safe: bool
    category: str
    severity: int
    reason: str