"""
Use Claude Haiku to paraphrase support ticket templates into diverse,
natural language variations that don't rely on category-specific keywords.

This makes the classification problem realistic — models need to understand
semantics, not just pattern-match on keywords like "refund" or "429".
"""

import json
import os
import time
import anthropic
from pathlib import Path

# Load API key
API_KEY = os.environ.get("ANTHROPIC_API_KEY")
if not API_KEY:
    raise ValueError("Set ANTHROPIC_API_KEY environment variable")

client = anthropic.Anthropic(api_key=API_KEY)

OUTPUT_DIR = Path(__file__).parent.parent.parent / "app" / "public" / "data"

SYSTEM_PROMPT = """You are helping generate realistic support ticket text for a classification benchmark.

Given a support ticket template, generate 10 diverse paraphrases that:
1. Express the SAME issue/intent but with completely different wording
2. Vary in length (some short and terse, some detailed with context)
3. Vary in tone (some frustrated, some polite, some matter-of-fact)
4. AVOID using obvious category-specific keywords when possible. For example:
   - Instead of "refund", say "get my money back" or "reverse the charge"
   - Instead of "can't log in", say "unable to access" or "my account won't open"
   - Instead of "rate limit" or "429", describe the symptom: "requests keep failing" or "getting throttled"
5. Sound like real people writing to customer support — typos are OK, incomplete sentences are OK
6. Include realistic details (error messages, timeframes, account info)

Return ONLY a JSON array of 10 strings, no other text. Example:
["paraphrase 1", "paraphrase 2", ...]"""


def paraphrase_template(template: str, category: str, urgency: str) -> list[str]:
    """Generate 10 paraphrases of a template using Claude Haiku."""
    prompt = f"""Category: {category}
Urgency: {urgency}
Original template: "{template}"

Generate 10 diverse paraphrases. Return ONLY a JSON array of 10 strings."""

    try:
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=2000,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )
        text = response.content[0].text.strip()
        # Strip markdown code blocks if present
        if text.startswith("```"):
            # Remove ```json or ``` prefix and trailing ```
            lines = text.split("\n")
            lines = [l for l in lines if not l.strip().startswith("```")]
            text = "\n".join(lines).strip()
        # Try to find JSON array in the response
        start = text.find("[")
        end = text.rfind("]")
        if start >= 0 and end > start:
            text = text[start:end + 1]
        paraphrases = json.loads(text)
        if isinstance(paraphrases, list) and len(paraphrases) > 0:
            return paraphrases
    except (json.JSONDecodeError, Exception) as e:
        print(f"  Error paraphrasing: {e}")

    return []


def extract_all_templates():
    """Extract all unique (template, category, urgency) tuples from generate_data.py."""
    from generate_data import CATEGORIES

    all_templates = []
    for category, info in CATEGORIES.items():
        for template_tuple in info["templates"]:
            text, urgency = template_tuple
            all_templates.append({
                "text": text,
                "category": category,
                "urgency": urgency,
            })

    print(f"Extracted {len(all_templates)} templates across {len(CATEGORIES)} categories")
    return all_templates


def main():
    templates = extract_all_templates()

    # Check for existing progress
    output_path = OUTPUT_DIR / "paraphrased_templates.json"
    if output_path.exists():
        with open(output_path) as f:
            existing = json.load(f)
        done_keys = {t["original"] for t in existing}
        print(f"Found {len(done_keys)} already paraphrased, resuming...")
    else:
        existing = []
        done_keys = set()

    total = len(templates)
    skipped = 0
    errors = 0

    for i, tmpl in enumerate(templates):
        if tmpl["text"] in done_keys:
            skipped += 1
            continue

        print(f"  [{i+1}/{total}] {tmpl['category']:20s} | {tmpl['text'][:60]}...")

        paraphrases = paraphrase_template(tmpl["text"], tmpl["category"], tmpl["urgency"])

        if paraphrases:
            existing.append({
                "original": tmpl["text"],
                "category": tmpl["category"],
                "urgency": tmpl["urgency"],
                "paraphrases": paraphrases,
            })
        else:
            errors += 1
            print(f"    FAILED — keeping original only")
            existing.append({
                "original": tmpl["text"],
                "category": tmpl["category"],
                "urgency": tmpl["urgency"],
                "paraphrases": [tmpl["text"]],  # fallback to original
            })

        # Save progress every 20 templates
        if (i + 1) % 20 == 0:
            with open(output_path, "w") as f:
                json.dump(existing, f, indent=2)
            print(f"    Saved progress ({len(existing)} templates)")

        # Rate limiting — Haiku is fast but let's not hammer it
        time.sleep(0.2)

    # Final save
    with open(output_path, "w") as f:
        json.dump(existing, f, indent=2)

    total_paraphrases = sum(len(t["paraphrases"]) for t in existing)
    print(f"\nDone!")
    print(f"  Templates processed: {len(existing)}")
    print(f"  Skipped (already done): {skipped}")
    print(f"  Errors: {errors}")
    print(f"  Total paraphrases: {total_paraphrases}")
    print(f"  Saved to {output_path}")


if __name__ == "__main__":
    main()
