"""
Generate realistic support tickets using LLM, grounded in OpenAI's
actual help center taxonomy. Instead of paraphrasing templates,
we ask the LLM to write fully original tickets about specific topics.
"""

import json
import os
import time
import anthropic
from pathlib import Path

API_KEY = os.environ.get("ANTHROPIC_API_KEY")
client = anthropic.Anthropic(api_key=API_KEY)

DATA_DIR = Path(__file__).parent.parent.parent / "app" / "public" / "data"

# Each category has specific subtopics drawn from OpenAI's help center articles.
# The LLM generates unique tickets about these real issues.

CATEGORY_TOPICS = {
    "billing": {
        "weight": 0.16,
        "subtopics": [
            "Unauthorized or unrecognized charges on account",
            "Requesting a refund for ChatGPT subscription (Plus, Pro, Go)",
            "Credit card declined during upgrade or renewal",
            "Double-charged for subscription",
            "Prepaid API credits not showing up or expiring",
            "Confusion about $5 hold after updating payment method",
            "Japanese Consumption Tax or Taiwan VAT on invoice",
            "Multi-currency billing — charged in wrong currency",
            "Invoice details wrong, need to update VAT ID or billing address",
            "Want to switch from monthly to annual billing",
            "Need sales tax exemption (U.S.) or W-9 for vendor registration",
            "Subscription shows as associated with a different account",
            "Need invoice broken down by project for cost allocation",
            "Accidentally purchased API credits instead of ChatGPT subscription",
            "Want to cancel auto-renewal but keep access until period ends",
            "Company credit card replaced, need to update payment method",
            "Charged after cancellation",
            "Confused about billing differences between ChatGPT and API Platform",
            "Need NET 30 payment terms for organization",
            "Free trial charges appearing unexpectedly",
        ],
    },
    "account_access": {
        "weight": 0.14,
        "subtopics": [
            "Can't log in after password reset",
            "Account deactivated or deleted without user action",
            "Traveling to unsupported country, can't access ChatGPT",
            "Suspicious Activity Alert blocking login",
            "Receiving verification emails not requested — possible compromise",
            "DeviceCheckError on login attempt",
            "Asked to verify login every single time",
            "Can't sign up — 'unsupported country' error",
            "Phone verification — Google Voice or VoIP number rejected",
            "Want to change phone number on account but not supported",
            "Deleted account, now want it back",
            "API Platform shows blank page on login",
            "Want to change sign-in method (Google to email/password, etc.)",
            "Getting CAPTCHAs on every ChatGPT interaction",
            "Passkey not working on new device",
            "Redirect loop after successful sign-in",
            "VPN blocking ChatGPT access",
            "Work email no longer accessible, locked out of account",
            "2FA authenticator codes not being accepted",
            "Account stuck in age verification loop",
            "Password reset link expired before use",
            "Session keeps expiring every few minutes",
            "Too many login attempts error after single try",
        ],
    },
    "account_management": {
        "weight": 0.08,
        "subtopics": [
            "How to add or remove members from API organization",
            "Need to change email address on account",
            "Transfer ownership of API organization",
            "Change default organization",
            "Domain verification for organization",
            "Change API platform org name",
            "Managing projects in API platform",
            "Reporting suspicious activity or unauthorized access",
            "Change display name",
            "Cancel API subscription entirely",
            "Merge two OpenAI accounts",
            "Set usage limits per team member",
            "Create separate API keys for dev and production",
            "Restrict which models team members can access",
            "View audit log for organization",
            "Revoke access for departed contractor",
        ],
    },
    "api_errors": {
        "weight": 0.12,
        "subtopics": [
            "429 Too Many Requests despite being under rate limit",
            "API key showing as incorrect",
            "Rate limit errors on Assistants API below quota",
            "High API latency for extended period",
            "File storage quota exceeded for Assistants",
            "Different completions in Playground vs API",
            "Intermittent 500 errors on API calls",
            "Usage limit reached unexpectedly",
            "Fine-tuning job failed with no error message",
            "Embeddings returning wrong dimensions",
            "Timeout on long Chat Completions requests",
            "Batch API rejecting input file format",
            "Function calling returning malformed JSON",
            "Streaming response cutting off mid-sentence",
            "Structured output schema being ignored",
            "Model not available despite correct tier",
            "Moderation endpoint flagging benign content",
            "Vision API rejecting images without error details",
            "Token count mismatch between response and dashboard",
            "Webhook for async completions never firing",
        ],
    },
    "api_usage": {
        "weight": 0.08,
        "subtopics": [
            "Getting started with the OpenAI API",
            "Difference between prompt tokens and completion tokens",
            "Where to find API key",
            "How to use Chat Completions API for a chatbot",
            "Whether Playground tokens count toward usage",
            "How to format data for fine-tuning",
            "Best practices for prompt engineering",
            "How to check token usage",
            "Using the API with non-English languages",
            "Migrating from Assistants API to Responses API",
            "Choosing between models for a use case",
            "Implementing streaming responses",
            "Using embeddings for semantic search",
            "Maximum context window for specific models",
            "Setting up the Python SDK",
            "Using Batch API for bulk processing",
            "Using structured outputs with JSON schemas",
            "Data residency options for API",
        ],
    },
    "chatgpt_product": {
        "weight": 0.15,
        "subtopics": [
            "ChatGPT extremely slow or stuck on loading spinner",
            "Chat history disappeared",
            "Image generation failing with no error",
            "Memory not working — forgetting previous context",
            "Deep research returning broken sources",
            "Agent mode not browsing web correctly",
            "ChatGPT search showing outdated information",
            "Voice mode cutting off sentences or disconnecting",
            "File upload stuck in processing",
            "ChatGPT refusing legitimate requests (false positive safety)",
            "Custom instructions being ignored",
            "Data analysis giving wrong calculations",
            "Can't switch between models — dropdown grayed out",
            "Temporary chat conversations being saved",
            "Study mode asking wrong type of questions",
            "Image editing creating artifacts",
            "Reached usage cap unexpectedly",
            "Conversation cut off, can't continue",
            "ChatGPT generating text in wrong language",
            "Tasks not running at scheduled time",
        ],
    },
    "chatgpt_apps": {
        "weight": 0.08,
        "subtopics": [
            "iOS app crashing during voice mode",
            "Cancel subscription through Apple App Store",
            "Can't log in to Android app with Microsoft account",
            "macOS screenshot tool not working",
            "Chat history not syncing between web and mobile app",
            "Windows app won't open after update",
            "Connected apps (Google Drive, Outlook, etc.) disconnecting",
            "Subscribed through Google Play but showing as free",
            "Android app excessive battery usage",
            "iOS widget not loading conversations",
            "Voice mode delay on mobile",
            "Files uploaded on app not visible on web",
            "macOS app not appearing in menu bar",
            "Windows app installer error",
            "iPad Split View not working properly",
            "Can't copy text from conversations in mobile app",
        ],
    },
    "enterprise": {
        "weight": 0.06,
        "subtopics": [
            "Configure SSO for Enterprise workspace",
            "SCIM provisioning not syncing user directory",
            "Domain verification for organization",
            "Difference between Enterprise and Business plans",
            "Managing admin roles in Enterprise workspace",
            "Workspace analytics not updating",
            "Setting up ChatGPT Edu for university",
            "Need BAA for HIPAA compliance",
            "SAML SSO returning errors during login",
            "Azure AD SCIM deprovisioning users incorrectly",
            "Migrating from Business to Enterprise",
            "Data residency configuration for Enterprise",
            "IP ranges to allowlist for Enterprise",
            "FERPA compliance for Edu workspace",
            "Admin console not loading",
            "Custom data retention policies for compliance",
            "Bulk user onboarding",
            "Enterprise contract renewal",
        ],
    },
    "gpts": {
        "weight": 0.05,
        "subtopics": [
            "Custom GPT won't publish to GPT Store",
            "GPT actions (API calls) not connecting",
            "GPT restricted from sharing, want to appeal",
            "Knowledge files not being used by GPT",
            "GPT not following instructions",
            "GPT hallucinating instead of using knowledge base",
            "Actions stopped working after schema update",
            "Authentication setup for GPT actions",
            "GPT builder preview doesn't match published behavior",
            "GPT Store review pending for weeks",
            "GPT removed from Store without explanation",
            "GPT action timing out due to slow external API",
            "GPT giving different answers to users vs during testing",
        ],
    },
    "newer_products": {
        "weight": 0.04,
        "subtopics": [
            "Sora video generation failing with no error",
            "Sora generating videos with artifacts/distortion",
            "Sora taking extremely long for short clips",
            "Sora credit usage seems too high",
            "Sora won't generate videos with people",
            "Codex making incorrect code changes",
            "Codex timing out on large PRs",
            "Codex ignoring coding standards",
            "Codex agent running indefinitely with no progress",
            "Codex suggesting deprecated dependencies",
            "ChatGPT Atlas not rendering pages",
            "Atlas blocked by company firewall",
            "Atlas can't log in to sites on user's behalf",
            "Connecting Codex to private GitHub organization",
        ],
    },
    "privacy_policy": {
        "weight": 0.03,
        "subtopics": [
            "Opt out of data being used for training",
            "Export all ChatGPT data",
            "How data is handled — API vs ChatGPT",
            "Whether OpenAI stores API inputs and outputs",
            "Delete account and all associated data",
            "GDPR right to erasure request",
            "Accidentally shared sensitive information in chat",
            "CCPA data request",
            "Whether model training opt-out is retroactive",
            "Need DPA signed by legal team",
            "SOC 2 compliance documentation",
            "Data handling documentation for vendor assessment",
            "Whether voice conversations are stored differently",
            "What data the mobile app collects",
        ],
    },
    "security": {
        "weight": 0.01,
        "subtopics": [
            "API key leaked — need to secure account",
            "Unauthorized usage on API account",
            "API key accidentally committed to public GitHub repo",
            "Someone using API key, running up charges",
            "Unknown IP accessed API organization",
            "Security vulnerability found in API — how to report",
            "Need to restrict API key to specific IP addresses",
            "Key rotation setup for production",
            "Phishing attempt pretending to be OpenAI",
            "API key exposed in client-side application",
        ],
    },
}

