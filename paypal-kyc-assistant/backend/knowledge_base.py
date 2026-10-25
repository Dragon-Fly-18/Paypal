"""Verified, general PayPal India guidance used by the assistant."""

KNOWLEDGE_BASE = [
    {
        "topic": "Identity verification",
        "keywords": (
            "identity",
            "verify",
            "verification",
            "document",
            "documents",
            "confirm",
            "kyc",
            "pan",
            "aadhaar",
        ),
        "answer": (
            "Follow the identity-verification instructions and notifications in "
            "your PayPal account. PayPal India says the process can include identity "
            "documents and a video verification call. Make sure account details match "
            "your documents and submit information only through official PayPal flows."
        ),
        "source_title": "PayPal India: How do I confirm my identity?",
        "source_url": (
            "https://www.paypal.com/in/cshelp/article/"
            "how-do-i-confirm-my-identity--help606"
        ),
    },
    {
        "topic": "Receiving payments",
        "keywords": (
            "receive",
            "receiving",
            "payment",
            "payments",
            "money",
            "withdraw",
            "withdrawal",
            "accept",
        ),
        "answer": (
            "PayPal India says merchants generally need to confirm their email and "
            "identity before receiving and withdrawing payments. For international "
            "payments, check the current requirements shown in your account, including "
            "PAN verification, an Indian bank account, and a purpose code where required."
        ),
        "source_title": "PayPal India: How do I receive payments?",
        "source_url": (
            "https://www.paypal.com/in/cshelp/article/"
            "how-do-i-receive-payments-through-paypal-HELP667"
        ),
    },
    {
        "topic": "Common verification problems",
        "keywords": (
            "delay",
            "delayed",
            "problem",
            "issue",
            "error",
            "failed",
            "failure",
            "stuck",
            "pending",
            "rejected",
        ),
        "answer": (
            "Verification may need more time when information is incomplete, unclear, "
            "or does not match. Check PayPal account notifications, confirm that requested "
            "documents are legible and current, and contact official PayPal support if the "
            "requested step still cannot be completed."
        ),
        "source_title": "PayPal India: Identity confirmation help",
        "source_url": (
            "https://www.paypal.com/in/cshelp/article/"
            "how-do-i-confirm-my-identity--help606"
        ),
    },
    {
        "topic": "PayPal Sandbox",
        "keywords": (
            "sandbox", "developer", "api", "checkout", "order", "integration",
        ),
        "answer": (
            "PayPal Sandbox is a developer test environment for payment integrations. "
            "Sandbox orders do not represent live payments and do not verify or approve "
            "a merchant's KYC status."
        ),
        "source_title": "PayPal Developer: Make REST API requests",
        "source_url": "https://developer.paypal.com/api/make-api-requests/",
    },
]

NO_MATCH_RESPONSE = (
    "I do not have a verified guidance answer for that question yet. "
    "Please check official PayPal Help for account-specific information."
)


def search_guidance(question: str, limit: int = 3) -> list[dict]:
    """Return relevant entries ordered by keyword score."""
    normalized_question = question.casefold()
    scored = []
    for entry in KNOWLEDGE_BASE:
        score = sum(keyword in normalized_question for keyword in entry["keywords"])
        if score:
            scored.append((score, entry))
    scored.sort(key=lambda item: item[0], reverse=True)
    return [entry for _, entry in scored[:limit]]


def find_guidance(question: str) -> dict | None:
    """Return the best keyword match without storing the submitted question."""
    matches = search_guidance(question, limit=1)
    return matches[0] if matches else None
