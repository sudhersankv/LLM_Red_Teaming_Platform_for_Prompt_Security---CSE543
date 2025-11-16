# datasets_loader.py
from __future__ import annotations
import os

from dotenv import load_dotenv

from typing import List

from datasets import load_dataset

from attacks import AttackSample
from config import (
    USE_ADV_BENCH,
    USE_HARM_BENCH,
    USE_REAL_TOXICITY,
    MAX_SAMPLES_PER_DATASET,
)

hf_token = os.getenv("HF_API_KEY")

def _safe_slice(ds, max_n: int):
    for i, row in enumerate(ds):
        if i >= max_n:
            break
        yield i, row


def load_advbench() -> List[AttackSample]:
    """
    Example loader for a jailbreak-style dataset.
    NOTE: Replace 'llm-attacks/AdvBench' with the exact dataset id you want.
    """
    ds = load_dataset("shiv96/AdvBench_safe_unsafe_responses", split="train", token=hf_token)  # placeholder id
    samples: List[AttackSample] = []

    for i, row in _safe_slice(ds, MAX_SAMPLES_PER_DATASET):
        prompt = row.get("prompt") or ""
        if not prompt:
            continue

        label = row.get("label")
        original_response = row.get("response")

        samples.append(
            {
                "id": f"advbench_{i}",
                "attack_name": "advbench_dataset",
                "system": None,          # falls back to DEFAULT_SYSTEM_PROMPT
                "user": prompt,
                "meta": {
                    "source": "advbench",
                    "intent": "harmful",
                    "label": label,
                    "original_response": original_response,
                    "dataset_row_id": i,
                },
            }
        )

    return samples


def load_harmbench() -> List[AttackSample]:
    """
    Placeholder loader for a harm-oriented dataset.
    Ensure you comply with safety & licensing of whatever you load here.
    """
    ds = load_dataset("walledai/HarmBench", "contextual", split="train", token=hf_token)  # placeholder
    samples: List[AttackSample] = []

    for i, row in _safe_slice(ds, MAX_SAMPLES_PER_DATASET):
        user_prompt = row.get("prompt") or ""
        context = row.get("context") or ""
        category = row.get("category") or "unknown"

        if not user_prompt:
            continue

        if context.strip():
            full_user = f"Context:\n{context}\n\nUser prompt:\n{user_prompt}"
        else:
            full_user = user_prompt

        samples.append(
            {
                "id": f"harmbench_{i}",
                "attack_name": "harmbench_dataset",
                "system": None,
                "user": full_user,
                "meta": {
                    "source": "harmbench",
                    "category": category,
                    "intent": "harmful",
                    "dataset_row_id": i,
                },
            }
        )

    return samples



def load_all_dataset_samples() -> List[AttackSample]:
    """
    Return all enabled dataset-based samples based on config flags.
    """
    samples: List[AttackSample] = []

    if USE_ADV_BENCH:
        try:
            samples.extend(load_advbench())
        except Exception as e:
            print(f"[WARN] Failed to load AdvBench dataset: {e}")

    if USE_HARM_BENCH:
        try:
            samples.extend(load_harmbench())
        except Exception as e:
            print(f"[WARN] Failed to load HarmBench dataset: {e}")

    return samples
