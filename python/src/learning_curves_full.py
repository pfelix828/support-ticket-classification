"""
Generate real learning curves for all local methods.
Runs each method separately to avoid OOM on Apple Silicon.

Usage:
  python -m src.learning_curves_full           # Run all methods
  python -m src.learning_curves_full classical  # Just logreg, xgboost, emb_xgb
  python -m src.learning_curves_full bert       # Just BERT
"""

import gc
import json
import sys
import time
import numpy as np
import pandas as pd
from pathlib import Path

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score
from sklearn.preprocessing import LabelEncoder

DATA_DIR = Path(__file__).parent.parent.parent / "app" / "public" / "data"

CATEGORIES = [
    "account_access", "account_management", "api_errors", "api_usage",
    "billing", "chatgpt_apps", "chatgpt_product", "enterprise",
    "gpts", "newer_products", "privacy_policy", "security",
]

VOLUMES = [100, 500, 1000, 5000]


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


def run_classical_curves():
    """Learning curves for logreg, xgboost, emb_xgb."""
    import xgboost as xgb
    from sentence_transformers import SentenceTransformer

    X_train, X_test, y_train, y_test, le = load_data()
    volumes = [v for v in VOLUMES if v < len(X_train)] + [len(X_train)]

    # TF-IDF
    tfidf = TfidfVectorizer(max_features=10000, ngram_range=(1, 2), min_df=2, sublinear_tf=True)
    X_train_tfidf = tfidf.fit_transform(X_train["text"])
    X_test_tfidf = tfidf.transform(X_test["text"])

    # Embeddings
    print("Computing embeddings...")
    st_model = SentenceTransformer("all-MiniLM-L6-v2")
    train_emb = st_model.encode(X_train["text"].tolist(), show_progress_bar=True, batch_size=256)
    test_emb = st_model.encode(X_test["text"].tolist(), show_progress_bar=True, batch_size=256)
    del st_model
    gc.collect()

    tier_map = {"free": 0, "plus": 1, "go": 2, "pro": 3, "api_only": 4, "enterprise": 5}
    urgency_map = {"low": 0, "medium": 1, "high": 2}

    def build_meta(subset_df):
        return np.column_stack([
            subset_df["customer_tier"].map(tier_map).fillna(0).values,
            subset_df["account_age_days"].values,
            subset_df["previous_tickets"].values,
            subset_df["urgency"].map(urgency_map).fillna(1).values,
        ])

    test_meta = build_meta(X_test)
    X_test_emb = np.hstack([test_emb, test_meta])

    results = {"volumes": [], "logreg": [], "xgboost": [], "emb_xgb": []}

    for vol in volumes:
        print(f"\nVolume: {vol}")
        if vol < len(X_train):
            idx = X_train.sample(n=vol, random_state=42).index
            indexer = X_train.index.get_indexer(idx)
        else:
            idx = X_train.index
            indexer = slice(None)
        y_sub = y_train.loc[idx]

        # LogReg
        lr = LogisticRegression(max_iter=1000, C=1.0, solver="lbfgs", random_state=42)
        lr.fit(X_train_tfidf[indexer], y_sub)
        lr_f1 = f1_score(y_test, lr.predict(X_test_tfidf), average="macro")

        # XGBoost
        xgb_m = xgb.XGBClassifier(n_estimators=200, max_depth=6, learning_rate=0.1,
                                    random_state=42, n_jobs=-1, eval_metric="mlogloss")
        xgb_m.fit(X_train_tfidf[indexer], y_sub)
        xgb_f1 = f1_score(y_test, xgb_m.predict(X_test_tfidf), average="macro")

        # Emb+XGB
        sub_emb = train_emb[indexer]
        sub_meta = build_meta(X_train.loc[idx])
        X_sub_emb = np.hstack([sub_emb, sub_meta])
        emb_m = xgb.XGBClassifier(n_estimators=300, max_depth=6, learning_rate=0.1,
                                    random_state=42, n_jobs=-1, eval_metric="mlogloss")
        emb_m.fit(X_sub_emb, y_sub)
        emb_f1 = f1_score(y_test, emb_m.predict(X_test_emb), average="macro")

        print(f"  LR={lr_f1:.4f}  XGB={xgb_f1:.4f}  Emb={emb_f1:.4f}")
        results["volumes"].append(vol)
        results["logreg"].append(round(lr_f1, 4))
        results["xgboost"].append(round(xgb_f1, 4))
        results["emb_xgb"].append(round(emb_f1, 4))

    return results


