"""
Distillation at scale: use o4-mini via Batch API to label the full training set,
then fine-tune GPT-4o-mini on those labels.

Previous run used only 855 labels → 69.9% F1. This uses ~9,557 labels for a fair comparison.

Usage:
  python -m src.run_distillation_batch label     # Submit o4-mini labeling batch
  python -m src.run_distillation_batch status    # Check batch status
  python -m src.run_distillation_batch finetune  # Parse labels, create FT job
  python -m src.run_distillation_batch eval      # Submit eval batch for the fine-tuned model
"""

import json
import sys
from pathlib import Path
from dotenv import load_dotenv

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from openai import OpenAI

load_dotenv(Path(__file__).parent.parent / ".env")
client = OpenAI()

DATA_DIR = Path(__file__).parent.parent.parent / "app" / "public" / "data"
BATCH_DIR = Path(__file__).parent.parent / "batch"
BATCH_DIR.mkdir(exist_ok=True)

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


def build_labeling_prompt():
    cat_list = "\n".join(f"- {cat}: {desc}" for cat, desc in CATEGORY_DESCRIPTIONS.items())
    return f"""Classify this support ticket into exactly one category. First explain your reasoning briefly, then output the category.

Categories:
{cat_list}

Format your response as:
Reasoning: <your reasoning>
Category: <category_name>"""


def label():
    """Submit o4-mini labeling batch for the full training set."""
    X_train, _, _, _, _ = load_data()
    print(f"Training set: {len(X_train)} tickets")

    prompt = build_labeling_prompt()
    texts = X_train["text"].tolist()

    # Build batch requests
    requests = []
    for i, text in enumerate(texts):
        request = {
            "custom_id": f"distill-{i}",
            "method": "POST",
            "url": "/v1/chat/completions",
            "body": {
                "model": "o4-mini",
                "messages": [
                    {"role": "user", "content": f"{prompt}\n\nTicket: {text}"},
                ],
                "max_completion_tokens": 300,
            },
        }
        requests.append(request)

    # Write JSONL
    req_path = BATCH_DIR / "distill_label_requests.jsonl"
    with open(req_path, "w") as f:
        for req in requests:
            f.write(json.dumps(req) + "\n")
    print(f"Wrote {len(requests)} requests to {req_path}")

    # Submit batch
    file_obj = client.files.create(file=open(req_path, "rb"), purpose="batch")
    batch = client.batches.create(
        input_file_id=file_obj.id,
        endpoint="/v1/chat/completions",
        completion_window="24h",
        metadata={"method": "distill_labeling"},
    )
    print(f"Submitted batch: {batch.id}")

    # Save batch ID
    meta = {"label_batch_id": batch.id, "train_size": len(X_train)}
    with open(BATCH_DIR / "distill_meta.json", "w") as f:
        json.dump(meta, f, indent=2)
    print("Saved to batch/distill_meta.json")
    print("Run: python -m src.run_distillation_batch status")


def status():
    """Check labeling batch status."""
    with open(BATCH_DIR / "distill_meta.json") as f:
        meta = json.load(f)

    bid = meta.get("label_batch_id") or meta.get("eval_batch_id")
    if not bid:
        print("No batch ID found")
        return

    b = client.batches.retrieve(bid)
    completed = b.request_counts.completed if b.request_counts else 0
    failed = b.request_counts.failed if b.request_counts else 0
    total = b.request_counts.total if b.request_counts else 0
    print(f"Batch {bid}")
    print(f"  Status: {b.status}")
    print(f"  Completed: {completed}/{total} ({failed} failed)")

    if b.status == "completed":
        if "label_batch_id" in meta and bid == meta["label_batch_id"]:
            print("\nLabeling done! Run: python -m src.run_distillation_batch finetune")
        elif "eval_batch_id" in meta and bid == meta["eval_batch_id"]:
            print("\nEval done! Run: python -m src.run_distillation_batch results")


