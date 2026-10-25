import os
from enum import Enum

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator

from services import (
    answer_with_verified_context,
    contains_sensitive_data,
    create_paypal_sandbox_order,
    paypal_sandbox_configured,
    review_sample_document,
    SandboxIntegrationError,
)

load_dotenv()

app = FastAPI(
    title="PayPal India Merchant Readiness Assistant",
    description="A privacy-conscious readiness demonstration, not a PayPal KYC service.",
    version="1.0.0",
)

allowed_origins = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173",
    ).split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


class AccountType(str, Enum):
    personal = "personal"
    business = "business"


class AssistantRequest(BaseModel):
    question: str = Field(min_length=2, max_length=500)

    @field_validator("question")
    @classmethod
    def reject_sensitive_values(cls, value: str) -> str:
        value = value.strip()
        if contains_sensitive_data(value):
            raise ValueError(
                "Remove passwords, OTPs, PAN/Aadhaar numbers, and other sensitive values."
            )
        return value


class ReadinessAnswers(BaseModel):
    account_info_matches: bool = False
    email_confirmed: bool = False
    pan_ready: bool = False
    bank_added: bool = False
    purpose_code_selected: bool = False
    video_kyc_ready: bool = False
    address_complete: bool = False
    business_documents_ready: bool = False


class ReadinessEvaluationRequest(BaseModel):
    account_type: AccountType
    answers: ReadinessAnswers


class DocumentReviewRequest(BaseModel):
    document_type: str = Field(pattern="^(identity|business|address)$")
    sample_text: str = Field(min_length=5, max_length=3000)
    image_quality: int = Field(default=80, ge=0, le=100)
    is_synthetic_or_redacted: bool

    @field_validator("sample_text")
    @classmethod
    def reject_sensitive_values(cls, value: str) -> str:
        if contains_sensitive_data(value):
            raise ValueError("Use synthetic or redacted values only.")
        return value.strip()


class SandboxOrderRequest(BaseModel):
    amount: str = Field(default="1.00", pattern=r"^\d{1,6}\.\d{2}$")
    currency: str = Field(default="USD", pattern=r"^[A-Z]{3}$")


BASE_REQUIREMENTS = [
    ("account_info_matches", "Account information matches your documents"),
    ("email_confirmed", "Email address confirmed"),
    ("pan_ready", "PAN preparation reviewed"),
    ("bank_added", "Indian bank account preparation reviewed"),
    ("purpose_code_selected", "Purpose code preparation reviewed"),
    ("video_kyc_ready", "Video verification setup prepared"),
    ("address_complete", "Address information complete"),
]


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "message": "Backend is running",
        "gemini_configured": bool(os.getenv("GEMINI_API_KEY", "").strip()),
        "paypal_sandbox_configured": paypal_sandbox_configured(),
    }


@app.get("/api/readiness")
def readiness(account_type: AccountType = AccountType.personal):
    definitions = [
        ("account_info_matches", "Review account information", "Match names and details to official documents."),
        ("email_confirmed", "Confirm your email", "Use the confirmation flow in your PayPal account."),
        ("pan_ready", "Review identity requirements", "Prepare requested documents; do not submit them here."),
        ("bank_added", "Prepare your bank account", "Review official receiving-payment requirements for India."),
        ("purpose_code_selected", "Review your purpose code", "Choose the appropriate purpose only through PayPal."),
        ("video_kyc_ready", "Prepare for video verification", "Check your camera, microphone, lighting, and connection."),
        ("address_complete", "Check address information", "Confirm address details are current and consistent."),
    ]
    if account_type == AccountType.business:
        definitions.append((
            "business_documents_ready",
            "Prepare business documents",
            "Review the documents requested for your business type.",
        ))
    steps = [
        {"id": index + 1, "key": key, "title": title, "description": description}
        for index, (key, title, description) in enumerate(definitions)
    ]
    return {
        "title": f"{account_type.value.title()} account readiness checklist",
        "account_type": account_type,
        "notice": "General preparation guidance only—not a live PayPal verification result.",
        "steps": steps,
        "official_help_url": "https://www.paypal.com/in/cshelp/article/how-do-i-confirm-my-identity--help606",
    }


@app.post("/api/readiness/evaluate")
def evaluate_readiness(request: ReadinessEvaluationRequest):
    requirements = list(BASE_REQUIREMENTS)
    if request.account_type == AccountType.business:
        requirements.append(("business_documents_ready", "Business documents prepared"))
    completed = [label for key, label in requirements if getattr(request.answers, key)]
    missing = [
        {"key": key, "label": label}
        for key, label in requirements
        if not getattr(request.answers, key)
    ]
    score = round(len(completed) / len(requirements) * 100)
    recommendation = (
        f"Next, review: {missing[0]['label']}. Use official PayPal guidance before proceeding."
        if missing else
        "Your preparation checklist is complete. Follow the instructions in your PayPal account."
    )
    return {
        "score": score,
        "completed": completed,
        "missing": missing,
        "recommendation": recommendation,
        "disclaimer": "Readiness estimate only; this is not a PayPal KYC status or approval.",
    }


@app.post("/api/assistant")
def assistant(request: AssistantRequest):
    result = answer_with_verified_context(request.question)
    result["source_url"] = result["sources"][0]["url"]
    result["disclaimer"] = "General guidance only; not an official account decision."
    return result


@app.get("/api/documents/sample")
def document_sample(document_type: str = Query(pattern="^(identity|business|address)$")):
    samples = {
        "identity": "Name: SAMPLE USER\nDate of birth: 1990-01-01\nExpiry date: 2030-01-01",
        "business": "Business name: SAMPLE EXPORTS\nRegistration type: Sole proprietorship\nAddress: REDACTED SAMPLE ADDRESS",
        "address": "Name: SAMPLE USER\nAddress: REDACTED SAMPLE ADDRESS\nIssue date: 2026-01-01",
    }
    return {"document_type": document_type, "sample_text": samples[document_type], "synthetic": True}


@app.post("/api/documents/review")
def document_review(request: DocumentReviewRequest):
    if not request.is_synthetic_or_redacted:
        raise HTTPException(
            status_code=400,
            detail="Only synthetic or fully redacted samples are accepted.",
        )
    return review_sample_document(
        request.document_type,
        request.sample_text,
        request.image_quality,
    )


@app.get("/api/paypal/sandbox/status")
def sandbox_status():
    return {
        "configured": paypal_sandbox_configured(),
        "environment": "sandbox",
        "workflow": "Create a Checkout order",
        "disclaimer": "Sandbox payment activity is unrelated to KYC approval.",
    }


@app.post("/api/paypal/sandbox/orders")
def sandbox_order(request: SandboxOrderRequest):
    if not paypal_sandbox_configured():
        raise HTTPException(status_code=503, detail="PayPal Sandbox is not configured.")
    try:
        return create_paypal_sandbox_order(request.amount, request.currency)
    except SandboxIntegrationError:
        raise HTTPException(
            status_code=502,
            detail="PayPal Sandbox could not create the order. Check server configuration.",
        ) from None
