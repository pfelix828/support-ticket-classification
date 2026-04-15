"""
Training and evaluation pipeline for support ticket classification.

Runs all local models (TF-IDF, XGBoost, Embeddings+XGBoost, BERT),
exports results to JSON for the frontend app.
"""

import json
import time
import numpy as np
import pandas as pd
from pathlib import Path
from collections import Counter

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    classification_report,
    f1_score,
    confusion_matrix,
)
from sklearn.preprocessing import LabelEncoder

# ---------------------------------------------------------------------------
# 1. Load & Deduplicate
# ---------------------------------------------------------------------------

DATA_DIR = Path(__file__).parent.parent.parent / "app" / "public" / "data"
OUTPUT_DIR = DATA_DIR


def load_and_prepare():
    """Load tickets, deduplicate, and split."""
    print("Loading data...")
    with open(DATA_DIR / "tickets.json") as f:
        tickets = json.load(f)

    df = pd.DataFrame(tickets)
    print(f"  Total tickets: {len(df):,}")
    print(f"  Unique texts: {df['text'].nunique():,}")

    # Deduplicate — keep first occurrence
    df_dedup = df.drop_duplicates(subset="text", keep="first").copy()
    print(f"  After dedup: {len(df_dedup):,}")

    # Encode labels
    le = LabelEncoder()
    df_dedup["label"] = le.fit_transform(df_dedup["category"])

    # Stratified split
    X_train, X_test, y_train, y_test = train_test_split(
        df_dedup,
        df_dedup["label"],
        test_size=0.2,
        random_state=42,
        stratify=df_dedup["label"],
    )

    print(f"  Train: {len(X_train):,}  Test: {len(X_test):,}")
    print(f"  Categories: {list(le.classes_)}")

    return X_train, X_test, y_train, y_test, le


# ---------------------------------------------------------------------------
# 2. TF-IDF + Logistic Regression
# ---------------------------------------------------------------------------


def run_tfidf_logreg(X_train, X_test, y_train, y_test, le):
    """TF-IDF + Logistic Regression baseline."""
    print("\n" + "=" * 60)
    print("TF-IDF + Logistic Regression")
    print("=" * 60)

    # Vectorize
    tfidf = TfidfVectorizer(
        max_features=10000,
        ngram_range=(1, 2),
        min_df=2,
        sublinear_tf=True,
    )
    X_train_tfidf = tfidf.fit_transform(X_train["text"])
    X_test_tfidf = tfidf.transform(X_test["text"])

    # Train
    t0 = time.time()
    model = LogisticRegression(
        max_iter=1000,
        C=1.0,
        solver="lbfgs",

        random_state=42,
        n_jobs=-1,
    )
    model.fit(X_train_tfidf, y_train)
    train_time = time.time() - t0
    print(f"  Training time: {train_time:.1f}s")

    # Predict + time
    t0 = time.time()
    y_pred = model.predict(X_test_tfidf)
    predict_time = time.time() - t0
    latency_ms = (predict_time / len(X_test)) * 1000

    # Metrics
    f1_macro = f1_score(y_test, y_pred, average="macro")
    f1_weighted = f1_score(y_test, y_pred, average="weighted")
    report = classification_report(y_test, y_pred, target_names=le.classes_, output_dict=True)

    print(f"  F1 macro: {f1_macro:.4f}")
    print(f"  F1 weighted: {f1_weighted:.4f}")
    print(f"  Latency: {latency_ms:.3f}ms per ticket")

    # Top features per class
    feature_names = tfidf.get_feature_names_out()
    top_features = {}
    for i, cls in enumerate(le.classes_):
        coefs = model.coef_[i]
        top_idx = np.argsort(coefs)[-5:][::-1]
        top_features[cls] = [
            {"feature": feature_names[j], "weight": round(float(coefs[j]), 3)}
            for j in top_idx
        ]

    # Per-class F1
    per_class_f1 = {}
    for cls in le.classes_:
        per_class_f1[cls] = round(report[cls]["f1-score"], 4)

    # Confusion matrix
    cm = confusion_matrix(y_test, y_pred)
    cm_data = []
    for i, actual in enumerate(le.classes_):
        for j, predicted in enumerate(le.classes_):
            if i != j and cm[i][j] > 0:
                cm_data.append({
                    "actual": actual,
                    "predicted": predicted,
                    "count": int(cm[i][j]),
                    "rate": round(cm[i][j] / cm[i].sum(), 4),
                })

    return {
        "method": "TF-IDF + Logistic Regression",
        "f1_macro": round(f1_macro, 4),
        "f1_weighted": round(f1_weighted, 4),
        "latency_ms": round(latency_ms, 3),
        "train_time_s": round(train_time, 1),
        "per_class_f1": per_class_f1,
        "top_features": top_features,
        "confusion_pairs": sorted(cm_data, key=lambda x: x["rate"], reverse=True)[:10],
    }


