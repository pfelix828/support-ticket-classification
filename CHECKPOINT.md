# Checkpoint — Support Ticket Classification Project

**Date:** 2026-04-14, ~10:30 PM
**Status:** Batch API jobs submitted, waiting for results

---

## What's Done

### App (fully built, deployed)
- 12-page Next.js app at `support-ticket-classification.vercel.app`
- GitHub repo: `github.com/pfelix828/support-ticket-classification`
- Added to portfolio site at `pfelix828.github.io`

### Data
- 12,091 unique realistic tickets generated via Claude Haiku
- 12 categories modeled after OpenAI's help center taxonomy
- Full test set: 2,390 tickets (±1.5% margin on F1)

### Local Model Results (REAL, measured)
Saved in `app/public/data/model_results.json`:
- **TF-IDF + Logistic Regression:** F1 macro = 0.8741
- **TF-IDF + XGBoost:** F1 macro = 0.8630
- **Embeddings + XGBoost:** F1 macro = 0.8914
- Learning curves at 100, 500, 1K, 5K, 9.5K tickets

### OpenAI API Results — STALE, being re-evaluated
- Zero-shot & few-shot results in model_results.json are from old/failed runs
- Fresh results coming from Batch API (see below)

---

## What's Running / Waiting

### 1. Batch API Jobs (submitted 2026-04-14 ~10:15 PM)
Batch IDs saved in `python/batch/batch_ids.json`:
- **Zero-shot batch:** `batch_69df01e41c4881909529761a97dc054b` — 2,390 tickets
- **Few-shot batch:** `batch_69df01ea63748190b4e66be00d36cd0a` — 2,390 tickets, 2 examples/category

Check status and get results:
```bash
cd /Users/pfelix/Claude/portfolio/support-ticket-classification/python
export $(grep OPENAI_API_KEY .env)
python3 -m src.run_batch status
python3 -m src.run_batch results   # downloads results, computes metrics, saves to model_results.json
```

### 2. Fine-tuning Jobs (still running as of 10:15 PM)
- **Standard FT:** `ftjob-p0eCw0DrNZzthLN5XcvlZRua` — gpt-4o-mini on 9,557 tickets
- **Distillation FT:** `ftjob-wEZ9QjqdCJvmbmrwjPLGknZk` — gpt-4o-mini distilled from 855 o4-mini labels

Check status:
```bash
python3 -c "from openai import OpenAI; c=OpenAI(); [print(f'{n}: {c.fine_tuning.jobs.retrieve(j).status}, {c.fine_tuning.jobs.retrieve(j).fine_tuned_model}') for j,n in [('ftjob-p0eCw0DrNZzthLN5XcvlZRua','Standard'),('ftjob-wEZ9QjqdCJvmbmrwjPLGknZk','Distilled')]]"
```

Once fine-tuning jobs are done, re-run `python3 -m src.run_batch submit` — it will detect the completed models and submit eval batches for them too. Then `status` → `results` as before.

### 3. Rate Limit Note
- **Real-time API (run_openai_fast.py) is RPD-limited** — 10,000 requests/day, burned through on 2026-04-14
- Resets ~24h from first use. Batch API is unaffected.
- For future real-time runs, the script now has token-aware auto-concurrency

---

## What's Left To Do (After Batch Results)

### Wire Results Into App
All pages currently have HARDCODED numbers that need replacing with real results from `model_results.json`:
- `app/src/app/baseline/page.tsx` — replace hardcoded F1 scores, per-class F1, top features
- `app/src/app/embeddings/page.tsx` — replace feature importance percentages
- `app/src/app/bert/page.tsx` — BERT was never trained; label results as "projected" or skip
- `app/src/app/llm/page.tsx` — replace with real zero/few-shot numbers
- `app/src/app/finetune/page.tsx` — replace with real fine-tuning results
- `app/src/app/distillation/page.tsx` — replace with real distillation results
- `app/src/app/comparison/page.tsx` — replace learning curve data with real numbers
- `app/src/app/errors/page.tsx` — replace confusion pairs with real confusion matrix data
- `app/src/app/architecture/page.tsx` — fix cascade math (claimed 96% but component accuracies only give ~93%)

### Fix Issues From Review
- Add visible "simulated" / "projected" labels on pages without real results (BERT, possibly distillation)
- Fix "accuracy" vs "F1" terminology inconsistency
- Update methodology page to reflect v3 data generation (LLM-generated, not templates)
- Update homepage stats (ticket count, method count)
- Commit and push to GitHub
- Redeploy to Vercel

---

## Key Scripts

| Script | Purpose |
|--------|---------|
| `python/src/run_batch.py` | **USE THIS** — Batch API submit/status/results (no rate limits) |
| `python/src/run_openai_fast.py` | Real-time API eval (token-aware concurrency, use after RPD resets) |
| `python/src/run_finetune.py` | Fine-tuning job submission/evaluation |
| `python/src/train_models.py` | Local model training (TF-IDF, XGBoost, Embeddings) |

## Key File Locations

| File | Purpose |
|------|---------|
| `python/.env` | API keys (OPENAI_API_KEY, ANTHROPIC_API_KEY) |
| `python/batch/batch_ids.json` | Current batch job IDs |
| `python/batch/test_meta.json` | Test set labels for batch results processing |
| `app/public/data/model_results.json` | All model results (loaded by app) |
| `app/public/data/realistic_tickets.json` | 12,091 LLM-generated tickets |

## Quick Resume Tomorrow
```bash
cd /Users/pfelix/Claude/portfolio/support-ticket-classification/python
export $(grep OPENAI_API_KEY .env)

# 1. Check batch results (should be done)
python3 -m src.run_batch status
python3 -m src.run_batch results

# 2. Check fine-tuning jobs
python3 -c "from openai import OpenAI; c=OpenAI(); [print(f'{n}: {c.fine_tuning.jobs.retrieve(j).status}') for j,n in [('ftjob-p0eCw0DrNZzthLN5XcvlZRua','Standard'),('ftjob-wEZ9QjqdCJvmbmrwjPLGknZk','Distilled')]]"

# 3. If fine-tuning done, submit those evals too
python3 -m src.run_batch submit
python3 -m src.run_batch status
python3 -m src.run_batch results

# 4. Wire results into app, commit, deploy
```
