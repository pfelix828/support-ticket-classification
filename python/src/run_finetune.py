"""
Fine-tune GPT-4o-mini on the support ticket training set.

Two fine-tuning experiments:
1. Standard fine-tune on human-labeled training data
2. Distillation: o1-mini labels a subset with reasoning, then fine-tune on those
"""

import json
import os
import time
import tempfile
from pathlib import Path
from dotenv import load_dotenv

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import f1_score, classification_report
from openai import OpenAI

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
    cat_list = "\n".join(f"- {cat}: {desc}" for cat, desc in CATEGORY_DESCRIPTIONS.items())
    return f"""You are a support ticket classifier for OpenAI. Classify the ticket into exactly one category.

Categories:
{cat_list}

Respond with ONLY the category name, nothing else."""


def create_finetune_file(X_train, output_path):
    """Create JSONL file for fine-tuning."""
    system_prompt = build_system_prompt()
    with open(output_path, "w") as f:
        for _, row in X_train.iterrows():
            entry = {
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": row["text"]},
                    {"role": "assistant", "content": row["category"]},
                ]
            }
            f.write(json.dumps(entry) + "\n")
    print(f"  Created fine-tuning file: {output_path} ({len(X_train)} examples)")


def run_finetune(X_train, X_test, y_test, le):
    """Fine-tune GPT-4o-mini on the training set."""
    print("\n" + "=" * 60)
    print("Fine-Tune GPT-4o-mini (standard)")
    print("=" * 60)

    # Create training file
    train_path = Path(tempfile.mktemp(suffix=".jsonl"))
    create_finetune_file(X_train, train_path)

    # Upload file
    print("  Uploading training file...")
    with open(train_path, "rb") as f:
        file_obj = client.files.create(file=f, purpose="fine-tune")
    print(f"  File ID: {file_obj.id}")

    # Create fine-tuning job
    print("  Starting fine-tuning job...")
    job = client.fine_tuning.jobs.create(
        training_file=file_obj.id,
        model="gpt-4o-mini-2024-07-18",
        hyperparameters={"n_epochs": 3},
    )
    print(f"  Job ID: {job.id}")

    # Wait for completion
    while True:
        job = client.fine_tuning.jobs.retrieve(job.id)
        print(f"  Status: {job.status}")
        if job.status in ("succeeded", "failed", "cancelled"):
            break
        time.sleep(30)

    if job.status != "succeeded":
        print(f"  Fine-tuning failed: {job.status}")
        return None

    model_id = job.fine_tuned_model
    print(f"  Fine-tuned model: {model_id}")

    # Evaluate on test set
    return evaluate_model(model_id, "Fine-Tuned GPT-4o-mini", X_test, y_test, le)