def finetune():
    """Download labeling results, parse categories, submit fine-tuning job."""
    with open(BATCH_DIR / "distill_meta.json") as f:
        meta = json.load(f)

    bid = meta["label_batch_id"]
    b = client.batches.retrieve(bid)
    if b.status != "completed":
        print(f"Labeling batch not done yet: {b.status}")
        return

    # Download results
    output_path = BATCH_DIR / "distill_label_output.jsonl"
    content = client.files.content(b.output_file_id)
    with open(output_path, "wb") as f:
        f.write(content.read())
    print(f"Downloaded {output_path}")

    # Parse labels
    X_train, _, _, _, _ = load_data()
    texts = X_train["text"].tolist()

    labeled = []
    errors = 0
    with open(output_path) as f:
        for line in f:
            resp = json.loads(line)
            idx = int(resp["custom_id"].split("-")[-1])

            if resp.get("error"):
                errors += 1
                continue

            content = resp["response"]["body"]["choices"][0]["message"]["content"]

            # Parse category from response
            category = None
            for resp_line in content.split("\n"):
                if resp_line.lower().startswith("category:"):
                    cat = resp_line.split(":", 1)[1].strip().lower()
                    cat = cat.replace('"', '').replace("'", "").strip()
                    if cat in CATEGORIES:
                        category = cat
                    else:
                        matched = [c for c in CATEGORIES if c in cat or cat in c]
                        category = matched[0] if matched else None

            if category:
                labeled.append({"text": texts[idx], "category": category})
            else:
                errors += 1

    print(f"Parsed {len(labeled)} labels ({errors} errors out of {meta['train_size']})")

    # Save labels
    with open(BATCH_DIR / "distill_labels_full.json", "w") as f:
        json.dump(labeled, f, indent=2)

    # Create fine-tuning JSONL
    cat_list = "\n".join(f"- {cat}: {desc}" for cat, desc in CATEGORY_DESCRIPTIONS.items())
    system_prompt = f"""You are a support ticket classifier for OpenAI. Classify the ticket into exactly one category.

Categories:
{cat_list}

Respond with ONLY the category name, nothing else."""

    import tempfile
    ft_path = Path(tempfile.mktemp(suffix=".jsonl"))
    with open(ft_path, "w") as f:
        for item in labeled:
            entry = {
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": item["text"]},
                    {"role": "assistant", "content": item["category"]},
                ]
            }
            f.write(json.dumps(entry) + "\n")

    print(f"Created fine-tuning file: {ft_path} ({len(labeled)} examples)")

    # Upload and start fine-tuning
    print("Uploading training file...")
    with open(ft_path, "rb") as f:
        file_obj = client.files.create(file=f, purpose="fine-tune")

    print("Starting fine-tuning job...")
    job = client.fine_tuning.jobs.create(
        training_file=file_obj.id,
        model="gpt-4o-mini-2024-07-18",
        hyperparameters={"n_epochs": 3},
    )
    print(f"Job ID: {job.id}")

    meta["ft_job_id"] = job.id
    meta["label_count"] = len(labeled)
    with open(BATCH_DIR / "distill_meta.json", "w") as f:
        json.dump(meta, f, indent=2)
    print("Run: python -m src.run_distillation_batch status")


def eval_cmd():
    """Submit eval batch for the fine-tuned distillation model."""
    with open(BATCH_DIR / "distill_meta.json") as f:
        meta = json.load(f)

    job = client.fine_tuning.jobs.retrieve(meta["ft_job_id"])
    print(f"Fine-tuning: status={job.status}, model={job.fine_tuned_model}")

    if job.status != "succeeded" or not job.fine_tuned_model:
        print("Fine-tuning not done yet")
        return

    model_id = job.fine_tuned_model
    X_train, X_test, _, _, _ = load_data()
    eval_texts = X_test["text"].tolist()

    cat_list = "\n".join(f"- {cat}: {desc}" for cat, desc in CATEGORY_DESCRIPTIONS.items())
    system_prompt = f"""You are a support ticket classifier for OpenAI. Classify the ticket into exactly one category.

Categories:
{cat_list}

Respond with ONLY the category name, nothing else. For example: billing"""

    # Build eval batch
    requests = []
    for i, text in enumerate(eval_texts):
        request = {
            "custom_id": f"distill_v2-{i}",
            "method": "POST",
            "url": "/v1/chat/completions",
            "body": {
                "model": model_id,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text},
                ],
                "max_tokens": 20,
                "temperature": 0,
            },
        }
        requests.append(request)

    req_path = BATCH_DIR / "distill_v2_eval_requests.jsonl"
    with open(req_path, "w") as f:
        for req in requests:
            f.write(json.dumps(req) + "\n")

    file_obj = client.files.create(file=open(req_path, "rb"), purpose="batch")
    batch = client.batches.create(
        input_file_id=file_obj.id,
        endpoint="/v1/chat/completions",
        completion_window="24h",
        metadata={"method": "distilled_v2", "model_id": model_id},
    )
    print(f"Submitted eval batch: {batch.id}")

    meta["eval_batch_id"] = batch.id
    meta["model_id"] = model_id
    with open(BATCH_DIR / "distill_meta.json", "w") as f:
        json.dump(meta, f, indent=2)
    print("Run: python -m src.run_distillation_batch status")


