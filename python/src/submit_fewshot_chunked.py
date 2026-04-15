"""
Submit few-shot batch in chunks to stay under OpenAI's 2M enqueued token limit.

Few-shot requests are ~2750 tokens each. With 2M limit and needing buffer for
other batches, we use ~700 requests per chunk.

Usage:
  python -m src.submit_fewshot_chunked submit   # Submit chunks (waits for queue space)
  python -m src.submit_fewshot_chunked results   # Merge chunk results into model_results.json
"""

import json
import sys
import time
from pathlib import Path
from dotenv import load_dotenv

from openai import OpenAI
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import f1_score, classification_report

load_dotenv(Path(__file__).parent.parent / ".env")
client = OpenAI()

DATA_DIR = Path(__file__).parent.parent.parent / "app" / "public" / "data"
BATCH_DIR = Path(__file__).parent.parent / "batch"

CATEGORIES = [
    "account_access", "account_management", "api_errors", "api_usage",
    "billing", "chatgpt_apps", "chatgpt_product", "enterprise",
    "gpts", "newer_products", "privacy_policy", "security",
]

CHUNK_SIZE = 600  # ~600 requests × ~2750 tokens ≈ 1.65M tokens per chunk


def wait_for_queue_space():
    """Wait until no other batches are in_progress/validating."""
    while True:
        with open(BATCH_DIR / "batch_ids.json") as f:
            batch_ids = json.load(f)
        active = 0
        for method, bid in batch_ids.items():
            if method == "few_shot":
                continue
            b = client.batches.retrieve(bid)
            if b.status in ("validating", "in_progress"):
                active += 1
        if active == 0:
            return
        print(f"  {active} batch(es) still processing, waiting 60s...")
        time.sleep(60)


def submit():
    """Submit few-shot in chunks."""
    # Read the full few-shot requests file
    few_path = BATCH_DIR / "few_shot_requests.jsonl"
    if not few_path.exists():
        print("Error: few_shot_requests.jsonl not found. Run 'python -m src.run_batch submit' first.")
        sys.exit(1)

    with open(few_path) as f:
        all_requests = [json.loads(line) for line in f]

    total = len(all_requests)
    num_chunks = (total + CHUNK_SIZE - 1) // CHUNK_SIZE
    print(f"Splitting {total} few-shot requests into {num_chunks} chunks of ~{CHUNK_SIZE}")

    chunk_ids = []

    for i in range(num_chunks):
        start = i * CHUNK_SIZE
        end = min(start + CHUNK_SIZE, total)
        chunk = all_requests[start:end]

        print(f"\nChunk {i+1}/{num_chunks} ({len(chunk)} requests, indices {start}-{end-1})")

        # Wait for queue space
        print("  Checking queue space...")
        wait_for_queue_space()

        # Also wait for prior chunks to clear
        for prior_bid in chunk_ids:
            while True:
                b = client.batches.retrieve(prior_bid)
                if b.status in ("completed", "failed", "cancelled"):
                    break
                print(f"  Waiting for prior chunk {prior_bid[:20]}... ({b.status})")
                time.sleep(60)

        # Write chunk file
        chunk_path = BATCH_DIR / f"few_shot_chunk_{i}.jsonl"
        with open(chunk_path, "w") as f:
            for req in chunk:
                f.write(json.dumps(req) + "\n")

        # Submit
        chunk_file = client.files.create(file=open(chunk_path, "rb"), purpose="batch")
        chunk_batch = client.batches.create(
            input_file_id=chunk_file.id,
            endpoint="/v1/chat/completions",
            completion_window="24h",
            metadata={"method": f"few_shot_chunk_{i}"},
        )
        chunk_ids.append(chunk_batch.id)
        print(f"  Submitted: {chunk_batch.id}")

    # Save chunk IDs
    with open(BATCH_DIR / "few_shot_chunk_ids.json", "w") as f:
        json.dump(chunk_ids, f, indent=2)
    print(f"\nSubmitted {len(chunk_ids)} chunks. IDs saved to batch/few_shot_chunk_ids.json")
    print("Run: python -m src.submit_fewshot_chunked results")


def results():
    """Download chunk results and merge into model_results.json."""
    with open(BATCH_DIR / "few_shot_chunk_ids.json") as f:
        chunk_ids = json.load(f)
    with open(BATCH_DIR / "test_meta.json") as f:
        test_meta = json.load(f)

    le = LabelEncoder()
    le.fit(CATEGORIES)
    y_true = test_meta["labels"]
    eval_size = test_meta["eval_size"]

    from src.run_batch import parse_prediction

    # Collect all predictions across chunks
    predictions = ["unknown"] * eval_size

    for i, bid in enumerate(chunk_ids):
        b = client.batches.retrieve(bid)
        print(f"Chunk {i}: status={b.status}")
        if b.status != "completed":
            print(f"  Not completed — cannot merge results yet")
            return

        # Download
        output_path = BATCH_DIR / f"few_shot_chunk_{i}_output.jsonl"
        if b.output_file_id:
            content = client.files.content(b.output_file_id)
            with open(output_path, "wb") as f:
                f.write(content.read())

        with open(output_path) as f:
            for line in f:
                resp = json.loads(line)
                idx = int(resp["custom_id"].split("-")[-1])
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

    print(f"\nGPT-4o-mini Few-Shot (merged from {len(chunk_ids)} chunks)")
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

    model_results["few_shot"] = {
        "method": "GPT-4o-mini Few-Shot",
        "f1_macro": round(f1_macro, 4),
        "f1_weighted": round(f1_weighted, 4),
        "per_class_f1": per_class_f1,
        "unknown_count": unknown_count,
        "eval_size": eval_size,
    }
    with open(results_path, "w") as f:
        json.dump(model_results, f, indent=2)
    print("  ✓ Saved to model_results.json")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m src.submit_fewshot_chunked [submit|results]")
        sys.exit(1)
    cmd = sys.argv[1]
    if cmd == "submit":
        submit()
    elif cmd == "results":
        results()
    else:
        print(f"Unknown: {cmd}")