def run_distillation(X_train, X_test, y_test, le):
    """
    Distillation: use o1-mini to label 1K training tickets with reasoning,
    then fine-tune GPT-4o-mini on those labels.
    """
    print("\n" + "=" * 60)
    print("Distillation: o1-mini → GPT-4o-mini")
    print("=" * 60)

    # Sample 1K tickets for o1-mini labeling
    sample = X_train.sample(n=min(1000, len(X_train)), random_state=42)
    print(f"  Labeling {len(sample)} tickets with o1-mini...")

    cat_list = "\n".join(f"- {cat}: {desc}" for cat, desc in CATEGORY_DESCRIPTIONS.items())
    o1_system = f"""Classify this support ticket into one category. First explain your reasoning, then output the category.

Categories:
{cat_list}

Format your response as:
Reasoning: <your reasoning>
Category: <category_name>"""

    o1_labeled = []
    errors = 0

    for i, (_, row) in enumerate(sample.iterrows()):
        try:
            response = client.chat.completions.create(
                model="o1-mini",
                messages=[
                    {"role": "user", "content": f"{o1_system}\n\nTicket: {row['text']}"},
                ],
                max_completion_tokens=300,
            )
            content = response.choices[0].message.content.strip()

            # Extract category from response
            category = None
            for line in content.split("\n"):
                if line.lower().startswith("category:"):
                    cat = line.split(":", 1)[1].strip().lower()
                    cat = cat.replace('"', '').replace("'", "").strip()
                    if cat in CATEGORIES:
                        category = cat
                    else:
                        matched = [c for c in CATEGORIES if c in cat or cat in c]
                        category = matched[0] if matched else None

            if category:
                o1_labeled.append({
                    "text": row["text"],
                    "category": category,
                    "reasoning": content,
                })
            else:
                errors += 1

        except Exception as e:
            errors += 1
            if i < 3:
                print(f"    Error: {e}")

        if (i + 1) % 100 == 0:
            print(f"  Labeled {i+1}/{len(sample)} ({errors} errors)...")

    print(f"  o1-mini labeled {len(o1_labeled)} tickets ({errors} errors)")

    if len(o1_labeled) < 100:
        print("  Not enough labeled data, skipping distillation")
        return None

    # Save o1 labels
    with open(DATA_DIR / "o1_labels.json", "w") as f:
        json.dump(o1_labeled, f, indent=2)

    # Create fine-tuning file from o1 labels (include reasoning in training)
    system_prompt = build_system_prompt()
    train_path = Path(tempfile.mktemp(suffix=".jsonl"))
    with open(train_path, "w") as f:
        for item in o1_labeled:
            entry = {
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": item["text"]},
                    {"role": "assistant", "content": item["category"]},
                ]
            }
            f.write(json.dumps(entry) + "\n")

    print(f"  Created distillation training file ({len(o1_labeled)} examples)")

    # Upload and fine-tune
    print("  Uploading training file...")
    with open(train_path, "rb") as f:
        file_obj = client.files.create(file=f, purpose="fine-tune")

    print("  Starting fine-tuning job...")
    job = client.fine_tuning.jobs.create(
        training_file=file_obj.id,
        model="gpt-4o-mini-2024-07-18",
        hyperparameters={"n_epochs": 3},
    )
    print(f"  Job ID: {job.id}")

    while True:
        job = client.fine_tuning.jobs.retrieve(job.id)
        print(f"  Status: {job.status}")
        if job.status in ("succeeded", "failed", "cancelled"):
            break
        time.sleep(30)

    if job.status != "succeeded":
        print(f"  Distillation fine-tuning failed: {job.status}")
        return None

    model_id = job.fine_tuned_model
    print(f"  Distilled model: {model_id}")

    return evaluate_model(model_id, "Distilled (o1-mini → GPT-4o-mini)", X_test, y_test, le)


def evaluate_model(model_id, method_name, X_test, y_test, le):
    """Evaluate a fine-tuned model on the test set."""
    print(f"\n  Evaluating {method_name} on {len(X_test)} test tickets...")

    system_prompt = build_system_prompt()
    predictions = []
    errors = 0

    for i, (_, row) in enumerate(X_test.iterrows()):
        try:
            response = client.chat.completions.create(
                model=model_id,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": row["text"]},
                ],
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
            print(f"    Evaluated {i+1}/{len(X_test)}...")

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

    report = classification_report(valid_true, valid_preds, target_names=le.classes_, output_dict=True)
    per_class_f1 = {cls: round(report[cls]["f1-score"], 4) for cls in le.classes_}

    return {
        "method": method_name,
        "model_id": model_id,
        "f1_macro": round(f1_macro, 4),
        "f1_weighted": round(f1_weighted, 4),
        "per_class_f1": per_class_f1,
    }


def main():
    X_train, X_test, y_train, y_test, le = load_data()
    print(f"Train: {len(X_train)}, Test: {len(X_test)}")

    results_path = DATA_DIR / "model_results.json"
    with open(results_path) as f:
        results = json.load(f)

    # Standard fine-tune
    ft_result = run_finetune(X_train, X_test, y_test, le)
    if ft_result:
        results["finetune"] = ft_result
        with open(results_path, "w") as f:
            json.dump(results, f, indent=2)
        print(f"\nSaved fine-tune results")

    # Distillation
    distill_result = run_distillation(X_train, X_test, y_test, le)
    if distill_result:
        results["distillation"] = distill_result
        with open(results_path, "w") as f:
            json.dump(results, f, indent=2)
        print(f"\nSaved distillation results")

    # Summary
    print("\n" + "=" * 60)
    print("ALL RESULTS")
    print("=" * 60)
    for key, r in results.items():
        if isinstance(r, dict) and "f1_macro" in r:
            print(f"  {r.get('method', key):35s}  F1={r['f1_macro']:.4f}")


if __name__ == "__main__":
    main()
