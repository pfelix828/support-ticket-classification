# Checkpoint — Support Ticket Classification Project

**Date:** 2026-04-15
**Status:** Feature-complete. All results measured and deployed.

---

## What's Done

### App (13 pages, fully deployed)
- Live at `support-ticket-classification.vercel.app`
- GitHub: `github.com/pfelix828/support-ticket-classification`
- Portfolio page synced at `pfelix828.github.io`
- Synthetic data disclaimer banner on every page
- Glossary page with plain-language definitions

### All Model Results (REAL, measured)

| Method | F1 (macro) | Training Data |
|---|---|---|
| GPT-4o-mini Standard FT | 96.1% | 9,557 human labels |
| Fine-Tuned BERT | 91.2% | 9,557 human labels |
| Embeddings + XGBoost | 89.1% | 9,557 human labels |
| TF-IDF + Logistic Regression | 87.4% | 9,557 human labels |
| TF-IDF + XGBoost | 86.3% | 9,557 human labels |
| Distillation with reasoning | 79.8% | 7,358 o4-mini labels (1 epoch) |
| GPT-4o-mini Few-Shot | 78.9% | 0 (24 prompt examples) |
| Distillation labels only | 78.9% | 7,358 o4-mini labels (3 epochs) |
| GPT-4o-mini Zero-Shot | 77.7% | 0 |
| Distillation v1 | 69.9% | 855 o1-mini labels |

### Learning Curves (all measured)
- LogReg, XGBoost, Emb+XGB, BERT: measured at 100, 500, 1K, 2.5K, 5K, 9.5K
- Fine-tuned LLM: measured at 500 (88.0%), 2.5K (94.4%), 9.5K (96.1%)
- Zero-shot & few-shot: constant (77.7%, 78.9%)

### Methodological Audit (completed)
All issues from the audit have been addressed:
- ✅ Recommendation table matches measured data
- ✅ Removed false "10% ambiguous tickets" claims
- ✅ Distillation page honestly describes implementation vs aspiration
- ✅ Scaling table labeled as projected estimates
- ✅ Error analysis updated with real BERT data
- ✅ Methodology page synced with reality
- ✅ Portfolio .qmd synced with app
- ✅ Single-seed caveat added
- ✅ Log scale claim removed
- ✅ "Why it failed" section added to distillation page

---

## Key Findings

1. **Fine-tuned LLM dominates from 500 tickets onward** — 88% F1 at just 500 tickets already beats every classical method at full training set.

2. **Distillation failed because the teacher wasn't good enough** — o4-mini zero-shot (~85% accuracy) teaching GPT-4o-mini is "sideways distillation." A frontier teacher (o1, Opus) would be needed.

3. **Reasoning transfer added <1 point** — Including chain-of-thought in training (79.8%) barely beat labels only (78.9%).

4. **LogReg beats XGBoost** — 87.4% vs 86.3%. Surprise finding.

5. **BERT needs data** — 6.5% F1 at 100 tickets, but 91.2% at 9.5K. Terrible at low volume, excellent at high volume.

---

## Deployment Notes

- Vercel deploys via CLI: `cd app && npx vercel --prod --scope pfelix828s-projects --yes`
- Must manually alias: `npx vercel alias set <deploy-url> support-ticket-classification.vercel.app --scope pfelix828s-projects`
- Git-triggered deploys don't reliably update the production alias
- `ignoreBuildErrors: true` in next.config.ts (Vercel overwrites tsconfig)
- Relative imports used (not @/ aliases) for Vercel compatibility
- Portfolio site: `cd portfolio-site && quarto render && git push` (must render full site, not single page)

## Key File Locations

| File | Purpose |
|------|---------|
| `app/public/data/model_results.json` | All model results (loaded by app) |
| `app/public/data/realistic_tickets.json` | 12,091 LLM-generated tickets |
| `python/src/train_models.py` | Local model training (TF-IDF, XGBoost, Embeddings) |
| `python/src/train_bert.py` | BERT fine-tuning |
| `python/src/run_batch.py` | OpenAI Batch API operations |
| `python/src/run_finetune.py` | OpenAI fine-tuning + distillation v1 |
| `python/src/run_distillation_batch.py` | Distillation v2/v3 (chunked batch labeling) |
| `python/src/learning_curves_full.py` | Full learning curve generation |
| `python/batch/distill_meta.json` | Distillation job IDs and metadata |
| `python/.env` | API keys (OPENAI_API_KEY) |
