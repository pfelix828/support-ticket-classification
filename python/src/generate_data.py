"""
Synthetic support ticket generator modeled after OpenAI's help center taxonomy.

Generates 100K realistic tickets with:
- 12 Tier-1 categories (broad routing)
- Realistic class imbalance (billing/ChatGPT dominate, Codex/Atlas rare)
- Compositional variation (template + detail + context + tone)
- Structured metadata (customer tier, account age, previous tickets)
- Ambiguous and multi-intent tickets for hard classification cases
- Typos, abbreviations, and varied writing styles
"""

import json
import random
from dataclasses import dataclass, asdict
from pathlib import Path

# Reproducibility
random.seed(42)

# --- Placeholder pools (expanded for variation) ---

PLANS = ["Plus", "Pro", "Go", "Enterprise", "Team", "Business", "Edu"]
COUNTRIES = [
    "Japan", "South Korea", "Germany", "Brazil", "India", "UK", "France",
    "Italy", "Spain", "Mexico", "Turkey", "Indonesia", "Nigeria", "Egypt",
    "Vietnam", "Thailand", "Russia", "China", "Iran", "Cuba",
]
TIMEFRAMES = [
    "last week", "last month", "yesterday", "two days ago", "this morning",
    "3 days ago", "a few hours ago", "last night", "on Monday", "on Friday",
    "earlier today", "about a week ago", "2 weeks ago",
]
AMOUNTS = [
    "19.99", "29.99", "200", "5", "99", "49.99", "500", "20", "100",
    "9.99", "59.99", "149", "39.99", "0.50", "1200", "75", "12.50",
]
MODELS = [
    "GPT-4o", "GPT-4o mini", "GPT-5.3", "GPT-5.4", "o4-mini", "o3",
    "DALL-E 3", "GPT Image", "Whisper",
]
ERROR_CODES = ["429", "500", "503", "401", "403", "400", "404", "422", "502"]
DEVICES = ["iPhone", "iPad", "Pixel", "Samsung Galaxy", "MacBook", "Windows PC", "iMac"]
BROWSERS = ["Chrome", "Safari", "Firefox", "Edge", "Arc"]
LANGUAGES = ["Spanish", "Japanese", "Korean", "Portuguese", "French", "German", "Arabic", "Chinese", "Hindi"]
FILE_TYPES = ["PDF", "CSV", "Excel file", "Word document", "PowerPoint", "image", "JSON file"]
APP_INTEGRATIONS = [
    "Google Drive", "Outlook", "Slack", "GitHub", "Linear", "Notion",
    "Asana", "Dropbox", "SharePoint", "Box", "Intercom", "Zoho",
]

# --- Detail fragments (appended to base templates for variation) ---

DETAIL_FRAGMENTS = {
    "billing": [
        " I've been a paying customer for {months} months.",
        " My company needs this resolved for month-end closing.",
        " I've tried updating my payment method but it still fails.",
        " This is the second time this has happened.",
        " I need the invoice for tax purposes.",
        " We're on the {plan} plan for our team of {team_size} people.",
        " I was not notified about this charge.",
        " I checked my bank and the charge went through twice.",
        " The amount doesn't match what's shown in my settings.",
        " I've attached a screenshot of the charge.",
        "",
        "",
        "",
    ],
    "account_access": [
        " I've tried on both {browser} and {browser2}.",
        " This started happening after the recent update.",
        " I need access urgently for a deadline.",
        " I've cleared my cookies and cache.",
        " My team is also experiencing this issue.",
        " The error page doesn't give any useful information.",
        " I'm using a VPN, could that be the issue?",
        " I've tried both the web and mobile app.",
        " It works on my phone but not my computer.",
        "",
        "",
        "",
    ],
    "account_management": [
        " We have {team_size} people in our organization.",
        " I'm the admin for our API organization.",
        " We're migrating from another AI provider and need this resolved.",
        " This is blocking onboarding for new team members.",
        "",
        "",
        "",
    ],
    "api_errors": [
        " I'm using the {model} model.",
        " This happens about {pct}% of the time.",
        " My code worked fine until {timeframe}.",
        " I'm on tier {tier} for rate limits.",
        " I've checked the status page and it shows all green.",
        " Here's the error message: {error_code}",
        " I've been debugging this for hours.",
        " The same request works in the Playground but fails via API.",
        " I'm using Python SDK version 1.x.",
        " We process about {volume} requests per minute.",
        "",
        "",
        "",
    ],
    "api_usage": [
        " I'm building a {app_type}.",
        " I'm new to APIs in general.",
        " I've read the docs but I'm still confused.",
        " We're evaluating OpenAI vs other providers.",
        " I need this for a production application.",
        " I'm a student working on a project.",
        "",
        "",
    ],
    "chatgpt_product": [
        " I'm using {model}.",
        " This happens on {browser}.",
        " I tried refreshing the page multiple times.",
        " It was working fine earlier today.",
        " I uploaded a {file_type} and that's when it broke.",
        " This is happening in a long conversation thread.",
        " I have a {plan} subscription.",
        " Other users in my organization are seeing the same issue.",
        "",
        "",
        "",
    ],
    "chatgpt_apps": [
        " I'm on {device}.",
        " I'm running the latest version of the app.",
        " I've tried reinstalling but the problem persists.",
        " It works on web but not on the app.",
        " I'm running iOS {ios_version}.",
        " My device is fully updated.",
        "",
        "",
    ],
    "enterprise": [
        " We have {team_size} users in our workspace.",
        " We're a {org_type}.",
        " Our IT team needs documentation for this.",
        " We're on the {plan} plan.",
        " This is blocking our rollout to the organization.",
        " We need this for compliance reasons.",
        "",
        "",
    ],
    "gpts": [
        " I've published {gpt_count} GPTs before without issues.",
        " The GPT uses {file_count} knowledge files.",
        " I've tested the API endpoint separately and it works.",
        " The GPT was working before the latest platform update.",
        "",
        "",
    ],
    "newer_products": [
        " I'm on the {plan} plan.",
        " This is my first time using this product.",
        " The error happens consistently, not intermittently.",
        " I've tried with different inputs and same result.",
        "",
        "",
    ],
    "privacy_policy": [
        " I'm asking on behalf of my organization.",
        " We're in the {industry} industry with compliance requirements.",
        " I need a clear answer for our legal team.",
        " GDPR requires us to understand this.",
        "",
        "",
    ],
    "security": [
        " I've already rotated the key.",
        " The unauthorized usage happened {timeframe}.",
        " We noticed unusual charges first.",
        " Our security team flagged this.",
        "",
        "",
    ],
}