# ---------------------------------------------------------------------------
# 3. TF-IDF + XGBoost
# ---------------------------------------------------------------------------


def run_tfidf_xgboost(X_train, X_test, y_train, y_test, le):
    """TF-IDF + XGBoost."""
    print("\n" + "=" * 60)
    print("TF-IDF + XGBoost")
    print("=" * 60)

    import xgboost as xgb

    tfidf = TfidfVectorizer(
        max_features=10000,
        ngram_range=(1, 2),
        min_df=2,
        sublinear_tf=True,
    )
    X_train_tfidf = tfidf.fit_transform(X_train["text"])
    X_test_tfidf = tfidf.transform(X_test["text"])

    t0 = time.time()
    model = xgb.XGBClassifier(
        n_estimators=200,
        max_depth=6,
        learning_rate=0.1,
        random_state=42,
        n_jobs=-1,
        eval_metric="mlogloss",
    )
    model.fit(X_train_tfidf, y_train)
    train_time = time.time() - t0
    print(f"  Training time: {train_time:.1f}s")

    t0 = time.time()
    y_pred = model.predict(X_test_tfidf)
    predict_time = time.time() - t0
    latency_ms = (predict_time / len(X_test)) * 1000

    f1_macro = f1_score(y_test, y_pred, average="macro")
    f1_weighted = f1_score(y_test, y_pred, average="weighted")
    report = classification_report(y_test, y_pred, target_names=le.classes_, output_dict=True)

    print(f"  F1 macro: {f1_macro:.4f}")
    print(f"  F1 weighted: {f1_weighted:.4f}")
    print(f"  Latency: {latency_ms:.3f}ms per ticket")

    per_class_f1 = {}
    for cls in le.classes_:
        per_class_f1[cls] = round(report[cls]["f1-score"], 4)

    # Feature importance (top overall)
    feature_names = tfidf.get_feature_names_out()
    importances = model.feature_importances_
    top_idx = np.argsort(importances)[-20:][::-1]
    top_features_overall = [
        {"feature": feature_names[j], "importance": round(float(importances[j]), 4)}
        for j in top_idx
    ]

    cm = confusion_matrix(y_test, y_pred)
    cm_data = []
    for i, actual in enumerate(le.classes_):
        for j, predicted in enumerate(le.classes_):
            if i != j and cm[i][j] > 0:
                cm_data.append({
                    "actual": actual,
                    "predicted": predicted,
                    "count": int(cm[i][j]),
                    "rate": round(cm[i][j] / cm[i].sum(), 4),
                })

    return {
        "method": "TF-IDF + XGBoost",
        "f1_macro": round(f1_macro, 4),
        "f1_weighted": round(f1_weighted, 4),
        "latency_ms": round(latency_ms, 3),
        "train_time_s": round(train_time, 1),
        "per_class_f1": per_class_f1,
        "top_features": top_features_overall,
        "confusion_pairs": sorted(cm_data, key=lambda x: x["rate"], reverse=True)[:10],
    }


# ---------------------------------------------------------------------------
# 4. Embeddings + XGBoost (with metadata)
# ---------------------------------------------------------------------------