def results():
    """Download eval results and compute metrics."""
    from sklearn.metrics import f1_score, classification_report
    from src.run_batch import parse_prediction

    with open(BATCH_DIR / "distill_meta.json") as f:
        meta = json.load(f)
    with open(BATCH_DIR / "test_meta.json") as f:
        test_meta = json.load(f)

    le = LabelEncoder()
    le.fit(CATEGORIES)
    y_true = test_meta["labels"]
    eval_size = test_meta["eval_size"]

    bid = meta["eval_batch_id"]
    b = client.batches.retrieve(bid)
    if b.status != "completed":
        print(f"Eval batch not done: {b.status}")
        return

    output_path = BATCH_DIR / "distill_v2_eval_output.jsonl"
    content = client.files.content(b.output_file_id)
    with open(output_path, "wb") as f:
        f.write(content.read())

    predictions = ["unknown"] * eval_size
    with open(output_path) as f:
        for line in f:
            resp = json.loads(line)
            idx = int(resp["custom_id"].split("-")[-1])
            if resp.get("error"):
                predictions[idx] = "unknown"
            else:
                text = resp["response"]["body"]["choices"][0]["message"]["content"]
                predictions[idx] = parse_prediction(text)

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
    valid_true = [y_true[i] for i in range(len(valid_mask)) if valid_mask[i]]

    labels = list(range(len(CATEGORIES)))
    f1_macro = f1_score(valid_true, valid_preds, average="macro", labels=labels, zero_division=0)
    f1_weighted = f1_score(valid_true, valid_preds, average="weighted", labels=labels, zero_division=0)

    report = classification_report(valid_true, valid_preds, target_names=le.classes_,
                                   labels=labels, output_dict=True, zero_division=0)
    per_class_f1 = {cls: round(report.get(cls, {}).get("f1-score", 0), 4) for cls in le.classes_}

    unknown_count = sum(1 for v in valid_mask if not v)

    print(f"\nDistillation v2 (o4-mini → GPT-4o-mini, {meta['label_count']} teacher labels)")
    print(f"  F1 macro:   {f1_macro:.4f}")
    print(f"  F1 weighted: {f1_weighted:.4f}")
    print(f"  Unknowns:   {unknown_count}/{eval_size}")
    print(f"  Per-class F1:")
    for cls, f1 in sorted(per_class_f1.items(), key=lambda x: x[1]):
        print(f"    {cls:<25} {f1:.4f}")

    # Save to model_results.json
    results_path = DATA_DIR / "model_results.json"
    with open(results_path) as f:
        model_results = json.load(f)

    model_results["distilled"] = {
        "method": f"GPT-4o-mini Distillation FT ({meta['label_count']} teacher labels)",
        "f1_macro": round(f1_macro, 4),
        "f1_weighted": round(f1_weighted, 4),
        "per_class_f1": per_class_f1,
        "unknown_count": unknown_count,
        "eval_size": eval_size,
        "model_id": meta.get("model_id"),
        "label_count": meta["label_count"],
    }
    with open(results_path, "w") as f:
        json.dump(model_results, f, indent=2)
    print("  ✓ Saved to model_results.json")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m src.run_distillation_batch [label|status|finetune|eval|results]")
        sys.exit(1)
    cmd = sys.argv[1]
    {"label": label, "status": status, "finetune": finetune, "eval": eval_cmd, "results": results}[cmd]()