# --- Context suffixes (optional, add realism) ---

CONTEXT_SUFFIXES = [
    " Thanks in advance.",
    " Please help.",
    " Any help would be appreciated.",
    " Let me know if you need more details.",
    " Thanks!",
    " I appreciate any guidance.",
    " Can someone look into this?",
    " What are my options?",
    " Please advise.",
    " Hoping for a quick resolution.",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
]

# --- Tone / urgency modifiers ---

URGENT_PREFIXES = [
    "URGENT: ",
    "HELP! ",
    "This is extremely frustrating. ",
    "I've been waiting for days with no response. ",
    "This is blocking my production system. ",
    "I've already contacted support 3 times about this. ",
    "I need immediate assistance. ",
    "This is a critical issue for my business. ",
    "PLEASE HELP — ",
    "I'm losing money every hour this isn't fixed. ",
    "This has been going on for over a week now. ",
    "I'm extremely disappointed with the support so far. ",
]

CASUAL_PREFIXES = [
    "Quick question: ",
    "Hi, ",
    "Hello, ",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
]

# --- Category definitions (massively expanded templates) ---

CATEGORIES = {
    "billing": {
        "weight": 0.16,
        "description": "Refunds, charges, payment methods, invoices, credits",
        "templates": [
            # high — unauthorized/unexpected charges, money at stake
            ("I was charged ${amount} but I didn't authorize this purchase", "high"),
            ("I was charged for {plan} but I cancelled {timeframe}", "high"),
            ("There are unauthorized charges on my account from OpenAI", "high"),
            ("I'm being double charged for my {plan} subscription", "high"),
            ("I was charged ${amount} for API usage that I don't recognize", "high"),
            ("I was charged ${amount} after a free trial I didn't sign up for", "high"),
            ("I got charged twice because the page refreshed during checkout", "high"),
            ("My API credits disappeared after I updated my payment method", "high"),
            ("My prepaid credits aren't showing up in my account", "high"),
            ("The pricing page says ${amount}/month but I was charged more", "high"),
            # medium — issues that need resolution but aren't urgent
            ("How do I request a refund for my {plan} subscription?", "medium"),
            ("My credit card was declined when trying to upgrade to {plan}", "medium"),
            ("I see a $5 charge after updating my payment method, is this a hold?", "medium"),
            ("Why did my {plan} renewal transaction fail?", "medium"),
            ("My subscription says it's associated with another account", "medium"),
            ("My invoice shows charges from a currency I didn't select", "medium"),
            ("I set up autopay but my card was still charged manually", "medium"),
            ("The billing dashboard shows different amounts than my bank statement", "medium"),
            ("I accidentally purchased API credits when I meant to subscribe to {plan}", "medium"),
            ("My company credit card was replaced, how do I update it?", "medium"),
            # low — informational, how-to, administrative
            ("Can you extend my API credits? They expire {timeframe}", "low"),
            ("How do I change the billing details on my invoice?", "low"),
            ("I need a U.S. sales tax exemption for my organization", "low"),
            ("I want to set up prepaid billing for my API usage", "low"),
            ("How can I find my past invoices?", "low"),
            ("How do I delete my payment method?", "low"),
            ("Can I move my ChatGPT subscription to the API billing?", "low"),
            ("I need to update my VAT ID on my account", "low"),
            ("How do I export my monthly API usage details for accounting?", "low"),
            ("How do I downgrade from {plan} to a lower tier?", "low"),
            ("How do I switch from monthly to annual billing?", "low"),
            ("I received a Japanese Consumption Tax charge, is this correct?", "low"),
            ("Can I get a receipt instead of a full invoice?", "low"),
            ("I'm being charged in USD but I'm in the EU, can I pay in EUR?", "low"),
            ("How do I add a backup payment method?", "low"),
            ("My organization needs NET 30 payment terms", "low"),
            ("How do I get a refund for unused API credits?", "medium"),
            ("I need a W-9 from OpenAI for our vendor registration", "low"),
            ("How do I cancel auto-renewal but keep access until the end of my billing period?", "low"),
            ("I need an invoice broken down by project for internal cost allocation", "low"),
        ],
    },
    "account_access": {
        "weight": 0.14,
        "description": "Login issues, password reset, account recovery, phone verification",
        "templates": [
            # high — locked out, can't work
            ("I can't log in to my account after resetting my password", "high"),
            ("My account was deactivated and I need to reactivate it", "high"),
            ("My account says it was deleted or deactivated but I never did that", "high"),
            ("My account was locked after too many failed password attempts", "high"),
            ("I set up my account with a work email that I no longer have access to", "high"),
            ("My account is stuck in a verification loop", "high"),
            ("I'm getting a 'Suspicious Activity Alert' when trying to sign in", "high"),
            ("I got a verification email I didn't request, is my account compromised?", "high"),
            ("I keep getting redirected to the login page after signing in successfully", "high"),
            ("My 2FA codes from my authenticator app aren't being accepted", "high"),
            # medium — access issues but workarounds exist
            ("I'm traveling to {country} and can't access ChatGPT", "medium"),
            ("Something went wrong with DeviceCheckError when I try to log in", "medium"),
            ("I can't sign up because it says 'unsupported country'", "medium"),
            ("I deleted my account but now I want it back", "medium"),
            ("I can't log in to the API Platform, it just shows a blank page", "medium"),
            ("The passkey I set up isn't working on my new device", "medium"),
            ("My VPN is blocking my access to ChatGPT", "medium"),
            ("I changed my email provider and now I can't log in with my old email", "medium"),
            ("Phone verification keeps saying my number is already in use", "medium"),
            ("I'm getting 'too many login attempts' but I only tried once", "medium"),
            ("SSO login works for my team but not for me specifically", "medium"),
            ("I can sign in on mobile but web keeps saying invalid credentials", "medium"),
            ("I'm in {country} and getting a region restriction error", "medium"),
            ("I'm getting a blank screen after the Google OAuth redirect", "medium"),
            ("My session keeps expiring every few minutes", "medium"),
            ("I can't complete age verification, the system rejects my ID", "medium"),
            ("The password reset link expired before I could use it", "medium"),
            ("I signed up with Apple ID and now I can't use the web version", "medium"),
            ("The 'Continue with Apple' sign-in option disappeared", "medium"),
            ("WhatsApp verification is not available in my country", "medium"),
            # low — informational
            ("Why am I being asked to verify my login every time?", "low"),
            ("Can I use a Google Voice number for phone verification?", "low"),
            ("How do I change the phone number on my account?", "low"),
            ("I want to change my sign-in method from Google to email/password", "low"),
            ("I'm getting CAPTCHAs every time I try to use ChatGPT", "low"),
            ("How do I enable MFA on my account?", "low"),
        ],
    },
    "account_management": {
        "weight": 0.08,
        "description": "Members, orgs, projects, security, email changes",
        "templates": [
            # high — security or access concerns
            ("I think someone else has access to my account, how do I secure it?", "high"),
            ("How do I report suspicious activity on my account?", "high"),
            ("I accidentally deleted a team member, can I undo this?", "high"),
            # medium — needs action but not urgent
            ("I need to change the email address on my account", "medium"),
            ("Can I transfer ownership of my API organization?", "medium"),
            ("I want to remove a team member from my API account", "medium"),
            ("I need to verify my domain for my organization", "medium"),
            ("I need to stop my API subscription entirely", "medium"),
            ("I need to be removed from an API organization I no longer belong to", "medium"),
            ("I need to revoke API access for a contractor whose engagement ended", "medium"),
            ("I need to change the owner of our API organization", "medium"),
            ("Can I move my personal API usage to my company's organization?", "medium"),
            ("I need to update our company email domain across all accounts", "medium"),
            # low — how-to, informational
            ("How do I add a new member to my API organization?", "low"),
            ("How do I change my default organization?", "low"),
            ("How can I change my API platform's org name?", "low"),
            ("How do I manage projects in the API platform?", "low"),
            ("How do I change my display name?", "low"),
            ("What roles and permissions can I assign to team members?", "low"),
            ("How do I merge two OpenAI accounts?", "low"),
            ("How do I create separate projects for different clients in the API platform?", "low"),
            ("How do I set up a shared billing account for my team?", "low"),
            ("How do I set usage limits per team member?", "low"),
            ("We need separate API keys for development and production", "low"),
            ("How do I set up a new organization for a different department?", "low"),
            ("Can I restrict which models certain team members can access?", "low"),
            ("How do I view the audit log for my organization?", "low"),
            ("I want to archive old projects without deleting them", "low"),
        ],
    },
    "api_errors": {
        "weight": 0.12,
        "description": "Rate limits, 429 errors, API key issues, latency, error codes",
        "templates": [
            # high — production systems affected
            ("I keep getting 429 Too Many Requests errors even though I'm under my rate limit", "high"),
            ("My API calls are returning 500 errors intermittently", "high"),
            ("My API requests are hanging for 30+ seconds before timing out", "high"),
            ("Getting error {error_code} on every request to the {model} model", "high"),
            ("The API is truncating my output at exactly 4096 tokens even though I set a higher max", "high"),
            ("Connection reset errors when sending large batch requests", "high"),
            ("The {model} model is not available for my organization despite being on the right tier", "high"),
            ("My fine-tuning job failed with no clear error message", "high"),
            # medium — broken but not production-critical
            ("My API key is showing as incorrect but I copied it directly", "medium"),
            ("I'm getting rate limit errors on the Assistants API despite being below my quota", "medium"),
            ("The API response latency has been very high for the past {timeframe}", "medium"),
            ("I hit my file storage quota for assistants, how do I fix this?", "medium"),
            ("I reached my usage limit but I thought I had more credits", "medium"),
            ("The Playground outputs are being flagged as unsafe incorrectly", "medium"),
            ("Embeddings API is returning different dimensions than expected", "medium"),
            ("I'm getting timeout errors on long Chat Completions requests", "medium"),
            ("The Batch API keeps rejecting my input file format", "medium"),
            ("Function calling is returning malformed JSON in the response", "medium"),
            ("The streaming response cuts off mid-sentence randomly", "medium"),
            ("The Responses API is returning empty content blocks", "medium"),
            ("I'm getting a {error_code} error but the docs don't explain this code", "medium"),
            ("Token count in the response doesn't match what I see in the usage dashboard", "medium"),
            ("The vision API is rejecting my image with no error details", "medium"),
            ("My assistants keep losing their thread context mid-conversation", "medium"),
            ("The fine-tuning validation step fails but no errors in the data", "medium"),
            ("Audio API transcription returns empty text for valid audio files", "medium"),
            ("My structured output schema is being ignored by the model", "medium"),
            ("Logprobs are returning null even though I set the parameter", "medium"),
            ("My webhook for async completions never fires", "medium"),
            ("The moderation endpoint is flagging benign content as harmful", "medium"),
            ("Image generation via API returns blurry/low-quality results compared to ChatGPT", "medium"),
            # low — unexpected behavior, not blocking
            ("Why am I getting different completions in the Playground vs the API?", "low"),
            ("How do I solve 429 errors? I've tried exponential backoff", "low"),
            ("I'm getting inconsistent results with temperature=0", "low"),
            ("The API returns different token counts for the same prompt", "low"),
        ],
    },
    "api_usage": {
        "weight": 0.08,
        "description": "How-to, getting started, best practices, billing/usage dashboard",
        "templates": [
            # all low — informational / how-to questions
            ("How do I get started with the OpenAI API?", "low"),
            ("What's the difference between prompt tokens and completion tokens?", "low"),
            ("Where do I find my API key?", "low"),
            ("How can I use the Chat Completion API for my chatbot?", "low"),
            ("Are Playground tokens counted toward my usage?", "low"),
            ("How do I format my data for fine-tuning?", "low"),
            ("What are the best practices for prompt engineering with the API?", "low"),
            ("How do I check my token usage?", "low"),
            ("Can I use the API with non-English text?", "low"),
            ("How do I use stop sequences?", "low"),
            ("What's the difference between the Completions and Chat Completions API?", "low"),
            ("How do I use function calling in the API?", "low"),
            ("Is there an SLA for API latency?", "low"),
            ("How do I increase my rate limit tier?", "low"),
            ("How does the DALL-E 3 API work?", "low"),
            ("What are the rate limits for image generation?", "low"),
            ("How do I migrate from the Assistants API to the Responses API?", "low"),
            ("What's the best model for my use case: {model} vs {model}?", "low"),
            ("How do I count tokens before sending a request?", "low"),
            ("Can I use the API to build a product for commercial use?", "low"),
            ("How do I implement streaming responses?", "low"),
            ("What's the difference between system, user, and assistant messages?", "low"),
            ("How do I use the embeddings API for semantic search?", "low"),
            ("Can I fine-tune {model}?", "low"),
            ("What's the maximum context window for {model}?", "low"),
            ("How do I set up the Python SDK?", "low"),
            ("How do I use the Batch API for bulk processing?", "low"),
            ("What's the recommended way to handle long conversations that exceed the context window?", "low"),
            ("How do I evaluate the quality of my fine-tuned model?", "low"),
            ("Can I use the API for real-time voice applications?", "low"),
            ("How does priority processing work?", "low"),
            ("What data format does the Whisper API accept?", "low"),
            ("How do I set up webhooks for async API calls?", "low"),
            ("What's the difference between the moderation and safety APIs?", "low"),
            ("How do I use structured outputs with JSON schemas?", "low"),
            ("Can I deploy the API in a specific region for data residency?", "low"),
        ],
    },
    "chatgpt_product": {
        "weight": 0.15,
        "description": "ChatGPT features, errors, slow responses, image generation, search, memory",
        "templates": [
            # high — data loss, broken core functionality
            ("I lost all my chat history, where did it go?", "high"),
            ("My conversation was cut off and I can't continue it", "high"),
            ("I reached my usage cap but it shouldn't have reset yet", "high"),
            ("ChatGPT is refusing my request but there's nothing harmful about it", "high"),
            # medium — features not working correctly
            ("ChatGPT is taking forever to respond, it just shows the loading spinner", "medium"),
            ("The image generation in ChatGPT keeps failing with no error message", "medium"),
            ("Memory isn't working, it keeps forgetting things I told it", "medium"),
            ("Deep research gave me results with broken sources", "medium"),
            ("ChatGPT agent mode isn't browsing the web correctly", "medium"),
            ("ChatGPT image generation isn't producing what I describe in my prompt", "medium"),
            ("ChatGPT search is showing outdated information", "medium"),
            ("My temporary chat conversations are being saved when they shouldn't be", "medium"),
            ("The voice mode cuts off my sentences", "medium"),
            ("Study mode isn't asking me the right kind of questions", "medium"),
            ("File uploads keep failing with large {file_type}s", "medium"),
            ("ChatGPT gave me completely wrong information and cited fake sources", "medium"),
            ("The image editing feature makes weird artifacts around the edges", "medium"),
            ("ChatGPT keeps switching to a different model mid-conversation", "medium"),
            ("Tasks I set up in ChatGPT aren't running at the scheduled time", "medium"),
            ("I can't share my conversation because it says content policy violation", "medium"),
            ("ChatGPT is generating images in the wrong style", "medium"),
            ("The file I uploaded is stuck in 'processing' and never completes", "medium"),
            ("Deep research keeps running for hours and never finishes", "medium"),
            ("ChatGPT generated an image that looks nothing like what I described", "medium"),
            ("My custom instructions are being ignored in new conversations", "medium"),
            ("I can't switch between models, the dropdown is grayed out", "medium"),
            ("Voice mode keeps disconnecting after a few seconds", "medium"),
            ("The data analysis output has wrong calculations", "medium"),
            ("The conversation history search doesn't find my old chats", "medium"),
            ("ChatGPT is generating text in {language} when I asked in English", "medium"),
            ("The shopping search feature isn't showing prices for my region", "medium"),
            # low — how-to, settings, minor annoyances
            ("How do I use the canvas feature?", "low"),
            ("How do I create a shared link for my conversation?", "low"),
            ("How is memory different from custom instructions?", "low"),
            ("How do I use data analysis to upload and analyze a CSV?", "low"),
            ("How do I delete a shared link I already created?", "low"),
            ("How do I use projects in ChatGPT to organize my work?", "low"),
            ("How do credits work on the {plan} plan?", "low"),
            ("How do I make ChatGPT remember my coding preferences?", "low"),
            ("How do I archive conversations I want to keep but not see?", "low"),
            ("ChatGPT Pulse notifications are too frequent", "low"),
            ("How do I use ChatGPT for {language} translation?", "low"),
        ],
    },
    "chatgpt_apps": {
        "weight": 0.08,
        "description": "iOS, Android, macOS, Windows app issues, connected apps",
        "templates": [
            # high — app completely broken
            ("The ChatGPT iOS app crashes when I try to use voice mode", "high"),
            ("The Windows app won't open after the latest update", "high"),
            ("I subscribed through Google Play but ChatGPT shows me as free", "high"),
            ("I can't log in to the Android app with my Microsoft account", "high"),
            # medium — features broken, workarounds exist
            ("Chat history isn't syncing between web and the iOS app", "medium"),
            ("The macOS app screenshot tool isn't working on my monitor", "medium"),
            ("The {app_integration} integration isn't showing my data", "medium"),
            ("Haptic feedback stopped working on my {device}", "medium"),
            ("Connected apps keep disconnecting from ChatGPT", "medium"),
            ("The Chat Bar shortcut isn't launching on my Mac", "medium"),
            ("The iOS app keeps crashing when I try to upload a {file_type}", "medium"),
            ("The Android app uses too much battery in the background", "medium"),
            ("The macOS Chat Bar doesn't work with my keyboard shortcut app", "medium"),
            ("I can't sign in to the Windows app with my {plan} account", "medium"),
            ("The widget on iOS isn't loading conversations", "medium"),
            ("Voice mode in the iOS app has a 2-second delay before it starts listening", "medium"),
            ("The Android app doesn't support my language for voice input", "medium"),
            ("Files I upload on the app aren't visible on the web version", "medium"),
            ("The macOS app isn't appearing in my menu bar", "medium"),
            ("My {app_integration} connection shows 'requires re-authentication'", "medium"),
            ("The iPad app doesn't support Split View properly", "medium"),
            ("The Windows app installer fails with error code 0x80070005", "medium"),
            ("I can't copy text from conversations in the mobile app", "medium"),
            # low — how-to
            ("How do I cancel my subscription through the Apple App Store?", "low"),
            ("How do I get my subscription invoice from the App Store?", "low"),
            ("How do I connect {app_integration} to ChatGPT?", "low"),
            ("How do I use drag and drop on iPad?", "low"),
            ("The ChatGPT app isn't available on my Android version", "low"),
            ("How do I set up the VS Code extension with the macOS app?", "low"),
            ("How do I restore my subscription after reinstalling the iOS app?", "low"),
            ("How do I turn off notifications for the ChatGPT app?", "low"),
            ("How do I use the ChatGPT app with my {device}?", "low"),
        ],
    },
    "enterprise": {
        "weight": 0.06,
        "description": "Enterprise, Business, Edu workspace setup, SSO, SCIM, admin",
        "templates": [
            # high — blocking team access
            ("Our SAML SSO integration is returning error during login", "high"),
            ("Our Azure AD SCIM integration keeps deprovisioning users incorrectly", "high"),
            ("The admin console isn't loading for any of our admins", "high"),
            ("Our team's data controls aren't applying to new members", "high"),
            # medium — setup/config needs, not emergency
            ("How do I configure SSO for my ChatGPT Enterprise workspace?", "medium"),
            ("SCIM provisioning isn't syncing our user directory correctly", "medium"),
            ("How do I set up domain verification for my organization?", "medium"),
            ("How do I manage admin roles in my Enterprise workspace?", "medium"),
            ("Our Enterprise workspace analytics aren't updating", "medium"),
            ("How do I restrict which GPTs my team can access?", "medium"),
            ("I need to set up ChatGPT Edu for our university", "medium"),
            ("I need a BAA for HIPAA compliance with the API", "medium"),
            ("How do I bulk invite users to our Enterprise workspace?", "medium"),
            ("How do I set up Okta as our identity provider for Enterprise?", "medium"),
            ("How do I migrate our team from Business to Enterprise?", "medium"),
            ("I need to set up separate workspaces for different departments", "medium"),
            ("How do I configure data residency for our Enterprise workspace?", "medium"),
            ("Our Edu workspace needs to comply with FERPA, what controls exist?", "medium"),
            ("We need custom data retention policies for compliance", "medium"),
            ("How do I onboard {team_size} users simultaneously?", "medium"),
            ("Our Enterprise contract is up for renewal, who do I contact?", "medium"),
            # low — informational
            ("What's the difference between Enterprise and Business plans?", "low"),
            ("How does flexible pricing work for Enterprise?", "low"),
            ("How do I configure audit logs for my API organization?", "low"),
            ("How do I manage credits and spend controls for Business?", "low"),
            ("Can we restrict which features are available to different user groups?", "low"),
            ("Our IT team needs the list of IP ranges to allowlist", "low"),
            ("How do I export workspace usage analytics for our quarterly review?", "low"),
            ("Can I set different model access levels for different teams?", "low"),
            ("How do I set up ChatGPT Business for a team of {team_size}?", "low"),
        ],
    },
    "gpts": {
        "weight": 0.05,
        "description": "Custom GPT creation, publishing, configuration, actions, troubleshooting",
        "templates": [
            # high — GPT broken or removed
            ("My GPT was restricted from sharing and I want to appeal", "high"),
            ("My GPT was removed from the Store with no explanation", "high"),
            ("My GPT's actions stopped working after I updated the schema", "high"),
            # medium — not working as expected
            ("My custom GPT won't publish to the GPT Store", "medium"),
            ("The knowledge files I uploaded to my GPT aren't being used", "medium"),
            ("I built a GPT but it's not following the instructions I gave it", "medium"),
            ("My GPT keeps hallucinating instead of using the knowledge I provided", "medium"),
            ("My GPT's action schema is valid but the GPT says it can't connect", "medium"),
            ("Users report my GPT gives different answers than when I test it", "medium"),
            ("My GPT is using outdated information from the knowledge files", "medium"),
            ("The GPT builder preview doesn't match the published behavior", "medium"),
            ("I uploaded {file_count} files but only some are being searched", "medium"),
            ("My GPT action is timing out because the API is slow", "medium"),
            ("My GPT doesn't retain context between user sessions, how do I fix this?", "medium"),
            ("The GPT Store review process has been pending for weeks", "medium"),
            # low — how-to, setup
            ("How do I configure actions in my GPT to call an external API?", "low"),
            ("How do I share my GPT with just my workspace?", "low"),
            ("How do I add authentication to my GPT's API actions?", "low"),
            ("Can I see analytics for how many people use my GPT?", "low"),
            ("How do I add OAuth authentication for my GPT's actions?", "low"),
            ("How do I enroll in the GPT revenue sharing program?", "low"),
            ("How do I update my GPT without breaking existing shared links?", "low"),
            ("Can I restrict my GPT to only work within my organization?", "low"),
            ("How do I configure my GPT to handle multi-turn conversations better?", "low"),
        ],
    },
    "newer_products": {
        "weight": 0.04,
        "description": "Sora, Codex, ChatGPT Atlas — newer product issues",
        "templates": [
            # high — product completely failing
            ("Sora keeps failing to generate my video, no error shown", "high"),
            ("Codex is making incorrect code changes to my repository", "high"),
            ("The Codex agent made changes I didn't approve", "high"),
            ("The Codex agent has been running for 30 minutes with no progress", "high"),
            # medium — not working as expected
            ("Sora generated a video with visible artifacts and distortion", "medium"),
            ("Codex keeps timing out on large pull requests", "medium"),
            ("ChatGPT Atlas isn't rendering the page I'm trying to visit", "medium"),
            ("Sora won't generate videos with people in them, is this intended?", "medium"),
            ("Codex doesn't understand the codebase structure of my monorepo", "medium"),
            ("Atlas crashes when visiting sites that require JavaScript", "medium"),
            ("Codex is ignoring my coding standards and style guide", "medium"),
            ("Sora generated a video that doesn't match my prompt at all", "medium"),
            ("Atlas opened a link but the content doesn't match what I asked for", "medium"),
            ("Sora credit usage seems too high for short videos", "medium"),
            ("Codex created a PR but the tests are all failing", "medium"),
            ("Atlas isn't able to log in to sites on my behalf", "medium"),
            ("Sora takes over an hour for a simple 5-second clip", "medium"),
            ("Codex keeps suggesting deprecated dependencies", "medium"),
            # low — how-to
            ("How long should Sora take to generate a 10-second video?", "low"),
            ("How do I connect Codex to my GitHub repository?", "low"),
            ("How do I use Sora for image-to-video generation?", "low"),
            ("Atlas is blocked by my company's firewall, how do I allowlist it?", "low"),
            ("How do I give Sora more specific direction on camera angles?", "low"),
            ("How do I use Codex for code review instead of code writing?", "low"),
            ("How do I set up Codex with a private GitHub organization?", "low"),
            ("How do I use Atlas for research across multiple websites?", "low"),
        ],
    },
    "privacy_policy": {
        "weight": 0.03,
        "description": "Data privacy, training opt-out, data export, content policies",
        "templates": [
            # high — urgent privacy concern
            ("I shared sensitive information in a chat by accident, how do I delete it?", "high"),
            ("I want to delete my account and all associated data", "high"),
            ("I'm a GDPR data subject and I want to exercise my right to erasure", "high"),
            # medium — needs answer for compliance/business
            ("How do I opt out of my data being used for training?", "medium"),
            ("I want to export all my ChatGPT data", "medium"),
            ("My company's legal team needs your DPA signed", "medium"),
            ("We need to know if our data is used for training before we can adopt the API", "medium"),
            ("I need documentation about data handling for a vendor assessment", "medium"),
            ("Our organization requires SOC 2 compliance, does OpenAI have this?", "medium"),
            ("I want to know exactly what data OpenAI has about me", "medium"),
            ("How do I submit a CCPA request?", "medium"),
            ("I need to transfer my conversations to a new account", "medium"),
            # low — informational
            ("How is my data handled if I use the API vs ChatGPT?", "low"),
            ("Does OpenAI store my API inputs and outputs?", "low"),
            ("How do I report harmful content generated by ChatGPT?", "low"),
            ("What happens to my data after I delete my account?", "low"),
            ("Does disabling chat history stop model training on my data?", "low"),
            ("What data residency options are available for API customers?", "low"),
            ("How long does OpenAI retain API request data?", "low"),
            ("Does ChatGPT store the images I upload?", "low"),
            ("What certifications does OpenAI have for data security?", "low"),
            ("Does the model training opt-out apply to all my conversations retroactively?", "low"),
            ("Are voice conversations stored differently than text?", "low"),
            ("What data does the ChatGPT mobile app collect beyond conversations?", "low"),
        ],
    },
    "security": {
        "weight": 0.01,
        "description": "API key safety, vulnerability reporting, fraud",
        "templates": [
            # high — active security incident
            ("My API key was leaked and I need help securing my account immediately", "high"),
            ("Someone is using my API key and I'm getting charged", "high"),
            ("My API key was accidentally committed to a public GitHub repo", "high"),
            ("I'm seeing unauthorized usage on my API account", "high"),
            ("Someone from an unknown IP accessed my API organization", "high"),
            ("Our API key was exposed in a client-side application", "high"),
            # medium — security concern but not active incident
            ("I found a security vulnerability in the API, how do I report it?", "medium"),
            ("I shared my API key with a coworker and now I need to understand the security implications", "medium"),
            ("I need to do a security audit of all API keys in our organization", "medium"),
            ("How do I report a phishing attempt pretending to be OpenAI?", "medium"),
            ("I received a suspicious email asking for my API key", "medium"),
            # low — how-to, configuration
            ("How do I assign permissions to different API keys?", "low"),
            ("How do I incorporate a safety identifier in my API integration?", "low"),
            ("I need to restrict my API key to specific IP addresses", "low"),
            ("How do I set up key rotation for my production API keys?", "low"),
            ("How do I enable IP allowlisting for my API account?", "low"),
        ],
    },
}

