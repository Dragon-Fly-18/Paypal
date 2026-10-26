"""Verified, general PayPal India guidance used by the assistant.

Reviewed against the linked official PayPal pages on 2026-10-26. Keep answers
general: this application cannot inspect an account or make a KYC decision.
"""

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
        "verified_on": "2026-10-26",
    },
    {
        "topic": "Merchant onboarding",
        "keywords": (
            "merchant onboarding",
            "merchant setup",
            "business account",
            "business type",
            "nature of business",
            "start selling",
            "iec",
            "export goods",
        ),
        "answer": (
            "For merchant onboarding in India, confirm the email address and complete "
            "the identity steps shown for your business type. PayPal's receiving-payments "
            "guidance also says international-payment preparation can include PAN "
            "verification, an Indian bank account, a purpose code, and business details. "
            "Exporters of goods may be asked for a valid IEC. Follow the requirements "
            "shown in your own PayPal account because they can differ by business type."
        ),
        "source_title": "PayPal India: How do I receive payments?",
        "source_url": (
            "https://www.paypal.com/in/cshelp/article/"
            "how-do-i-receive-payments-through-paypal-HELP667"
        ),
        "verified_on": "2026-10-26",
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
        "verified_on": "2026-10-26",
    },
    {
        "topic": "Confirming a bank account",
        "keywords": (
            "confirm bank",
            "confirm my bank",
            "bank verification",
            "penny drop",
            "cancelled cheque",
            "bank statement",
            "ifsc",
        ),
        "answer": (
            "PayPal India says it may confirm that a bank account is active and belongs "
            "to you through a small test deposit. If that check does not succeed, follow "
            "the instructions in your PayPal account; you may be asked for a recent bank "
            "statement or cancelled cheque showing the requested account details. Do not "
            "enter bank account numbers in this prototype."
        ),
        "source_title": "PayPal India: How do I confirm my bank account?",
        "source_url": (
            "https://www.paypal.com/in/cshelp/article/"
            "how-do-i-confirm-my-bank-account-with-paypal-help185"
        ),
        "verified_on": "2026-10-26",
    },
    {
        "topic": "Domestic payments in India",
        "keywords": (
            "domestic payment",
            "domestic payments",
            "indian customer",
            "indian customers",
            "india customer",
            "local payment",
            "local payments",
        ),
        "answer": (
            "PayPal India's help page says PayPal cannot be used to receive domestic "
            "payments from Indian customers. Check the official page for the current "
            "scope of supported international payments."
        ),
        "source_title": "PayPal India: Receiving payments from Indian customers",
        "source_url": (
            "https://www.paypal.com/in/cshelp/article/"
            "can-i-use-paypal-to-receive-payments-from-indian-customers-help1049"
        ),
        "verified_on": "2026-10-26",
    },
    {
        "topic": "Common verification problems",
        "keywords": (
            "verification delayed",
            "verification pending",
            "verification failed",
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
        "verified_on": "2026-10-26",
    },
    {
        "topic": "Account limitations",
        "keywords": (
            "account limited",
            "account limitation",
            "limited account",
            "remove limitation",
            "resolution centre",
            "resolution center",
            "restricted account",
        ),
        "answer": (
            "For an account limitation, open the Resolution Centre or the notification "
            "in your PayPal account and complete the steps shown there. The reason and "
            "review time depend on the specific account, so this assistant cannot tell "
            "whether an account is limited, why it was limited, or when access will be "
            "restored."
        ),
        "source_title": "PayPal India: How do I remove an account limitation?",
        "source_url": (
            "https://www.paypal.com/in/cshelp/article/"
            "how-do-i-remove-a-limitation-from-my-account-help535"
        ),
        "verified_on": "2026-10-26",
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
        "verified_on": "2026-10-26",
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
        # Longer phrases carry more weight than generic words such as "payment".
        # This keeps specific questions (for example, domestic payments) from being
        # swallowed by a broader topic (receiving payments).
        score = sum(
            len(keyword)
            for keyword in entry["keywords"]
            if keyword in normalized_question
        )
        if score:
            scored.append((score, entry))
    scored.sort(key=lambda item: item[0], reverse=True)
    return [entry for _, entry in scored[:limit]]


def find_guidance(question: str) -> dict | None:
    """Return the best keyword match without storing the submitted question."""
    matches = search_guidance(question, limit=1)
    return matches[0] if matches else None
