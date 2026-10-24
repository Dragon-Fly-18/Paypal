"""General PayPal India guidance used by the first assistant implementation."""

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
            "PayPal may ask you to confirm information about your identity or "
            "business. Review the instructions shown in your PayPal account and "
            "provide only the information requested through official PayPal "
            "channels. Requirements can vary by account and may change."
        ),
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
            "To prepare to receive payments, complete the account steps shown "
            "in your PayPal account and check that your account information is "
            "current. Payment availability, holds, and withdrawal options "
            "depend on your account and applicable regulations."
        ),
        "source_url": (
            "https://www.paypal.com/in/webapps/mpp/accept-payments-online"
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
            "Verification can take longer when information is incomplete, "
            "does not match, or requires additional review. Check your account "
            "notifications, follow the exact requested next step, and contact "
            "PayPal through its official Help or Support channels if the issue "
            "continues. This assistant cannot inspect or decide your account "
            "verification status."
        ),
        "source_url": (
            "https://www.paypal.com/in/cshelp/contact-us"
        ),
    },
]

NO_MATCH_RESPONSE = (
    "I do not have a relevant general guidance answer for that question yet. "
    "Please check official PayPal Help for account-specific information."
)


def find_guidance(question: str) -> dict | None:
    """Return the best keyword match without storing the submitted question."""
    normalized_question = question.casefold()
    matches = [
        entry
        for entry in KNOWLEDGE_BASE
        if any(keyword in normalized_question for keyword in entry["keywords"])
    ]
    if not matches:
        return None
    return max(
        matches,
        key=lambda entry: sum(
            keyword in normalized_question for keyword in entry["keywords"]
        ),
    )
