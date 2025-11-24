from typing import Dict

from rule_filter import run_rule_filter
from ml_classifier import classify, is_harmful_label
from llm_guard import check_with_llm

def run_pipeline(prompt: str) -> Dict[str, any]:
    if not prompt.strip():
        print("Prompt is empty - blocked")
        return {
            "decision": "UNSAFE",
            "stage": "precheck",
            "reason": "Empty prompt",
            "details": {}
        }

    details = {}  # Collect results from all stages

    # Stage 1: Rule filter (always run)
    print("Running rule filter...")
    rule_result = run_rule_filter(prompt)
    print(f"Rule result: score={rule_result.score}, triggers={rule_result.triggers}")
    details["rule"] = {"score": rule_result.score, "triggers": rule_result.triggers}
    rule_decision = "UNSAFE" if rule_result.score >= 1 else "SAFE"  # 1 or 2 considered unsafe for logging

    # Stage 2: ML classifier (always run)
    print("Running ML classifier...")
    ml_result = classify(prompt)
    print(f"ML result: label={ml_result.label}, confidence={ml_result.confidence}")
    details["ml"] = {"label": ml_result.label, "confidence": ml_result.confidence}
    ml_decision = "UNSAFE" if ml_result.confidence > 0.8 and is_harmful_label(ml_result) else "SAFE"

    # Stage 3: LLM guard (always run)
    print("Running LLM guard...")
    llm_result = check_with_llm(prompt)
    print(f"LLM result: safe={llm_result.safe}, category={llm_result.category}, severity={llm_result.severity}, reason={llm_result.reason}")
    details["llm"] = {"safe": llm_result.safe, "category": llm_result.category, "severity": llm_result.severity, "reason": llm_result.reason}
    llm_decision = "SAFE" if llm_result.safe else "UNSAFE"

    # Final decision: Block if ANY stage says UNSAFE, prioritize earliest block for "stage"
    if rule_decision == "UNSAFE":
        final_stage = "rule"
        final_decision = "UNSAFE"
        final_reason = f"Blocked at rule filter: score={rule_result.score}, triggers={rule_result.triggers}"
    elif ml_decision == "UNSAFE":
        final_stage = "ml"
        final_decision = "UNSAFE"
        final_reason = f"Blocked at ML: label={ml_result.label}, confidence={ml_result.confidence}"
    elif llm_decision == "UNSAFE":
        final_stage = "llm"
        final_decision = "UNSAFE"
        final_reason = f"Blocked at LLM: category={llm_result.category}, severity={llm_result.severity}, reason={llm_result.reason}"
    else:
        final_stage = "all"
        final_decision = "SAFE"
        final_reason = "Passed all stages"

    print(f"Final decision: {final_decision} at stage {final_stage}")

    return {
        "decision": final_decision,
        "stage": final_stage,
        "reason": final_reason,
        "details": details
    }
