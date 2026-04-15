"""
OpenAI API classification with token-aware rate limiting.

Rate limits (Tier 1 gpt-4o-mini):
  - 10,000 RPD (requests per day) — not a concern for ~5-10K evals
  - 200,000 TPM (tokens per minute) — this is the real throttle

Strategy: estimate tokens per request, calculate max concurrent requests
to stay at ~80% of TPM budget, use Retry-After header when available.
"""

import json
import os
import asyncio
import time
from pathlib import Path
from dotenv import load_dotenv

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import f1_score, classification_report
from openai import AsyncOpenAI, RateLimitError

load_dotenv(Path(__file__).parent.parent / ".env")
aclient = AsyncOpenAI()

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

TPM_LIMIT = 200_000
TPM_TARGET = int(TPM_LIMIT * 0.80)  # Stay at 80% to avoid hitting the wall


def estimate_tokens(messages):
    """Rough token estimate: ~4 chars per token for English text."""
    total_chars = sum(len(m["content"]) for m in messages)
    return total_chars // 4 + 20  # +20 for response tokens


def optimal_concurrency(messages_sample, target_tpm=TPM_TARGET):
    """Calculate concurrency to stay under TPM, assuming ~1s per request."""
    tokens_per_request = estimate_tokens(messages_sample)
    # Requests we can do per minute at target TPM
    rpm = target_tpm // tokens_per_request
    # Each request takes ~1-2s, so in-flight at any time ≈ rpm / 30
    concurrency = max(2, min(rpm // 30, 50))
    return concurrency, tokens_per_request


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


async def classify_one(semaphore, messages, model="gpt-4o-mini", retries=5):
    async with semaphore:
        for attempt in range(retries):
            try:
                response = await aclient.chat.completions.create(
                    model=model,
                    messages=messages,
                    max_tokens=20,
                    temperature=0,
                )
                return parse_prediction(response.choices[0].message.content)
            except RateLimitError as e:
                # Parse Retry-After if available, otherwise exponential backoff
                retry_after = None
                if hasattr(e, 'response') and e.response is not None:
                    retry_after = e.response.headers.get('retry-after')
                if retry_after:
                    wait = min(float(retry_after), 60)
                else:
                    wait = min(2 ** attempt + 1, 30)
                if attempt < retries - 1:
                    print(f"  ⚠ Retry {attempt+1}/{retries}: 429 — waiting {wait:.0f}s", flush=True)
                    await asyncio.sleep(wait)
                else:
                    print(f"  ✗ Failed after {retries} retries: 429", flush=True)
                    return "unknown"
            except Exception as e:
                wait = min(2 ** attempt + 1, 30)
                if attempt < retries - 1:
                    print(f"  ⚠ Retry {attempt+1}/{retries}: {type(e).__name__} — waiting {wait}s", flush=True)
                    await asyncio.sleep(wait)
                else:
                    print(f"  ✗ Failed after {retries} retries: {type(e).__name__}", flush=True)
                    return "unknown"


async def classify_batch(texts, system_prompt, fewshot_messages=None, model="gpt-4o-mini", concurrency=None):
    # Build all message lists first
    all_messages = []
    for text in texts:
        if fewshot_messages:
            messages = fewshot_messages + [{"role": "user", "content": text}]
        else:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text},
            ]
        all_messages.append(messages)

    # Auto-calculate concurrency from token estimates if not specified
    if concurrency is None:
        concurrency, est_tokens = optimal_concurrency(all_messages[0])
        print(f"  Auto concurrency: {concurrency} (~{est_tokens} tokens/req, targeting {TPM_TARGET:,} TPM)", flush=True)
    else:
        est_tokens = estimate_tokens(all_messages[0])
        print(f"  Concurrency: {concurrency} (~{est_tokens} tokens/req)", flush=True)

    semaphore = asyncio.Semaphore(concurrency)
    tasks = [classify_one(semaphore, msgs, model) for msgs in all_messages]

    results = []
    chunk_size = 100
    for i in range(0, len(tasks), chunk_size):
        chunk = tasks[i:i + chunk_size]
        chunk_results = await asyncio.gather(*chunk)
        results.extend(chunk_results)
        unknowns = sum(1 for r in results if r == "unknown")
        done = min(i + chunk_size, len(tasks))
        pct_unknown = unknowns / done * 100
        elapsed = time.time() - _batch_start
        rate = done / elapsed * 60 if elapsed > 0 else 0
        eta = (len(tasks) - done) / (done / elapsed) if done > 0 and elapsed > 0 else 0
        print(f"  {done}/{len(tasks)} done | {unknowns} unknowns ({pct_unknown:.1f}%) | {rate:.0f} req/min | ETA {eta:.0f}s", flush=True)
        if pct_unknown > 20 and done >= 200:
            print(f"  ⚠️  ABORT: unknown rate {pct_unknown:.1f}% > 20% — likely rate limited", flush=True)
            return results

    return results