def run_bert_curves():
    """Learning curves for BERT — one volume at a time to avoid OOM."""
    import torch
    from torch.utils.data import Dataset, DataLoader
    from transformers import BertTokenizer, BertForSequenceClassification, get_linear_schedule_with_warmup

    class TicketDataset(Dataset):
        def __init__(self, texts, labels, tokenizer, max_length=128):
            self.encodings = tokenizer(texts, truncation=True, padding="max_length",
                                        max_length=max_length, return_tensors="pt")
            self.labels = torch.tensor(labels, dtype=torch.long)
        def __len__(self):
            return len(self.labels)
        def __getitem__(self, idx):
            return {"input_ids": self.encodings["input_ids"][idx],
                    "attention_mask": self.encodings["attention_mask"][idx],
                    "labels": self.labels[idx]}

    X_train, X_test, y_train, y_test, le = load_data()
    volumes = [v for v in VOLUMES if v < len(X_train)] + [len(X_train)]

    device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
    print(f"BERT device: {device}")

    tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")

    # Pre-tokenize test set once
    test_texts = X_test["text"].tolist()
    test_labels = y_test.tolist()
    test_dataset = TicketDataset(test_texts, test_labels, tokenizer)
    test_loader = DataLoader(test_dataset, batch_size=64)

    results = {"volumes": [], "bert": []}

    for vol in volumes:
        print(f"\nBERT at volume {vol}...")
        t0 = time.time()

        # Subsample
        if vol < len(X_train):
            idx = X_train.sample(n=vol, random_state=42).index
        else:
            idx = X_train.index
        sub_texts = X_train.loc[idx, "text"].tolist()
        sub_labels = y_train.loc[idx].tolist()

        # Fresh model each time
        model = BertForSequenceClassification.from_pretrained(
            "bert-base-uncased", num_labels=len(CATEGORIES)
        )
        model.to(device)

        train_dataset = TicketDataset(sub_texts, sub_labels, tokenizer)
        train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)

        epochs = 3
        optimizer = torch.optim.AdamW(model.parameters(), lr=2e-5, weight_decay=0.01)
        total_steps = len(train_loader) * epochs
        scheduler = get_linear_schedule_with_warmup(
            optimizer, num_warmup_steps=int(total_steps * 0.1), num_training_steps=total_steps
        )

        model.train()
        for epoch in range(epochs):
            for step, batch in enumerate(train_loader):
                batch = {k: v.to(device) for k, v in batch.items()}
                outputs = model(**batch)
                loss = outputs.loss
                loss.backward()
                torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                optimizer.step()
                scheduler.step()
                optimizer.zero_grad()
            print(f"  Epoch {epoch+1}/3 done")

        model.eval()
        all_preds, all_labels = [], []
        with torch.no_grad():
            for batch in test_loader:
                batch_dev = {k: v.to(device) for k, v in batch.items()}
                outputs = model(**batch_dev)
                preds = torch.argmax(outputs.logits, dim=-1)
                all_preds.extend(preds.cpu().numpy())
                all_labels.extend(batch["labels"].numpy())

        bert_f1 = f1_score(all_labels, all_preds, average="macro")
        elapsed = time.time() - t0
        print(f"  BERT F1={bert_f1:.4f} ({elapsed:.0f}s)")

        results["volumes"].append(vol)
        results["bert"].append(round(bert_f1, 4))

        # Free memory
        del model, train_dataset, train_loader, optimizer, scheduler
        gc.collect()
        if torch.backends.mps.is_available():
            torch.mps.empty_cache()

    return results


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "all"

    # Load existing results
    results_path = DATA_DIR / "model_results.json"
    with open(results_path) as f:
        model_results = json.load(f)

    existing = model_results.get("learning_curves", {})

    if mode in ("all", "classical"):
        print("=" * 60)
        print("CLASSICAL METHODS (LogReg, XGBoost, Emb+XGB)")
        print("=" * 60)
        classical = run_classical_curves()
        existing["volumes"] = classical["volumes"]
        existing["logreg"] = classical["logreg"]
        existing["xgboost"] = classical["xgboost"]
        existing["emb_xgb"] = classical["emb_xgb"]

    if mode in ("all", "bert"):
        print("\n" + "=" * 60)
        print("BERT")
        print("=" * 60)
        bert = run_bert_curves()
        # Merge — volumes should match
        if "volumes" not in existing:
            existing["volumes"] = bert["volumes"]
        existing["bert"] = bert["bert"]

    model_results["learning_curves"] = existing
    with open(results_path, "w") as f:
        json.dump(model_results, f, indent=2)

    print(f"\n\nSaved to model_results.json")
    print("\nFinal learning curves:")
    vols = existing.get("volumes", [])
    for i, vol in enumerate(vols):
        parts = [f"vol={vol}"]
        for key in ["logreg", "xgboost", "emb_xgb", "bert"]:
            if key in existing and i < len(existing[key]):
                parts.append(f"{key}={existing[key][i]:.4f}")
        print(f"  {' | '.join(parts)}")


if __name__ == "__main__":
    main()
