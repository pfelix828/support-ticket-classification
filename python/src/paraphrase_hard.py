"""
Generate deliberately harder paraphrases that blur category boundaries.
Instead of faithfully paraphrasing, we ask the LLM to make tickets
that are semantically ambiguous — preserving the ground truth category
but using language that could plausibly belong to 2-3 categories.
"""

import json
import os
import time
import anthropic
from pathlib import Path

API_KEY = os.environ.get("ANTHROPIC_API_KEY")
client = anthropic.Anthropic(api_key=API_KEY)

DATA_DIR = Path(__file__).parent.parent.parent / "app" / "public" / "data"

CATEGORY_DESCRIPTIONS = {
    "billing": "Refunds, charges, payment methods, invoices, credits",
    "account_access": "Login issues, password reset, account recovery, phone verification",
    "account_management": "Members, orgs, projects, security, email changes",
    "api_errors": "Rate limits, 429 errors, API key issues, latency, error codes",
    "api_usage": "How-to, getting started, best practices, billing/usage dashboard",
    "chatgpt_product": "ChatGPT features, errors, slow responses, image generation, search, memory",
    "chatgpt_apps": "iOS, Android, macOS, Windows app issues, connected apps",
    "enterprise": "Enterprise, Business, Edu workspace setup, SSO, SCIM, admin",
    "gpts": "Custom GPT creation, publishing, configuration, actions, troubleshooting",
    "newer_products": "Sora, Codex, ChatGPT Atlas — newer product issues",
    "privacy_policy": "Data privacy, training opt-out, data export, content policies",
    "security": "API key safety, vulnerability reporting, fraud",
}

# Which categories are commonly confused with each other
CONFUSION_NEIGHBORS = {
    "billing": ["account_management", "api_usage", "account_access"],
    "account_access": ["account_management", "security", "chatgpt_apps"],
    "account_management": ["account_access", "enterprise", "billing"],
    "api_errors": ["api_usage", "chatgpt_product", "gpts"],
    "api_usage": ["api_errors", "chatgpt_product", "billing"],
    "chatgpt_product": ["chatgpt_apps", "api_errors", "gpts"],
    "chatgpt_apps": ["chatgpt_product", "account_access", "billing"],
    "enterprise": ["account_management", "billing", "security"],
    "gpts": ["chatgpt_product", "api_errors", "enterprise"],
    "newer_products": ["chatgpt_product", "api_errors", "chatgpt_apps"],
    "privacy_policy": ["account_management", "security", "account_access"],
    "security": ["account_access", "billing", "privacy_policy"],
}

SYSTEM_PROMPT = """You generate realistic support tickets for a classification benchmark.

Your goal is to make tickets that are HARD to classify. The ticket should genuinely belong to the specified category, but it should use language and framing that could plausibly suggest neighboring categories.

Rules:
1. The ticket MUST be about the specified category's topic at its core
2. But phrase it in a way that's VAGUE, INDIRECT, or uses language from neighboring categories
3. Don't use obvious category keywords — instead of "refund" say "get my money back" or just "fix this charge situation"
4. Write like a real frustrated/confused user — incomplete sentences, vague descriptions, burying the actual issue
5. Vary length: some are 1 sentence, some are a full paragraph
6. Include realistic but misleading context (mentioning other products, past issues, etc.)
7. Make some tickets where the user describes symptoms rather than the actual problem

Examples of HARD tickets:
- For billing: "My account is showing something weird and I can't use the service anymore" (could be access, could be billing)
- For api_errors: "The thing I built stopped working after I made changes yesterday" (could be api_errors, api_usage, or gpts)
- For account_access: "I can't do anything with my account right now" (could be access, management, or billing)

Return ONLY a JSON array of 15 strings."""


def generate_hard_tickets(category: str, original: str) -> list[str]:
    """Generate 15 hard-to-classify paraphrases."""
    neighbors = CONFUSION_NEIGHBORS.get(category, [])
    neighbor_descs = {n: CATEGORY_DESCRIPTIONS[n] for n in neighbors}

    prompt = f"""Generate 15 support tickets that belong to category "{category}" ({CATEGORY_DESCRIPTIONS[category]}).

Original ticket: "{original}"

Make them HARD to classify. The tickets should be about this topic but use language that could also suggest these neighboring categories:
{json.dumps(neighbor_descs, indent=2)}

The ticket must genuinely be about {category}, but a classifier should struggle to distinguish it from the neighbors.

Return ONLY a JSON array of 15 strings."""

    try:
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=3000,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )
        text = response.content[0].text.strip()
        if text.startswith("```"):
            lines = text.split("\n")
            lines = [l for l in lines if not l.strip().startswith("```")]
            text = "\n".join(lines).strip()
        start = text.find("[")
        end = text.rfind("]")
        if start >= 0 and end > start:
            text = text[start:end + 1]
        result = json.loads(text)
        if isinstance(result, list):
            return result
    except Exception as e:
        print(f"  Error: {e}")
    return []


def main():
    # Load existing paraphrases to get the template list
    with open(DATA_DIR / "paraphrased_templates.json") as f:
        existing = json.load(f)

    output_path = DATA_DIR / "hard_paraphrases.json"
    if output_path.exists():
        with open(output_path) as f:
            hard = json.load(f)
        done_keys = {t["original"] for t in hard}
        print(f"Resuming: {len(done_keys)} already done")
    else:
        hard = []
        done_keys = set()

    # Sample ~25 templates per category (total ~300) for hard paraphrases
    # This gives us ~4500 hard tickets + 3690 normal paraphrases = ~8000 unique texts
    by_cat = {}
    for t in existing:
        cat = t["category"]
        if cat not in by_cat:
            by_cat[cat] = []
        by_cat[cat].append(t)

    selected = []
    for cat, templates in by_cat.items():
        # Take up to 25 templates per category
        sample = templates[:25] if len(templates) >= 25 else templates
        selected.extend(sample)

    print(f"Selected {len(selected)} templates for hard paraphrasing")

    for i, tmpl in enumerate(selected):
        if tmpl["original"] in done_keys:
            continue

        print(f"  [{i+1}/{len(selected)}] {tmpl['category']:20s} | {tmpl['original'][:55]}...")

        tickets = generate_hard_tickets(tmpl["category"], tmpl["original"])

        hard.append({
            "original": tmpl["original"],
            "category": tmpl["category"],
            "urgency": tmpl["urgency"],
            "hard_paraphrases": tickets,
        })

        if (i + 1) % 20 == 0:
            with open(output_path, "w") as f:
                json.dump(hard, f, indent=2)
            print(f"    Saved progress ({len(hard)} templates)")

        time.sleep(0.2)

    with open(output_path, "w") as f:
        json.dump(hard, f, indent=2)

    total = sum(len(t["hard_paraphrases"]) for t in hard)
    print(f"\nDone! {len(hard)} templates → {total} hard paraphrases")


if __name__ == "__main__":
    main()