# --- Ambiguous / multi-intent tickets (expanded) ---

AMBIGUOUS_TEMPLATES = [
    {"text": "I was charged twice AND my API key stopped working at the same time", "category": "billing", "secondary_category": "api_errors"},
    {"text": "I can't log in and when I finally got in my billing shows charges I didn't make", "category": "account_access", "secondary_category": "billing"},
    {"text": "ChatGPT keeps crashing on my phone and I lost my chat history", "category": "chatgpt_apps", "secondary_category": "chatgpt_product"},
    {"text": "My Enterprise SSO broke and now none of my team can access their GPTs", "category": "enterprise", "secondary_category": "gpts"},
    {"text": "Rate limit errors on the API and I think I'm being billed for the failed requests", "category": "api_errors", "secondary_category": "billing"},
    {"text": "I want to opt out of training but I also need to export my data first", "category": "privacy_policy", "secondary_category": "account_management"},
    {"text": "My custom GPT's API action is returning {error_code} errors", "category": "gpts", "secondary_category": "api_errors"},
    {"text": "Sora failed to generate and I still got charged credits for it", "category": "newer_products", "secondary_category": "billing"},
    {"text": "I changed my password and now the iOS app won't log in", "category": "account_access", "secondary_category": "chatgpt_apps"},
    {"text": "Memory keeps things I asked it to forget and I have privacy concerns", "category": "chatgpt_product", "secondary_category": "privacy_policy"},
    {"text": "My API key was leaked and someone ran up ${amount} in charges on my account", "category": "security", "secondary_category": "billing"},
    {"text": "Codex made changes to my repo and I can't figure out how to connect to my enterprise workspace", "category": "newer_products", "secondary_category": "enterprise"},
    {"text": "I need a refund AND I want to delete my account and all my data", "category": "billing", "secondary_category": "privacy_policy"},
    {"text": "I'm getting API errors and I think it's because my account was flagged for suspicious activity", "category": "api_errors", "secondary_category": "account_access"},
    {"text": "ChatGPT generated an image that violates content policy and now my GPT is restricted", "category": "chatgpt_product", "secondary_category": "gpts"},
    {"text": "Our Enterprise workspace billing is wrong and users can't access the API", "category": "enterprise", "secondary_category": "billing"},
    {"text": "The Android app logged me out and now I can't get back in with my phone number", "category": "chatgpt_apps", "secondary_category": "account_access"},
    {"text": "My fine-tuning job keeps failing and I'm being charged for the failed attempts", "category": "api_errors", "secondary_category": "billing"},
    {"text": "I need to transfer my GPTs to a new account because I'm changing my email", "category": "gpts", "secondary_category": "account_management"},
    {"text": "Sora isn't available in my country and Atlas won't browse sites in my language", "category": "newer_products", "secondary_category": "account_access"},
    {"text": "My team member was removed from the org but they still have an active API key", "category": "account_management", "secondary_category": "security"},
    {"text": "ChatGPT voice mode transcribes poorly and the app crashes when I switch to text", "category": "chatgpt_product", "secondary_category": "chatgpt_apps"},
    {"text": "I was told to contact sales for Enterprise pricing but nobody has responded and our free trial is expiring", "category": "enterprise", "secondary_category": "billing"},
    {"text": "I connected GitHub but Codex can't see my private repos and the connection keeps dropping", "category": "newer_products", "secondary_category": "chatgpt_apps"},
    {"text": "My GPT builder preview works but published version gives errors, and I think it's related to my rate limits", "category": "gpts", "secondary_category": "api_errors"},
    {"text": "I need to export my conversations before deleting my account for GDPR reasons", "category": "privacy_policy", "secondary_category": "account_access"},
    {"text": "The API key associated with my Enterprise org has unauthorized usage from an unknown IP", "category": "security", "secondary_category": "enterprise"},
    {"text": "I subscribed to {plan} through the iOS app but it's not showing on the web and I can't get a refund", "category": "chatgpt_apps", "secondary_category": "billing"},
    {"text": "ChatGPT search gives wrong results and I want to know how my search data is being used", "category": "chatgpt_product", "secondary_category": "privacy_policy"},
    {"text": "My account got hacked, they changed my email and password, and there are charges I didn't make", "category": "account_access", "secondary_category": "security"},
]

