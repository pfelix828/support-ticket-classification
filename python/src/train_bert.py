"""
Fine-tune bert-base-uncased for support ticket classification.

Uses MPS (Apple Silicon GPU) for training.
Evaluates on the same test set as all other models.
Saves results to model_results.json.
"""

import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import BertTokenizer, BertForSequenceClassification, get_linear_schedule_with_warmup
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import f1_score, classification_report

DATA_DIR = Path(__file__).parent.parent.parent / "app" / "public" / "data"

CATEGORIES = [
    "account_access", "account_management", "api_errors", "api_usage",
    "billing", "chatgpt_apps", "chatgpt_product", "enterprise",
    "gpts", "newer_products", "privacy_policy", "security",
]


class TicketDataset(Dataset):
    def __init__(self, texts, labels, tokenizer, max_length=128):
        self.encodings = tokenizer(
            texts, truncation=True, padding="max_length",
            max_length=max_length, return_tensors="pt"
        )
        self.labels = torch.tensor(labels, dtype=torch.long)

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        return {
            "input_ids": self.encodings["input_ids"][idx],
            "attention_mask": self.encodings["attention_mask"][idx],
            "labels": self.labels[idx],
        }


def main():
    # Load data — same split as all other models
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
    print(f"Train: {len(X_train)}, Test: {len(X_test)}")

    # Device
    if torch.backends.mps.is_available():
        device = torch.device("mps")
        print("Using MPS (Apple Silicon GPU)")
    elif torch.cuda.is_available():
        device = torch.device("cuda")
        print("Using CUDA")
    else:
        device = torch.device("cpu")
        print("Using CPU")

    # Tokenizer and model
    model_name = "bert-base-uncased"
    print(f"Loading {model_name}...")
    tokenizer = BertTokenizer.from_pretrained(model_name)
    model = BertForSequenceClassification.from_pretrained(
        model_name, num_labels=len(CATEGORIES)
    )
    model.to(device)

    # Datasets
    print("Tokenizing...")
    train_dataset = TicketDataset(
        X_train["text"].tolist(), y_train.tolist(), tokenizer
    )
    test_dataset = TicketDataset(
        X_test["text"].tolist(), y_test.tolist(), tokenizer
    )

    train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=64)

    # Training setup
    epochs = 3
    lr = 2e-5
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=0.01)
    total_steps = len(train_loader) * epochs
    scheduler = get_linear_schedule_with_warmup(
        optimizer, num_warmup_steps=int(total_steps * 0.1), num_training_steps=total_steps
    )

    # Train
    print(f"\nTraining for {epochs} epochs ({total_steps} steps)...")
    start_time = time.time()

    for epoch in range(epochs):
        model.train()
        total_loss = 0
        for step, batch in enumerate(train_loader):
            batch = {k: v.to(device) for k, v in batch.items()}
            outputs = model(**batch)
            loss = outputs.loss
            total_loss += loss.item()

            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            scheduler.step()
            optimizer.zero_grad()

            if (step + 1) % 50 == 0:
                print(f"  Epoch {epoch+1}/{epochs}, Step {step+1}/{len(train_loader)}, Loss: {loss.item():.4f}")

        avg_loss = total_loss / len(train_loader)
        print(f"  Epoch {epoch+1} avg loss: {avg_loss:.4f}")

    train_time = time.time() - start_time
    print(f"Training complete in {train_time:.1f}s")

    # Evaluate
    print("\nEvaluating on test set...")
    model.eval()
    all_preds = []
    all_labels = []

    with torch.no_grad():
        for batch in test_loader:
            batch_device = {k: v.to(device) for k, v in batch.items()}
            outputs = model(**batch_device)
            preds = torch.argmax(outputs.logits, dim=-1)
            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(batch["labels"].numpy())

    all_preds = np.array(all_preds)
    all_labels = np.array(all_labels)

    f1_macro = f1_score(all_labels, all_preds, average="macro")
    f1_weighted = f1_score(all_labels, all_preds, average="weighted")

    report = classification_report(
        all_labels, all_preds, target_names=le.classes_,
        output_dict=True, zero_division=0
    )
    per_class_f1 = {cls: round(report[cls]["f1-score"], 4) for cls in le.classes_}

    # Confusion pairs
    from collections import Counter
    confusion_counts = Counter()
    for true, pred in zip(all_labels, all_preds):
        if true != pred:
            confusion_counts[(le.classes_[true], le.classes_[pred])] += 1

    # Count per actual class
    actual_counts = Counter(all_labels)
    confusion_pairs = []
    for (actual, predicted), count in confusion_counts.most_common(10):
        actual_idx = le.transform([actual])[0]
        rate = round(count / actual_counts[actual_idx], 4)
        confusion_pairs.append({
            "actual": actual, "predicted": predicted,
            "count": count, "rate": rate,
        })

    print(f"\n{'='*60}")
    print(f"Fine-Tuned BERT Results")
    print(f"{'='*60}")
    print(f"  F1 macro:   {f1_macro:.4f}")
    print(f"  F1 weighted: {f1_weighted:.4f}")
    print(f"  Train time: {train_time:.1f}s")
    print(f"  Per-class F1:")
    for cls, f1 in sorted(per_class_f1.items(), key=lambda x: x[1]):
        print(f"    {cls:<25} {f1:.4f}")

    # Save to model_results.json
    results_path = DATA_DIR / "model_results.json"
    with open(results_path) as f:
        model_results = json.load(f)

    model_results["bert"] = {
        "method": "Fine-Tuned BERT",
        "f1_macro": round(f1_macro, 4),
        "f1_weighted": round(f1_weighted, 4),
        "train_time_s": round(train_time, 1),
        "per_class_f1": per_class_f1,
        "confusion_pairs": confusion_pairs,
        "eval_size": len(X_test),
    }

    with open(results_path, "w") as f:
        json.dump(model_results, f, indent=2)
    print(f"\n  ✓ Saved to model_results.json")


if __name__ == "__main__":
    main()