SYSTEM_PROMPT = """You generate realistic customer support tickets for a classification benchmark dataset.

Write tickets that sound like REAL people contacting support. Key rules:
1. Each ticket should be a completely unique situation — different details, context, and phrasing
2. Vary the writing quality: some well-written, some with typos/grammar issues, some terse, some rambling
3. Vary the tone: frustrated, confused, polite, demanding, panicked, matter-of-fact
4. Some tickets should be vague about the actual problem — the user describes symptoms not root causes
5. Include realistic details: error messages, account info, timeframes, device names, but also irrelevant context
6. Some tickets should mention issues from OTHER categories tangentially (e.g., a billing ticket that mentions they also can't log in)
7. Vary length: some are one sentence, some are a full paragraph with background context
8. Don't use support jargon — real users don't say "I need to escalate" or "please route to billing team"

Return ONLY a JSON array of strings. No other text."""


def generate_tickets_for_subtopic(category: str, subtopic: str, count: int = 30) -> list[str]:
    """Generate unique tickets for a specific subtopic."""
    prompt = f"""Generate {count} unique, realistic support tickets about this issue:

Category: {category}
Specific issue: {subtopic}

Make each ticket a completely different situation with different details, context, and writing style. Some should be hard to classify — vague, mentioning other issues, burying the real problem.

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
            return result
    except Exception as e:
        print(f"    Error: {e}")
    return []


def main():
    output_path = DATA_DIR / "realistic_tickets.json"

    # Resume support
    if output_path.exists():
        with open(output_path) as f:
            all_tickets = json.load(f)
        done_keys = {(t["category"], t["subtopic"]) for t in all_tickets}
        print(f"Resuming: {len(done_keys)} subtopics already done")
    else:
        all_tickets = []
        done_keys = set()

    total_subtopics = sum(len(c["subtopics"]) for c in CATEGORY_TOPICS.values())
    processed = 0

    for category, info in CATEGORY_TOPICS.items():
        for subtopic in info["subtopics"]:
            processed += 1
            if (category, subtopic) in done_keys:
                continue

            print(f"  [{processed}/{total_subtopics}] {category:20s} | {subtopic[:55]}...")

            tickets = generate_tickets_for_subtopic(category, subtopic, count=30)

            for ticket_text in tickets:
                all_tickets.append({
                    "text": ticket_text,
                    "category": category,
                    "subtopic": subtopic,
                })

            # Save progress every 10 subtopics
            if processed % 10 == 0:
                with open(output_path, "w") as f:
                    json.dump(all_tickets, f, indent=2)
                print(f"    Saved progress ({len(all_tickets)} tickets)")

            time.sleep(0.3)

    # Final save
    with open(output_path, "w") as f:
        json.dump(all_tickets, f, indent=2)

    # Stats
    from collections import Counter
    cat_counts = Counter(t["category"] for t in all_tickets)
    print(f"\nDone! {len(all_tickets)} total tickets")
    for cat, count in cat_counts.most_common():
        print(f"  {cat:25s} {count:5d}")


if __name__ == "__main__":
    main()