# Global timer for ETA calculation within classify_batch
_batch_start = time.time()


def compute_metrics(predictions, y_test, le, all_categories):
    y_test_arr = y_test.values
    y_pred_encoded = []
    valid_mask = []
    for pred in predictions:
        if pred in all_categories:
            y_pred_encoded.append(le.transform([pred])[0])
            valid_mask.append(True)
        else:
            y_pred_encoded.append(-1)
            valid_mask.append(False)

    valid_preds = [y_pred_encoded[i] for i in range(len(valid_mask)) if valid_mask[i]]
    valid_true = [y_test_arr[i] for i in range(len(valid_mask)) if valid_mask[i]]

    labels = list(range(len(all_categories)))
    f1_macro = f1_score(valid_true, valid_preds, average="macro", labels=labels, zero_division=0)
    f1_weighted = f1_score(valid_true, valid_preds, average="weighted", labels=labels, zero_division=0)

    report = classification_report(valid_true, valid_preds, target_names=le.classes_,
                                   labels=labels, output_dict=True, zero_division=0)
    per_class_f1 = {cls: round(report.get(cls, {}).get("f1-score", 0), 4) for cls in le.classes_}

    unknown_count = sum(1 for v in valid_mask if not v)
    return f1_macro, f1_weighted, per_class_f1, unknown_count


