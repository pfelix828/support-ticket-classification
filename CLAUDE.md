# Support Ticket Classification

## What This Is
A full-stack project comparing classification methods for support ticket routing, using synthetic data modeled after OpenAI's help center taxonomy. Built as a portfolio piece for an OpenAI Support Data Science role.

## Structure
- `python/` — data generation, model training, evaluation
- `app/` — Next.js interactive web app (visualization, comparison, analysis)
- `reference/` — OpenAI help center taxonomy scraped for data generation

## Python
- Stack: Python 3.12+, pandas, numpy, scikit-learn
- Generate data: `cd python && python -m src.generate_data`
- Data exports to `app/public/data/`

## App
- Stack: Next.js, TypeScript, React, Tailwind, shadcn/ui, Recharts, Framer Motion
- Dev server: `cd app && npm run dev`
- Build: `cd app && npm run build`
- Design system shared with marketing-measurement project

## Key Design Decisions
- 12 Tier-1 categories modeled after OpenAI's real help center structure
- Realistic class imbalance (billing/ChatGPT dominate, Codex/Atlas rare)
- Natural category overlap between similar classes (API Usage vs API Errors, Account Access vs Account Mgmt) creates realistic classification challenges
- Structured metadata (customer tier, account age) for hybrid model features
- 7 methods compared: logistic regression, XGBoost, embeddings+XGBoost, BERT, LLM zero-shot, LLM few-shot, fine-tuned LLM
- Cascade architecture as production recommendation
