"""
OpenAI Batch API for classification evaluation.

Submits all eval requests as batch jobs (separate quota from real-time API).
50% cheaper, no rate limit issues, results typically in <1 hour.

Usage:
  python -m src.run_batch submit     # Submit batch jobs
  python -m src.run_batch status     # Check batch status
  python -m src.run_batch results    # Download results and compute metrics
"""

import json
import sys
import time
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


def build_system_prompt():
    cat_list = "\n".join(f"- {cat}: {desc}" for cat, desc in CATEGORY_DESCRIPTIONS.items())
    return f"""You are a support ticket classifier for OpenAI. Classify the ticket into exactly one category.

Categories:
{cat_list}

Respond with ONLY the category name, nothing else. For example: billing"""


def build_fewshot_examples(X_train):
    examples = []
    for cat in CATEGORIES:
        cat_tickets = X_train[X_train["category"] == cat]["text"].tolist()
        sorted_by_len = sorted(cat_tickets, key=len)
        selected = sorted_by_len[:2] if len(sorted_by_len) >= 2 else sorted_by_len
        for t in selected:
            examples.append({"text": t, "category": cat})
    return examples


def parse_prediction(text: str) -> str:
    pred = text.strip().lower().replace('"', '').replace("'", "").strip()
    if pred in CATEGORIES:
        return pred
    matched = [c for c in CATEGORIES if c in pred or pred in c]
    return matched[0] if matched else "unknown"


def build_batch_requests(eval_texts, system_prompt, method, fewshot_messages=None, model="gpt-4o-mini"):
    """Build JSONL batch request lines."""
    requests = []
    for i, text in enumerate(eval_texts):
        if fewshot_messages:
            messages = fewshot_messages + [{"role": "user", "content": text}]
        else:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text},
            ]

        request = {
            "custom_id": f"{method}-{i}",
            "method": "POST",
            "url": "/v1/chat/completions",
            "body": {
                "model": model,
                "messages": messages,
                "max_tokens": 20,
                "temperature": 0,
            },
        }
        requests.append(request)
    return requests


def submit():
    """Submit batch jobs for all methods."""
    X_train, X_test, y_train, y_test, le = load_data()
    print(f"Train: {len(X_train)}, Test: {len(X_test)}")
    print(f"Eval set: {len(X_test)} tickets (full test set)")

    system_prompt = build_system_prompt()
    eval_texts = X_test["text"].tolist()

    # Save test set metadata for results processing
    test_meta = {
        "categories": X_test["category"].tolist(),
        "labels": y_test.tolist(),
        "eval_size": len(X_test),
    }
    with open(BATCH_DIR / "test_meta.json", "w") as f:
        json.dump(test_meta, f)

    batch_ids = {}

    # --- Zero-shot batch ---
    print("\nBuilding zero-shot batch...")
    zero_requests = build_batch_requests(eval_texts, system_prompt, "zero_shot")
    zero_path = BATCH_DIR / "zero_shot_requests.jsonl"
    with open(zero_path, "w") as f:
        for req in zero_requests:
            f.write(json.dumps(req) + "\n")
    print(f"  Wrote {len(zero_requests)} requests to {zero_path}")

    zero_file = client.files.create(file=open(zero_path, "rb"), purpose="batch")
    zero_batch = client.batches.create(
        input_file_id=zero_file.id,
        endpoint="/v1/chat/completions",
        completion_window="24h",
        metadata={"method": "zero_shot"},
    )
    batch_ids["zero_shot"] = zero_batch.id
    print(f"  Submitted batch: {zero_batch.id}")

    # --- Few-shot batch ---
    print("\nBuilding few-shot batch...")
    examples = build_fewshot_examples(X_train)
    fewshot_messages = [{"role": "system", "content": system_prompt}]
    for ex in examples:
        fewshot_messages.append({"role": "user", "content": ex["text"]})
        fewshot_messages.append({"role": "assistant", "content": ex["category"]})
    print(f"  Few-shot prompt: {len(fewshot_messages)} messages ({len(examples)} examples)")

    few_requests = build_batch_requests(eval_texts, system_prompt, "few_shot", fewshot_messages)
    few_path = BATCH_DIR / "few_shot_requests.jsonl"
    with open(few_path, "w") as f:
        for req in few_requests:
            f.write(json.dumps(req) + "\n")
    print(f"  Wrote {len(few_requests)} requests to {few_path}")

    few_file = client.files.create(file=open(few_path, "rb"), purpose="batch")
    few_batch = client.batches.create(
        input_file_id=few_file.id,
        endpoint="/v1/chat/completions",
        completion_window="24h",
        metadata={"method": "few_shot"},
    )
    batch_ids["few_shot"] = few_batch.id
    print(f"  Submitted batch: {few_batch.id}")

    # --- Fine-tuned model batches (if jobs are done) ---
    ft_jobs = [
        ("ftjob-p0eCw0DrNZzthLN5XcvlZRua", "Standard FT", "finetuned"),
        ("ftjob-wEZ9QjqdCJvmbmrwjPLGknZk", "Distillation FT", "distilled"),
    ]
    for jid, name, result_key in ft_jobs:
        try:
            j = client.fine_tuning.jobs.retrieve(jid)
            print(f"\n{name}: status={j.status}, model={j.fine_tuned_model}")
            if j.status == "succeeded" and j.fine_tuned_model:
                print(f"  Building {name} batch with model {j.fine_tuned_model}...")
                ft_requests = build_batch_requests(
                    eval_texts, system_prompt, result_key, model=j.fine_tuned_model
                )
                ft_path = BATCH_DIR / f"{result_key}_requests.jsonl"
                with open(ft_path, "w") as f:
                    for req in ft_requests:
                        f.write(json.dumps(req) + "\n")

                ft_file = client.files.create(file=open(ft_path, "rb"), purpose="batch")
                ft_batch = client.batches.create(
                    input_file_id=ft_file.id,
                    endpoint="/v1/chat/completions",
                    completion_window="24h",
                    metadata={"method": result_key, "model_id": j.fine_tuned_model},
                )
                batch_ids[result_key] = ft_batch.id
                print(f"  Submitted batch: {ft_batch.id}")
            else:
                print(f"  Skipping — not ready yet")
        except Exception as e:
            print(f"  Error: {e}")

    # Save batch IDs for status/results commands
    with open(BATCH_DIR / "batch_ids.json", "w") as f:
        json.dump(batch_ids, f, indent=2)
    print(f"\n{'='*60}")
    print(f"Submitted {len(batch_ids)} batch jobs. IDs saved to batch/batch_ids.json")
    print(f"Check status: python -m src.run_batch status")
    print(f"Get results:  python -m src.run_batch results")