async def run_all():
    global _batch_start

    X_train, X_test, y_train, y_test, le = load_data()
    print(f"Train: {len(X_train)}, Test: {len(X_test)}")

    X_eval, y_eval = X_test, y_test
    print(f"Eval set: {len(X_eval)} tickets (full test set, ~±1.5% margin)")

    system_prompt = build_system_prompt()
    eval_texts = X_eval["text"].tolist()

    results_path = DATA_DIR / "model_results.json"
    with open(results_path) as f:
        results = json.load(f)

    # --- Zero-shot ---
    print("\n" + "=" * 60)
    print(f"GPT-4o-mini Zero-Shot — {len(eval_texts)} tickets")
    print("=" * 60)
    _batch_start = time.time()
    zero_preds = await classify_batch(eval_texts, system_prompt)
    zero_time = time.time() - _batch_start
    f1m, f1w, pcf1, unk = compute_metrics(zero_preds, y_eval, le, CATEGORIES)
    print(f"  F1 macro: {f1m:.4f}")
    print(f"  F1 weighted: {f1w:.4f}")
    print(f"  Unknowns: {unk}/{len(eval_texts)}")
    print(f"  Time: {zero_time:.1f}s")

    results["zero_shot"] = {
        "method": "GPT-4o-mini Zero-Shot",
        "f1_macro": round(f1m, 4),
        "f1_weighted": round(f1w, 4),
        "per_class_f1": pcf1,
        "unknown_count": unk,
        "eval_size": len(eval_texts),
    }
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)
    print("  ✓ Zero-shot results saved")

    # --- Few-shot ---
    print("\n" + "=" * 60)
    print(f"GPT-4o-mini Few-Shot — {len(eval_texts)} tickets")
    print("=" * 60)
    examples = build_fewshot_examples(X_train)
    fewshot_messages = [{"role": "system", "content": system_prompt}]
    for ex in examples:
        fewshot_messages.append({"role": "user", "content": ex["text"]})
        fewshot_messages.append({"role": "assistant", "content": ex["category"]})
    print(f"  Few-shot prompt: {len(fewshot_messages)} messages ({len(examples)} examples)")

    _batch_start = time.time()
    few_preds = await classify_batch(eval_texts, system_prompt, fewshot_messages)
    few_time = time.time() - _batch_start
    f1m, f1w, pcf1, unk = compute_metrics(few_preds, y_eval, le, CATEGORIES)
    print(f"  F1 macro: {f1m:.4f}")
    print(f"  F1 weighted: {f1w:.4f}")
    print(f"  Unknowns: {unk}/{len(eval_texts)}")
    print(f"  Time: {few_time:.1f}s")

    results["few_shot"] = {
        "method": "GPT-4o-mini Few-Shot",
        "f1_macro": round(f1m, 4),
        "f1_weighted": round(f1w, 4),
        "per_class_f1": pcf1,
        "unknown_count": unk,
        "eval_size": len(eval_texts),
    }
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)
    print("  ✓ Few-shot results saved")

    # --- Check fine-tuning jobs and evaluate if ready ---
    print("\n" + "=" * 60)
    print("FINE-TUNING JOB STATUS")
    print("=" * 60)
    from openai import OpenAI
    sync_client = OpenAI()
    ft_jobs = [
        ("ftjob-p0eCw0DrNZzthLN5XcvlZRua", "Standard FT", "finetuned"),
        ("ftjob-wEZ9QjqdCJvmbmrwjPLGknZk", "Distillation FT", "distilled"),
    ]
    for jid, name, result_key in ft_jobs:
        try:
            j = sync_client.fine_tuning.jobs.retrieve(jid)
            print(f"  {name}: status={j.status}, model={j.fine_tuned_model}")
            if j.status == "succeeded" and j.fine_tuned_model:
                print(f"    → Evaluating {j.fine_tuned_model} on {len(eval_texts)} tickets...")
                _batch_start = time.time()
                ft_preds = await classify_batch(eval_texts, system_prompt, model=j.fine_tuned_model)
                ft_time = time.time() - _batch_start
                f1m, f1w, pcf1, unk = compute_metrics(ft_preds, y_eval, le, CATEGORIES)
                print(f"    F1 macro: {f1m:.4f}")
                print(f"    F1 weighted: {f1w:.4f}")
                print(f"    Unknowns: {unk}/{len(eval_texts)}")
                print(f"    Time: {ft_time:.1f}s")

                results[result_key] = {
                    "method": f"GPT-4o-mini {name}",
                    "f1_macro": round(f1m, 4),
                    "f1_weighted": round(f1w, 4),
                    "per_class_f1": pcf1,
                    "unknown_count": unk,
                    "eval_size": len(eval_texts),
                    "model_id": j.fine_tuned_model,
                }
                with open(results_path, "w") as f:
                    json.dump(results, f, indent=2)
                print(f"    ✓ {name} results saved")
            elif j.status == "failed":
                print(f"    ✗ Job failed: {j.error}")
        except Exception as e:
            print(f"  {name}: error — {e}")

    # --- Summary ---
    print("\n" + "=" * 60)
    print("ALL RESULTS")
    print("=" * 60)
    for key, r in results.items():
        if isinstance(r, dict) and "f1_macro" in r:
            unk_str = f" ({r.get('unknown_count', '?')} unknowns)" if r.get('unknown_count', 0) > 0 else ""
            print(f"  {r.get('method', key):40s} F1={r['f1_macro']:.4f}{unk_str}")
    print("\nDone! Results saved to model_results.json")


def main():
    asyncio.run(run_all())


if __name__ == "__main__":
    main()