# --- Metadata distributions ---

CUSTOMER_TIERS = ["free", "plus", "pro", "go", "enterprise", "api_only"]
TIER_WEIGHTS = [0.30, 0.25, 0.10, 0.10, 0.10, 0.15]


@dataclass
class SupportTicket:
    id: int
    text: str
    category: str
    secondary_category: str | None
    customer_tier: str
    account_age_days: int
    previous_tickets: int
    is_ambiguous: bool
    urgency: str  # "low", "medium", "high"


def fill_template(template: str) -> str:
    """Fill template placeholders with random values."""
    result = template
    if "{plan}" in result:
        result = result.replace("{plan}", random.choice(PLANS), 1)
    if "{plan}" in result:  # handle second {plan} in same template
        result = result.replace("{plan}", random.choice(PLANS), 1)
    if "{country}" in result:
        result = result.replace("{country}", random.choice(COUNTRIES))
    if "{timeframe}" in result:
        result = result.replace("{timeframe}", random.choice(TIMEFRAMES))
    if "{amount}" in result:
        result = result.replace("{amount}", random.choice(AMOUNTS))
    if "{model}" in result:
        result = result.replace("{model}", random.choice(MODELS), 1)
    if "{model}" in result:
        result = result.replace("{model}", random.choice(MODELS), 1)
    if "{error_code}" in result:
        result = result.replace("{error_code}", random.choice(ERROR_CODES))
    if "{device}" in result:
        result = result.replace("{device}", random.choice(DEVICES))
    if "{browser}" in result:
        result = result.replace("{browser}", random.choice(BROWSERS), 1)
    if "{browser2}" in result:
        result = result.replace("{browser2}", random.choice(BROWSERS))
    if "{file_type}" in result:
        result = result.replace("{file_type}", random.choice(FILE_TYPES))
    if "{app_integration}" in result:
        result = result.replace("{app_integration}", random.choice(APP_INTEGRATIONS))
    if "{language}" in result:
        result = result.replace("{language}", random.choice(LANGUAGES))
    if "{team_size}" in result:
        result = result.replace("{team_size}", str(random.choice([5, 10, 15, 25, 50, 100, 200, 500, 1000])))
    if "{months}" in result:
        result = result.replace("{months}", str(random.randint(1, 36)))
    if "{pct}" in result:
        result = result.replace("{pct}", str(random.choice([10, 20, 30, 40, 50, 60, 70, 80])))
    if "{tier}" in result:
        result = result.replace("{tier}", str(random.choice([1, 2, 3, 4, 5])))
    if "{volume}" in result:
        result = result.replace("{volume}", str(random.choice([10, 50, 100, 500, 1000, 5000])))
    if "{app_type}" in result:
        result = result.replace("{app_type}", random.choice([
            "customer support chatbot", "coding assistant", "content generation tool",
            "data analysis pipeline", "document Q&A system", "language tutor",
            "sales assistant", "medical triage bot", "legal document analyzer",
        ]))
    if "{ios_version}" in result:
        result = result.replace("{ios_version}", random.choice(["16", "17", "17.5", "18", "18.1"]))
    if "{org_type}" in result:
        result = result.replace("{org_type}", random.choice([
            "Fortune 500 company", "university", "startup", "government agency",
            "healthcare provider", "law firm", "consulting firm", "nonprofit",
        ]))
    if "{industry}" in result:
        result = result.replace("{industry}", random.choice([
            "healthcare", "financial services", "education", "legal",
            "government", "defense", "pharmaceutical", "insurance",
        ]))
    if "{file_count}" in result:
        result = result.replace("{file_count}", str(random.choice([3, 5, 10, 15, 20, 50])))
    if "{gpt_count}" in result:
        result = result.replace("{gpt_count}", str(random.choice([2, 3, 5, 8, 10])))
    return result