def run_embeddings_xgboost(X_train, X_test, y_train, y_test, le):
    """Sentence embeddings + metadata features + XGBoost."""
    print("\n" + "=" * 60)
    print("Embeddings + XGBoost (with metadata)")
    print("=" * 60)

    import xgboost as xgb
    from sentence_transformers import SentenceTransformer

    # Encode text
    print("  Loading sentence transformer...")
    st_model = SentenceTransformer("all-MiniLM-L6-v2")

    print("  Encoding training texts...")
    t0 = time.time()
    train_embeddings = st_model.encode(
        X_train["text"].tolist(), show_progress_bar=True, batch_size=256
    )
    print(f"  Encoding time (train): {time.time() - t0:.1f}s")

    print("  Encoding test texts...")
    t0 = time.time()
    test_embeddings = st_model.encode(
        X_test["text"].tolist(), show_progress_bar=True, batch_size=256
    )
    embed_time_test = time.time() - t0
    print(f"  Encoding time (test): {embed_time_test:.1f}s")

    # Metadata features
    tier_map = {"free": 0, "plus": 1, "go": 2, "pro": 3, "api_only": 4, "enterprise": 5}
    urgency_map = {"low": 0, "medium": 1, "high": 2}

    def build_metadata(df):
        return np.column_stack([
            df["customer_tier"].map(tier_map).fillna(0).values,
            df["account_age_days"].values,
            df["previous_tickets"].values,
            df["urgency"].map(urgency_map).fillna(1).values,
        ])

    train_meta = build_metadata(X_train)
    test_meta = build_metadata(X_test)

    # Combine embeddings + metadata
    X_train_combined = np.hstack([train_embeddings, train_meta])
    X_test_combined = np.hstack([test_embeddings, test_meta])

    print(f"  Feature dims: {X_train_combined.shape[1]} (384 embedding + {train_meta.shape[1]} metadata)")

    # Train XGBoost
    t0 = time.time()
    model = xgb.XGBClassifier(
        n_estimators=300,
        max_depth=6,
        learning_rate=0.1,
        random_state=42,
        n_jobs=-1,
        eval_metric="mlogloss",
    )
    model.fit(X_train_combined, y_train)
    train_time = time.time() - t0
    print(f"  XGBoost training time: {train_time:.1f}s")

    # Predict
    t0 = time.time()
    y_pred = model.predict(X_test_combined)
    predict_time = time.time() - t0
    # Total latency includes embedding time
    latency_ms = ((embed_time_test + predict_time) / len(X_test)) * 1000

    f1_macro = f1_score(y_test, y_pred, average="macro")
    f1_weighted = f1_score(y_test, y_pred, average="weighted")
    report = classification_report(y_test, y_pred, target_names=le.classes_, output_dict=True)

    print(f"  F1 macro: {f1_macro:.4f}")
    print(f"  F1 weighted: {f1_weighted:.4f}")
    print(f"  Latency: {latency_ms:.3f}ms per ticket")

    per_class_f1 = {}
    for cls in le.classes_:
        per_class_f1[cls] = round(report[cls]["f1-score"], 4)

    # Feature importance — embedding dims vs metadata
    importances = model.feature_importances_
    embedding_importance = float(importances[:384].sum())
    metadata_names = ["customer_tier", "account_age_days", "previous_tickets", "urgency"]
    metadata_importance = {
        name: round(float(importances[384 + i]), 4)
        for i, name in enumerate(metadata_names)
    }
    total_importance = embedding_importance + sum(metadata_importance.values())

    feature_importance = {
        "embedding_pct": round(embedding_importance / total_importance * 100, 1),
        "metadata": {
            name: round(val / total_importance * 100, 1)
            for name, val in metadata_importance.items()
        },
    }

    # Confusion matrix
    cm = confusion_matrix(y_test, y_pred)
    cm_data = []
    for i, actual in enumerate(le.classes_):
        for j, predicted in enumerate(le.classes_):
            if i != j and cm[i][j] > 0:
                cm_data.append({
                    "actual": actual,
                    "predicted": predicted,
                    "count": int(cm[i][j]),
                    "rate": round(cm[i][j] / cm[i].sum(), 4),
                })

    # Performance on ambiguous tickets specifically
    ambiguous_mask = X_test["is_ambiguous"].values
    if ambiguous_mask.sum() > 0:
        f1_ambiguous = f1_score(
            y_test.values[ambiguous_mask],
            y_pred[ambiguous_mask],
            average="macro",
        )
    else:
        f1_ambiguous = None

    return {
        "method": "Embeddings + XGBoost",
        "f1_macro": round(f1_macro, 4),
        "f1_weighted": round(f1_weighted, 4),
        "f1_ambiguous": round(f1_ambiguous, 4) if f1_ambiguous else None,
        "latency_ms": round(latency_ms, 3),
        "train_time_s": round(train_time, 1),
        "per_class_f1": per_class_f1,
        "feature_importance": feature_importance,
        "confusion_pairs": sorted(cm_data, key=lambda x: x["rate"], reverse=True)[:10],
    }


