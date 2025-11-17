from fw_types import ClassifierResult


HARMFUL_LABELS = {"harmful", "malicious", "unsafe"}


def classify(prompt: str) -> ClassifierResult:
    # Placeholder logic
    return ClassifierResult(label="unknown", confidence=0.0)


def is_harmful_label(result: ClassifierResult) -> bool:
    return result.label.lower() in HARMFUL_LABELS