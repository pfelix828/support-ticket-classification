# Support Ticket Classification: Method Comparison

**Live demo: [support-ticket-classification.vercel.app](https://support-ticket-classification.vercel.app)**

Eight ways to classify support tickets, compared honestly on the same data: how much labeled data does each method need, what does each cost, and when is each one the right choice?

All results are measured, not projected. The data is synthetic, modeled after OpenAI's public help center taxonomy, and every page of the app says so.

## The comparison

| Method | F1 (macro) | Labeled data used |
|---|---|---|
| Fine-tuned GPT-4o-mini | 96.1% | 9,557 |
| Fine-tuned BERT | 91.2% | 9,557 |
| Embeddings + XGBoost | 89.1% | 9,557 |
| TF-IDF + Logistic Regression | 87.4% | 9,557 |
| TF-IDF + XGBoost | 86.3% | 9,557 |
| Distillation, with reasoning | 79.8% | 7,358 model-generated labels |
| LLM few-shot | 78.9% | 24 prompt examples |
| LLM zero-shot | 77.7% | 0 |

Learning curves were measured at 100, 500, 1,000, 2,500, 5,000, and 9,500 labels for the classical methods and BERT, and at 500, 2,500, and 9,500 for the fine-tuned LLM.

## What stood out

- **The fine-tuned LLM wins early.** At just 500 labeled tickets it reaches 88% F1, already beating every classical method at the full training set.
- **Distillation failed, and the writeup says why.** A mid-tier teacher labeling data for a same-tier student is sideways distillation; the student capped out near the teacher's own accuracy. Adding chain-of-thought reasoning to training moved the result less than one point.
- **Logistic regression beat XGBoost** on TF-IDF features, 87.4% vs 86.3%.
- **BERT is volume-hungry.** 6.5% F1 at 100 tickets, 91.2% at 9,500.

The app's production recommendation is a cascade: a cheap classical model handles confident cases, the fine-tuned LLM handles the rest.

## Data honesty

Tickets are LLM-generated using OpenAI's public help center category structure as the seed: 12 top-level categories with realistic class imbalance and natural overlap between neighboring categories. No real customer data is involved, and conclusions about absolute accuracy should not be transferred to production data. The method comparison and data-volume tradeoffs are the point.

## Structure

- `app/` — Next.js app: data explorer, per-method pages, learning curves, error analysis, methodology, glossary
- `python/` — data generation, model training, OpenAI Batch API and fine-tuning runs
- `reference/` — public help center taxonomy used to seed data generation

## Run locally

```bash
# App
cd app && npm install && npm run dev

# Python pipeline (regenerates data into app/public/data/)
cd python && python -m src.generate_data
```

Model results load from precomputed JSON in `app/public/data/`, so the app runs without any API keys.
