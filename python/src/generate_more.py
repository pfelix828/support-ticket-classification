"""
Generate a second batch of realistic tickets to supplement the existing 6K.
Uses the same subtopics but asks for NEW unique tickets.
"""

import json
import os
import time
import anthropic
from pathlib import Path

API_KEY = os.environ.get("ANTHROPIC_API_KEY")
client = anthropic.Anthropic(api_key=API_KEY)

DATA_DIR = Path(__file__).parent.parent.parent / "app" / "public" / "data"

# Import subtopics from the main generator
from generate_realistic import CATEGORY_TOPICS, SYSTEM_PROMPT


def generate_batch(category: str, subtopic: str, existing_texts: set, count: int = 30) -> list[str]:
    """Generate unique tickets, avoiding duplicates with existing."""
    prompt = f"""Generate {count} unique, realistic support tickets about this issue:

Category: {category}
Specific issue: {subtopic}

IMPORTANT: Make these DIFFERENT from any previous tickets. Use different scenarios,
different user backgrounds, different levels of technical sophistication.
Some should be from enterprise users, some from hobbyists, some from developers.

Return ONLY a JSON array of {count} strings."""

    try:
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=8000,
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
            # Filter out exact duplicates
            new_tickets = [t for t in result if t not in existing_texts]
            return new_tickets
    except Exception as e:
        print(f"    Error: {e}")
    return []


def main():
    # Load existing tickets
    with open(DATA_DIR / "realistic_tickets.json") as f:
        existing = json.load(f)

    existing_texts = {t["text"] for t in existing}
    print(f"Existing tickets: {len(existing)} ({len(existing_texts)} unique)")

    total_subtopics = sum(len(c["subtopics"]) for c in CATEGORY_TOPICS.values())
    processed = 0
    new_count = 0

    for category, info in CATEGORY_TOPICS.items():
        for subtopic in info["subtopics"]:
            processed += 1
            print(f"  [{processed}/{total_subtopics}] {category:20s} | {subtopic[:55]}...")

            tickets = generate_batch(category, subtopic, existing_texts, count=30)

            for ticket_text in tickets:
                existing.append({
                    "text": ticket_text,
                    "category": category,
                    "subtopic": subtopic,
                })
                existing_texts.add(ticket_text)
                new_count += 1

            if processed % 10 == 0:
                with open(DATA_DIR / "realistic_tickets.json", "w") as f:
                    json.dump(existing, f, indent=2)
                print(f"    Saved ({new_count} new, {len(existing)} total)")

            time.sleep(0.2)

    # Final save
    with open(DATA_DIR / "realistic_tickets.json", "w") as f:
        json.dump(existing, f, indent=2)

    from collections import Counter
    cat_counts = Counter(t["category"] for t in existing)
    print(f"\nDone! {new_count} new tickets, {len(existing)} total")
    for cat, count in cat_counts.most_common():
        print(f"  {cat:25s} {count:5d}")


if __name__ == "__main__":
    main()