def generate_ticket(ticket_id: int, force_ambiguous: bool = False) -> SupportTicket:
    """Generate a single synthetic support ticket with compositional variation."""
    is_ambiguous = force_ambiguous or random.random() < 0.10

    if is_ambiguous:
        ambig = random.choice(AMBIGUOUS_TEMPLATES)
        text = fill_template(ambig["text"])
        category = ambig["category"]
        secondary_category = ambig["secondary_category"]
        # Ambiguous tickets are medium-high urgency (they're inherently complex)
        urgency = random.choice(["medium", "high"])
    else:
        # Pick category by weight
        categories = list(CATEGORIES.keys())
        weights = [CATEGORIES[c]["weight"] for c in categories]
        category = random.choices(categories, weights=weights, k=1)[0]
        template_text, urgency = random.choice(CATEGORIES[category]["templates"])
        text = fill_template(template_text)
        secondary_category = None

    # Compositional variation: add detail fragment (60% of tickets)
    if random.random() < 0.60:
        detail = random.choice(DETAIL_FRAGMENTS.get(category, [""]))
        detail = fill_template(detail)
        text += detail

    # Add context suffix (40% of tickets)
    if random.random() < 0.40:
        text += random.choice(CONTEXT_SUFFIXES)

    # Add tone prefix — only urgent prefixes for high urgency, casual for low
    if urgency == "high" and random.random() < 0.40:
        text = random.choice(URGENT_PREFIXES) + text
    elif urgency == "low" and random.random() < 0.25:
        text = random.choice(CASUAL_PREFIXES) + text

    # Metadata
    customer_tier = random.choices(CUSTOMER_TIERS, weights=TIER_WEIGHTS, k=1)[0]
    account_age_days = int(random.gammavariate(2, 180))
    previous_tickets = int(random.expovariate(0.5))

    return SupportTicket(
        id=ticket_id,
        text=text.strip(),
        category=category,
        secondary_category=secondary_category,
        customer_tier=customer_tier,
        account_age_days=min(account_age_days, 1500),
        previous_tickets=min(previous_tickets, 20),
        is_ambiguous=is_ambiguous,
        urgency=urgency,
    )


