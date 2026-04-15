"""
Run OpenAI API-based classification experiments:
1. GPT-4o-mini zero-shot
2. GPT-4o-mini few-shot (3 examples per category)
3. Fine-tuned GPT-4o-mini
4. o1-mini distillation → fine-tuned GPT-4o-mini

Loads train/test split from the realistic ticket dataset.
"""

import json
import os
import time
import random
from pathlib import Path
from collections import Counter
from dotenv import load_dotenv

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import f1_score, classification_report
from openai import OpenAI

# Load env
load_dotenv(Path(__file__).parent.parent / ".env")
client = OpenAI()

DATA_DIR = Path(__file__).parent.parent.parent / "app" / "public" / "data"

CATEGORIES = [
    "account_access", "account_management", "api_errors", "api_usage",
    "billing", "chatgpt_apps", "chatgpt_product", "enterprise",
    "gpts", "newer_products", "privacy_policy", "security",
]

CATEGORY_DESCRIPTIONS = {
    "billing": "Refunds, charges, payment methods, invoices, credits, subscription pricing",
    "account_access": "Login issues, password reset, account recovery, phone verification, locked out",
    "account_management": "Organization members, email changes, org settings, projects, roles/permissions",
    "api_errors": "Rate limits, 429/500 errors, API key issues, latency, timeouts, error codes",
    "api_usage": "How-to questions, getting started, best practices, model selection, SDK setup",
    "chatgpt_product": "ChatGPT features, errors, slow responses, image generation, search, memory, voice",
    "chatgpt_apps": "iOS, Android, macOS, Windows app issues, connected apps, app store subscriptions",
    "enterprise": "Enterprise/Business/Edu workspace setup, SSO, SCIM, admin console, compliance",
    "gpts": "Custom GPT creation, publishing, configuration, actions, GPT Store, knowledge files",
    "newer_products": "Sora (video), Codex (coding), ChatGPT Atlas (browser) — newer product issues",
    "privacy_policy": "Data privacy, training opt-out, data export, GDPR/CCPA, data retention",
    "security": "API key safety, leaked keys, unauthorized usage, vulnerability reporting",
}


def load_data():
    """Load and split the realistic ticket dataset."""
    with open(DATA_DIR / "tickets.json") as f:
        tickets = json.load(f)

    df = pd.DataFrame(tickets)
    df = df.drop_duplicates(subset="text", keep="first").copy()

    le = LabelEncoder()
    le.fit(CATEGORIES)
    df["label"] = le.transform(df["category"])

    X_train, X_test, y_train, y_test = train_test_split(
        df, df["label"], test_size=0.2, random_state=42, stratify=df["label"]
    )
    return X_train, X_test, y_train, y_test, le


def build_system_prompt():
    """Build the classification system prompt."""
    cat_list = "\n".join(f"- {cat}: {desc}" for cat, desc in CATEGORY_DESCRIPTIONS.items())
    return f"""You are a support ticket classifier for OpenAI. Classify the ticket into exactly one category.

Categories:
{cat_list}

Respond with ONLY the category name, nothing else. For example: billing"""


def build_fewshot_examples(X_train):
    """Select 3 representative examples per category for few-shot."""
    examples = []
    for cat in CATEGORIES:
        cat_tickets = X_train[X_train["category"] == cat]["text"].tolist()
        # Pick 3 short, clear examples
        sorted_by_len = sorted(cat_tickets, key=len)
        selected = sorted_by_len[:3] if len(sorted_by_len) >= 3 else sorted_by_len
        for t in selected:
            examples.append({"text": t, "category": cat})
    return examples


# ---------------------------------------------------------------------------
# 1. Zero-shot
# ---------------------------------------------------------------------------

def run_zero_shot(X_test, y_test, le):
    """Classify test set with GPT-4o-mini zero-shot."""
    print("\n" + "=" * 60)
    print("GPT-4o-mini Zero-Shot")
    print("=" * 60)

    system_prompt = build_system_prompt()
    predictions = []
    errors = 0

    for i, (_, row) in enumerate(X_test.iterrows()):
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": row["text"]},
                ],
                max_tokens=20,
                temperature=0,
            )
            pred = response.choices[0].message.content.strip().lower()
            # Clean up prediction
            pred = pred.replace('"', '').replace("'", "").strip()
            if pred not in CATEGORIES:
                # Try partial match
                matched = [c for c in CATEGORIES if c in pred or pred in c]
                pred = matched[0] if matched else "unknown"
            predictions.append(pred)
        except Exception as e:
            predictions.append("unknown")
            errors += 1

        if (i + 1) % 100 == 0:
            print(f"  Processed {i+1}/{len(X_test)}...")

    # Metrics
    y_pred_encoded = []
    valid_mask = []
    for i, pred in enumerate(predictions):
        if pred in CATEGORIES:
            y_pred_encoded.append(le.transform([pred])[0])
            valid_mask.append(True)
        else:
            y_pred_encoded.append(-1)
            valid_mask.append(False)

    y_test_arr = y_test.values
    valid_preds = [y_pred_encoded[i] for i in range(len(valid_mask)) if valid_mask[i]]
    valid_true = [y_test_arr[i] for i in range(len(valid_mask)) if valid_mask[i]]

    f1_macro = f1_score(valid_true, valid_preds, average="macro")
    f1_weighted = f1_score(valid_true, valid_preds, average="weighted")

    print(f"  F1 macro: {f1_macro:.4f}")
    print(f"  F1 weighted: {f1_weighted:.4f}")
    print(f"  Errors/unknowns: {errors + sum(1 for v in valid_mask if not v)}")

    report = classification_report(valid_true, valid_preds, target_names=le.classes_, output_dict=True)
    per_class_f1 = {cls: round(report[cls]["f1-score"], 4) for cls in le.classes_}

    return {
        "method": "GPT-4o-mini Zero-Shot",
        "f1_macro": round(f1_macro, 4),
        "f1_weighted": round(f1_weighted, 4),
        "per_class_f1": per_class_f1,
        "unknown_count": sum(1 for v in valid_mask if not v),
    }