# ---------------------------------------------------------------------------
# 5. Learning Curves (train on subsets)
# ---------------------------------------------------------------------------


def run_learning_curves(X_train, X_test, y_train, y_test, le):
    """Train TF-IDF+LogReg and TF-IDF+XGBoost on increasing subsets."""
    print("\n" + "=" * 60)
    print("Learning Curves")
    print("=" * 60)

    import xgboost as xgb

    volumes = [100, 500, 1000, 5000, 10000]
    # Add larger volumes if we have enough data
    if len(X_train) >= 20000:
        volumes.append(20000)
    if len(X_train) >= 50000:
        volumes.append(50000)
    volumes.append(len(X_train))  # full training set

    tfidf = TfidfVectorizer(
        max_features=10000, ngram_range=(1, 2), min_df=2, sublinear_tf=True
    )
    X_train_tfidf_full = tfidf.fit_transform(X_train["text"])
    X_test_tfidf = tfidf.transform(X_test["text"])

    curves = {"volumes": [], "logreg": [], "xgboost": []}

    for vol in volumes:
        if vol > len(X_train):
            continue

        # Subsample
        if vol < len(X_train):
            idx = X_train.sample(n=vol, random_state=42).index
            X_sub = X_train_tfidf_full[X_train.index.get_indexer(idx)]
            y_sub = y_train.loc[idx]
        else:
            X_sub = X_train_tfidf_full
            y_sub = y_train

        # LogReg
        lr = LogisticRegression(max_iter=1000, C=1.0, solver="lbfgs",
                                random_state=42)
        lr.fit(X_sub, y_sub)
        lr_f1 = f1_score(y_test, lr.predict(X_test_tfidf), average="macro")

        # XGBoost
        xgb_model = xgb.XGBClassifier(
            n_estimators=200, max_depth=6, learning_rate=0.1,
            random_state=42, n_jobs=-1, eval_metric="mlogloss"
        )
        xgb_model.fit(X_sub, y_sub)
        xgb_f1 = f1_score(y_test, xgb_model.predict(X_test_tfidf), average="macro")

        curves["volumes"].append(vol)
        curves["logreg"].append(round(lr_f1, 4))
        curves["xgboost"].append(round(xgb_f1, 4))

        print(f"  Volume {vol:>6,}: LogReg={lr_f1:.4f}  XGBoost={xgb_f1:.4f}")

    return curves


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    X_train, X_test, y_train, y_test, le = load_and_prepare()

    results = {}

    # TF-IDF + LogReg (always available)
    results["logreg"] = run_tfidf_logreg(X_train, X_test, y_train, y_test, le)

    # TF-IDF + XGBoost
    try:
        results["xgboost"] = run_tfidf_xgboost(X_train, X_test, y_train, y_test, le)
    except ImportError:
        print("\n  [SKIP] xgboost not installed")

    # Embeddings + XGBoost
    try:
        results["emb_xgboost"] = run_embeddings_xgboost(X_train, X_test, y_train, y_test, le)
    except ImportError as e:
        print(f"\n  [SKIP] {e}")

    # Learning curves
    try:
        results["learning_curves"] = run_learning_curves(X_train, X_test, y_train, y_test, le)
    except ImportError:
        print("\n  [SKIP] learning curves (xgboost not installed)")

    # Save results
    output_path = OUTPUT_DIR / "model_results.json"
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n\nResults saved to {output_path}")

    # Print summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    for key in ["logreg", "xgboost", "emb_xgboost"]:
        if key in results:
            r = results[key]
            print(f"  {r['method']:35s}  F1={r['f1_macro']:.4f}  latency={r['latency_ms']:.3f}ms")


if __name__ == "__main__":
    main()