def generate_dataset(n: int = 100_000) -> list[dict]:
    """Generate full dataset of n tickets."""
    tickets = []
    for i in range(n):
        ticket = generate_ticket(ticket_id=i + 1)
        tickets.append(asdict(ticket))
    return tickets


def get_category_stats(tickets: list[dict]) -> dict:
    """Compute category distribution statistics."""
    from collections import Counter

    counts = Counter(t["category"] for t in tickets)
    total = len(tickets)
    stats = {}
    for cat, count in counts.most_common():
        stats[cat] = {
            "count": count,
            "percentage": round(count / total * 100, 1),
            "description": CATEGORIES[cat]["description"],
        }
    return stats


def main():
    n = 100_000
    print(f"Generating {n:,} synthetic support tickets...")
    tickets = generate_dataset(n)

    # Stats
    stats = get_category_stats(tickets)
    print("\nCategory distribution:")
    for cat, info in stats.items():
        print(f"  {cat:25s} {info['count']:6d}  ({info['percentage']}%)")

    ambiguous_count = sum(1 for t in tickets if t["is_ambiguous"])
    print(f"\nAmbiguous tickets: {ambiguous_count:,} ({ambiguous_count/len(tickets)*100:.1f}%)")

    # Check unique ticket texts
    unique_texts = len(set(t["text"] for t in tickets))
    print(f"Unique ticket texts: {unique_texts:,} / {len(tickets):,} ({unique_texts/len(tickets)*100:.1f}%)")

    # Export
    output_dir = Path(__file__).parent.parent.parent / "app" / "public" / "data"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Full dataset (for Python modeling, not loaded by frontend)
    with open(output_dir / "tickets.json", "w") as f:
        json.dump(tickets, f)
    size_mb = (output_dir / "tickets.json").stat().st_size / 1024 / 1024
    print(f"\nExported to {output_dir / 'tickets.json'} ({size_mb:.1f} MB)")

    # Sample for frontend (1000 tickets for interactive explorer)
    sample = random.sample(tickets, 1000)
    with open(output_dir / "tickets_sample.json", "w") as f:
        json.dump(sample, f, indent=2)
    print(f"Exported sample to {output_dir / 'tickets_sample.json'}")

    with open(output_dir / "category_stats.json", "w") as f:
        json.dump(stats, f, indent=2)
    print(f"Exported stats to {output_dir / 'category_stats.json'}")


if __name__ == "__main__":
    main()