def status():
    """Check status of all submitted batches."""
    with open(BATCH_DIR / "batch_ids.json") as f:
        batch_ids = json.load(f)

    print(f"{'Method':<20} {'Status':<15} {'Completed':<12} {'Failed':<8} {'Total':<8}")
    print("-" * 65)
    all_done = True
    for method, bid in batch_ids.items():
        b = client.batches.retrieve(bid)
        completed = b.request_counts.completed if b.request_counts else 0
        failed = b.request_counts.failed if b.request_counts else 0
        total = b.request_counts.total if b.request_counts else 0
        print(f"{method:<20} {b.status:<15} {completed:<12} {failed:<8} {total:<8}")
        if b.status not in ("completed", "failed", "cancelled"):
            all_done = False

    if all_done:
        print("\nAll batches done! Run: python -m src.run_batch results")
    else:
        print("\nStill processing. Check again in a few minutes.")


def results():
    """Download batch results and compute metrics."""
    with open(BATCH_DIR / "batch_ids.json") as f:
        batch_ids = json.load(f)
    with open(BATCH_DIR / "test_meta.json") as f:
        test_meta = json.load(f)

    le = LabelEncoder()
    le.fit(CATEGORIES)
    y_true = test_meta["labels"]
    eval_size = test_meta["eval_size"]

    results_path = DATA_DIR / "model_results.json"
    with open(results_path) as f:
        model_results = json.load(f)

    method_names = {
        "zero_shot": "GPT-4o-mini Zero-Shot",
        "few_shot": "GPT-4o-mini Few-Shot",
        "finetuned": "GPT-4o-mini Standard FT",
        "distilled": "GPT-4o-mini Distillation FT",
    }

    for method, bid in batch_ids.items():
        print(f"\n{'='*60}")
        print(f"{method_names.get(method, method)}")
        print(f"{'='*60}")

        b = client.batches.retrieve(bid)
        if b.status != "completed":
            print(f"  Status: {b.status} — skipping")
            continue

        # Download output file
        output_path = BATCH_DIR / f"{method}_output.jsonl"
        if b.output_file_id:
            content = client.files.content(b.output_file_id)
            with open(output_path, "wb") as f:
                f.write(content.read())
            print(f"  Downloaded {output_path}")

        # Parse results — responses may be out of order, use custom_id to reorder
        predictions = ["unknown"] * eval_size
        with open(output_path) as f:
            for line in f:
                resp = json.loads(line)
                custom_id = resp["custom_id"]  # e.g. "zero_shot-42"
                idx = int(custom_id.split("-")[-1])

                if resp.get("error"):
                    predictions[idx] = "unknown"
                else:
                    content = resp["response"]["body"]["choices"][0]["message"]["content"]
                    predictions[idx] = parse_prediction(content)

        # Compute metrics
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

        print(f"  F1 macro:   {f1_macro:.4f}")
        print(f"  F1 weighted: {f1_weighted:.4f}")
        print(f"  Unknowns:   {unknown_count}/{eval_size}")
        print(f"  Per-class F1:")
        for cls, f1 in sorted(per_class_f1.items(), key=lambda x: x[1]):
            print(f"    {cls:<25} {f1:.4f}")

        # Save to model_results.json
        result_entry = {
            "method": method_names.get(method, method),
            "f1_macro": round(f1_macro, 4),
            "f1_weighted": round(f1_weighted, 4),
            "per_class_f1": per_class_f1,
            "unknown_count": unknown_count,
            "eval_size": eval_size,
        }
        # Preserve model_id if it was a fine-tuned model
        if b.metadata and b.metadata.get("model_id"):
            result_entry["model_id"] = b.metadata["model_id"]

        model_results[method] = result_entry
        with open(results_path, "w") as f:
            json.dump(model_results, f, indent=2)
        print(f"  ✓ Saved to model_results.json")

    # Summary
    print(f"\n{'='*60}")
    print("ALL RESULTS")
    print(f"{'='*60}")
    for key, r in model_results.items():
        if isinstance(r, dict) and "f1_macro" in r:
            unk_str = f" ({r.get('unknown_count', '?')} unknowns)" if r.get('unknown_count', 0) > 0 else ""
            print(f"  {r.get('method', key):40s} F1={r['f1_macro']:.4f}{unk_str}")
    print("\nDone! Results saved to model_results.json")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m src.run_batch [submit|status|results]")
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd == "submit":
        submit()
    elif cmd == "status":
        status()
    elif cmd == "results":
        results()
    else:
        print(f"Unknown command: {cmd}")
        print("Usage: python -m src.run_batch [submit|status|results]")
        sys.exit(1)
