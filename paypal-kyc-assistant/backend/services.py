"""External-service and privacy helpers for the PayReady prototype."""

import json
import os
import re
from typing import Any

from knowledge_base import NO_MATCH_RESPONSE, search_guidance

PAYPAL_SANDBOX_BASE_URL = "https://api-m.sandbox.paypal.com"
SENSITIVE_PATTERNS = (
    re.compile(r"\b\d{12}\b"),
    re.compile(r"\b[A-Z]{5}\d{4}[A-Z]\b", re.IGNORECASE),
    re.compile(r"\b(?:password|passcode|otp|pin)\s*[:=]\s*\S+", re.IGNORECASE),
)


class SandboxIntegrationError(RuntimeError):
    """Safe public boundary for PayPal Sandbox dependency or request failures."""


def contains_sensitive_data(value: str) -> bool:
    return any(pattern.search(value) for pattern in SENSITIVE_PATTERNS)


def answer_with_verified_context(question: str) -> dict[str, Any]:
    """Use Gemini when configured, otherwise return deterministic local guidance."""
    entries = search_guidance(question)
    sources = []
    seen_urls = set()
    for entry in entries:
        if entry["source_url"] not in seen_urls:
            sources.append({"title": entry["source_title"], "url": entry["source_url"]})
            seen_urls.add(entry["source_url"])
    fallback = entries[0]["answer"] if entries else NO_MATCH_RESPONSE
    api_key = os.getenv("GEMINI_API_KEY", "").strip()

    if not api_key or not entries:
        return {
            "answer": fallback,
            "matched": bool(entries),
            "provider": "verified-knowledge-base",
            "topic": entries[0]["topic"] if entries else None,
            "sources": sources or [{
                "title": "PayPal India Help",
                "url": "https://www.paypal.com/in/cshelp/home",
            }],
        }

    try:
        from google import genai

        context = "\n\n".join(
            f"Topic: {entry['topic']}\nGuidance: {entry['answer']}\nSource: {entry['source_url']}"
            for entry in entries
        )
        prompt = (
            "You are a PayPal India KYC readiness guide. Answer only from the verified "
            "context below. Do not claim access to an account, approval authority, or a "
            "live KYC decision. Do not ask for passwords, PAN/Aadhaar numbers, or document "
            "images. Keep the answer below 120 words and direct the user to the sources.\n\n"
            f"Verified context:\n{context}\n\nQuestion: {question}"
        )
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
            contents=prompt,
        )
        answer = (response.text or "").strip()
        if answer:
            return {
                "answer": answer,
                "matched": True,
                "provider": "gemini-grounded",
                "topic": entries[0]["topic"],
                "sources": sources,
            }
    except Exception:
        pass

    return {
        "answer": fallback,
        "matched": True,
        "provider": "verified-knowledge-base-fallback",
        "topic": entries[0]["topic"],
        "sources": sources,
    }


def review_sample_document(
    document_type: str,
    sample_text: str,
    image_quality: int,
) -> dict[str, Any]:
    """Review synthetic/redacted text without retaining it or making a KYC decision."""
    fields: dict[str, str] = {}
    for key, value in re.findall(
        r"(?im)^\s*([a-z][a-z ]{1,30})\s*:\s*([^\n]{1,100})$",
        sample_text,
    ):
        fields[key.strip().lower().replace(" ", "_")] = value.strip()

    expected = {
        "identity": ("name", "date_of_birth", "expiry_date"),
        "business": ("business_name", "registration_type", "address"),
        "address": ("name", "address", "issue_date"),
    }[document_type]
    missing = [field for field in expected if not fields.get(field)]
    issues = []
    if image_quality < 60:
        issues.append("The sample is marked as difficult to read.")
    if missing:
        issues.append("Expected sample fields are missing: " + ", ".join(missing) + ".")

    return {
        "document_type": document_type,
        "extracted_fields": fields,
        "missing_fields": missing,
        "readability": "clear" if image_quality >= 60 else "needs-review",
        "issues": issues,
        "result": "sample-ready" if not issues else "sample-needs-attention",
        "recommendation": (
            "The redacted sample contains the expected fields and is readable. Confirm "
            "current requirements in your PayPal account before submitting a real document."
            if not issues else
            "Improve the synthetic/redacted sample and review official PayPal guidance. "
            "Do not upload a real identity document to this prototype."
        ),
        "disclaimer": "Simulated document review only; this is not PayPal KYC approval.",
    }


def paypal_sandbox_configured() -> bool:
    return bool(
        os.getenv("PAYPAL_SANDBOX_CLIENT_ID", "").strip()
        and os.getenv("PAYPAL_SANDBOX_CLIENT_SECRET", "").strip()
    )


def create_paypal_sandbox_order(amount: str, currency: str) -> dict[str, Any]:
    """Create an order against the Sandbox host only; secrets never reach the browser."""
    client_id = os.getenv("PAYPAL_SANDBOX_CLIENT_ID", "").strip()
    client_secret = os.getenv("PAYPAL_SANDBOX_CLIENT_SECRET", "").strip()
    if not client_id or not client_secret:
        raise SandboxIntegrationError("PayPal Sandbox credentials are not configured.")

    try:
        import httpx
    except ImportError as error:
        raise SandboxIntegrationError(
            "The optional PayPal Sandbox dependency is not installed."
        ) from error

    try:
        with httpx.Client(timeout=15.0) as client:
            token_response = client.post(
                f"{PAYPAL_SANDBOX_BASE_URL}/v1/oauth2/token",
                data={"grant_type": "client_credentials"},
                auth=(client_id, client_secret),
                headers={"Accept": "application/json"},
            )
            token_response.raise_for_status()
            access_token = token_response.json()["access_token"]
            order_response = client.post(
                f"{PAYPAL_SANDBOX_BASE_URL}/v2/checkout/orders",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json",
                    "PayPal-Request-Id": os.urandom(12).hex(),
                },
                content=json.dumps({
                    "intent": "CAPTURE",
                    "purchase_units": [{
                        "amount": {"currency_code": currency, "value": amount},
                        "description": "PayReady Sandbox demonstration",
                    }],
                }),
            )
            order_response.raise_for_status()
            order = order_response.json()
    except (httpx.HTTPError, KeyError) as error:
        raise SandboxIntegrationError("PayPal Sandbox request failed.") from error

    approve_url = next(
        (link["href"] for link in order.get("links", []) if link.get("rel") == "approve"),
        None,
    )
    return {
        "id": order["id"],
        "status": order["status"],
        "approve_url": approve_url,
        "environment": "sandbox",
        "disclaimer": "Sandbox payment demonstration only; unrelated to KYC approval.",
    }
