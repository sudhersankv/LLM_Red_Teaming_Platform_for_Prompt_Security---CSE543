from my_firewall.fw_types import ClassifierResult
from transformers import pipeline
import torch

MODEL_PATH = "/Users/ritamupadhyay/Documents/MS/Fall 25/CSE 543/red_teaming/my_firewall/prompt_classifier_model"  # Full path to the model folder
classifier = pipeline("text-classification", model=MODEL_PATH, return_all_scores=True)

def classify(prompt: str) -> ClassifierResult:
    # Run the model on the prompt (adapted from your Colab predict)
    outputs = classifier(prompt)[0]  # List of [{"label": "LABEL_0", "score": ...}, {"label": "LABEL_1", "score": ...}]
    
    # Find the prediction with max score
    pred = max(outputs, key=lambda x: x["score"])
    label_num = int(pred["label"].split("_")[-1])  # Extract 0 or 1
    confidence = float(pred["score"])
    
    # Map to string labels for our pipeline
    label = "harmful" if label_num == 1 else "safe"
    
    return ClassifierResult(label=label, confidence=confidence)

def is_harmful_label(result: ClassifierResult) -> bool:
    return result.label == "harmful"