# pipeline.py
from __future__ import annotations

import json
import time
from typing import Dict, Any, Iterable, List

from tqdm import tqdm

from config import (
    DEFAULT_SYSTEM_PROMPT,
    BASELINE_LOG,
    FIREWALL_LOG,
)
from attacks import get_builtin_strategies, AttackSample
from datasets_loader import load_all_dataset_samples
from evaluator import heuristic_evaluate, eval_to_dict
from llm_client import call_target_llm
from firewall import firewall_check


def iter_builtin_samples() -> Iterable[AttackSample]:
    for strategy in get_builtin_strategies():
        for sample in strategy.generate():
            sample.setdefault("attack_name", strategy.name)
            sample.setdefault("meta", {})
            yield sample


def iter_all_samples() -> List[AttackSample]:
    """
    Collect all samples we want to run: built-in + datasets.
    """
    samples: List[AttackSample] = []

    # Built-in strategies
    samples.extend(list(iter_builtin_samples()))

    # Dataset-based samples (optional)
    ds_samples = load_all_dataset_samples()
    samples.extend(ds_samples)

    return samples


def run_baseline() -> None:
    """
    Run red-teaming WITHOUT any firewall. Directly hits the target model.
    """
    samples = iter_all_samples()
    print(f"[Baseline] Running on {len(samples)} samples...")

    with open(BASELINE_LOG, "w", encoding="utf-8") as f_out:
        for sample in tqdm(samples, desc="Baseline"):
            system_prompt = sample.get("system") or DEFAULT_SYSTEM_PROMPT
            user_prompt = sample["user"]

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ]

            try:
                llm_result = call_target_llm(messages)
                response_text = llm_result["content"]
            except Exception as e:
                llm_result = {"error": str(e)}
                response_text = ""

            ev = heuristic_evaluate(sample, response_text)

            record: Dict[str, Any] = {
                "timestamp": time.time(),
                "mode": "baseline",
                "sample": sample,
                "response_text": response_text,
                "response_raw": llm_result.get("raw", llm_result),
                "firewall": None,
                "evaluation": eval_to_dict(ev),
            }

            f_out.write(json.dumps(record, ensure_ascii=False) + "\n")

    print(f"[Baseline] Done. Results saved to {BASELINE_LOG}")


def run_with_firewall() -> None:
    """
    Run red-teaming WITH an LLM firewall.

    Flow:
      - Firewall sees the user prompt.
      - If UNSAFE → we do NOT call the target model; log as blocked.
      - If SAFE   → call the target model and evaluate its response.
    """
    samples = iter_all_samples()
    print(f"[Firewall] Running on {len(samples)} samples...")

    with open(FIREWALL_LOG, "w", encoding="utf-8") as f_out:
        for sample in tqdm(samples, desc="Firewall"):
            user_prompt = sample["user"]

            fw = firewall_check(user_prompt)
            fw_decision = fw.get("decision", "SAFE").upper()
            fw_reason = fw.get("reason", "")

            if fw_decision == "UNSAFE":
                # Blocked: do not call target model
                record: Dict[str, Any] = {
                    "timestamp": time.time(),
                    "mode": "firewall",
                    "sample": sample,
                    "response_text": "[BLOCKED_BY_FIREWALL]",
                    "response_raw": None,
                    "firewall": {
                        "decision": fw_decision,
                        "reason": fw_reason,
                    },
                    "evaluation": {
                        "is_flagged": False,
                        "reasons": [],
                        "notes": "Blocked before model call.",
                    },
                }
                f_out.write(json.dumps(record, ensure_ascii=False) + "\n")
                continue

            # SAFE → call target model
            system_prompt = sample.get("system") or DEFAULT_SYSTEM_PROMPT
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ]

            try:
                llm_result = call_target_llm(messages)
                response_text = llm_result["content"]
            except Exception as e:
                llm_result = {"error": str(e)}
                response_text = ""

            ev = heuristic_evaluate(sample, response_text)

            record = {
                "timestamp": time.time(),
                "mode": "firewall",
                "sample": sample,
                "response_text": response_text,
                "response_raw": llm_result.get("raw", llm_result),
                "firewall": {
                    "decision": fw_decision,
                    "reason": fw_reason,
                },
                "evaluation": eval_to_dict(ev),
            }

            f_out.write(json.dumps(record, ensure_ascii=False) + "\n")

    print(f"[Firewall] Done. Results saved to {FIREWALL_LOG}")
