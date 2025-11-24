from typing import Any, Dict

from my_firewall.rule_filter import run_rule_filter
from my_firewall.ml_classifier import classify, is_harmful_label
from my_firewall.llm_guard import check_with_llm


def run_pipeline(prompt: str) -> dict:  # Changed to return dict for compatibility
    if not prompt.strip():
        print("Prompt is empty - blocked")
        return {"decision": "UNSAFE", "reason": "Empty prompt"}

    print("Running rule filter...")
    rule_result = run_rule_filter(prompt)
    print(f"Rule result: score={rule_result.score}, triggers={rule_result.triggers}")

    if rule_result.score == 2:
        print("Blocked at rule filter (malicious)")
        return {"decision": "UNSAFE", "reason": f"Rule filter blocked: score=2, triggers={rule_result.triggers}"}

    if rule_result.score == 0:
        print("Allowed at rule filter (safe)")
        return {"decision": "SAFE", "reason": "Passed rule filter"}

    print("Running ML classifier...")
    ml_result = classify(prompt)
    print(f"ML result: label={ml_result.label}, confidence={ml_result.confidence}")

    if ml_result.confidence > 0.8 and is_harmful_label(ml_result):
        print("Blocked at ML classifier (harmful)")
        return {"decision": "UNSAFE", "reason": f"ML blocked: label={ml_result.label}, confidence={ml_result.confidence}"}

    print("Running LLM guard...")
    llm_result = check_with_llm(prompt)
    print(f"LLM result: safe={llm_result.safe}, category={llm_result.category}, severity={llm_result.severity}, reason={llm_result.reason}")

    if llm_result.safe:
        print("Allowed at LLM guard (safe)")
        return {"decision": "SAFE", "reason": f"Passed LLM guard: category={llm_result.category}"}
    else:
        print("Blocked at LLM guard (unsafe)")
        return {"decision": "UNSAFE", "reason": f"LLM blocked: category={llm_result.category}, severity={llm_result.severity}, reason={llm_result.reason}"}