# ---------------------------------------------------------------------------
# 2. Few-shot
# ---------------------------------------------------------------------------

def run_few_shot(X_train, X_test, y_test, le):
    """Classify test set with GPT-4o-mini few-shot (3 examples per category)."""
    print("\n" + "=" * 60)
    print("GPT-4o-mini Few-Shot")
    print("=" * 60)

    system_prompt = build_system_prompt()
    examples = build_fewshot_examples(X_train)

    # Build few-shot messages
    fewshot_messages = [{"role": "system", "content": system_prompt}]
    for ex in examples:
        fewshot_messages.append({"role": "user", "content": ex["text"]})
        fewshot_messages.append({"role": "assistant", "content": ex["category"]})

    predictions = []
    errors = 0

    for i, (_, row) in enumerate(X_test.iterrows()):
        try:
            messages = fewshot_messages + [{"role": "user", "content": row["text"]}]
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=20,
                temperature=0,
            )
            pred = response.choices[0].message.content.strip().lower()
            pred = pred.replace('"', '').replace("'", "").strip()
            if pred not in CATEGORIES:
                matched = [c for c in CATEGORIES if c in pred or pred in c]
                pred = matched[0] if matched else "unknown"
            predictions.append(pred)
        except Exception as e:
            predictions.append("unknown")
            errors += 1

        if (i + 1) % 100 == 0:
            print(f"  Processed {i+1}/{len(X_test)}...")

    y_test_arr = y_test.values
    y_pred_encoded = []
    valid_mask = []
    for pred in predictions:
        if pred in CATEGORIES:
            y_pred_encoded.append(le.transform([pred])[0])
            valid_mask.append(True)
        else:
            y_pred_encoded.append(-1)
            valid_mask.append(False)

    valid_preds = [y_pred_encoded[i] for i in range(len(valid_mask)) if valid_mask[i]]
    valid_true = [y_test_arr[i] for i in range(len(valid_mask)) if valid_mask[i]]

    f1_macro = f1_score(valid_true, valid_preds, average="macro")
    f1_weighted = f1_score(valid_true, valid_preds, average="weighted")

    print(f"  F1 macro: {f1_macro:.4f}")
    print(f"  F1 weighted: {f1_weighted:.4f}")
    print(f"  Errors/unknowns: {errors + sum(1 for v in valid_mask if not v)}")

    report = classification_report(valid_true, valid_preds, target_names=le.classes_, output_dict=True)
    per_class_f1 = {cls: round(report[cls]["f1-score"], 4) for cls in le.classes_}

    return {
        "method": "GPT-4o-mini Few-Shot",
        "f1_macro": round(f1_macro, 4),
        "f1_weighted": round(f1_weighted, 4),
        "per_class_f1": per_class_f1,
        "unknown_count": sum(1 for v in valid_mask if not v),
    }


# ---------------------------------------------------------------------------
# Main — run zero-shot and few-shot first
# ---------------------------------------------------------------------------

def main():
    X_train, X_test, y_test_series = None, None, None

    X_train, X_test, y_train, y_test, le = load_data()
    print(f"Train: {len(X_train)}, Test: {len(X_test)}")

    # Load existing results
    results_path = DATA_DIR / "model_results.json"
    if results_path.exists():
        with open(results_path) as f:
            results = json.load(f)
    else:
        results = {}

    # Zero-shot
    results["zero_shot"] = run_zero_shot(X_test, y_test, le)

    # Save after each experiment
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved results to {results_path}")

    # Few-shot
    results["few_shot"] = run_few_shot(X_train, X_test, y_test, le)

    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved results to {results_path}")

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY (all methods)")
    print("=" * 60)
    for key, r in results.items():
        if isinstance(r, dict) and "f1_macro" in r:
            print(f"  {r.get('method', key):35s}  F1={r['f1_macro']:.4f}")


if __name__ == "__main__":
    main()
