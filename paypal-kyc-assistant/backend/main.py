
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from knowledge_base import NO_MATCH_RESPONSE, find_guidance

app = FastAPI(
    title="PayPal India Merchant Readiness Assistant",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AssistantRequest(BaseModel):
    question: str = Field(min_length=1, max_length=500)


@app.get("/api/health")
def health():
    return {"status": "ok", "message": "Backend is running"}

@app.get("/api/readiness")
def readiness():
    return {
        "title": "Merchant payment-readiness checklist",
        "notice": (
            "This is general guidance, not a live PayPal "
            "account verification result."
        ),
        "steps": [
            {
                "id": 1,
                "title": "Review account information",
                "description": (
                    "Check that your PayPal account information "
                    "matches the information in your official documents."
                )
            },
            {
                "id": 2,
                "title": "Review identity requirements",
                "description": (
                    "Follow the instructions shown in your PayPal "
                    "account and consult the official India help page."
                )
            },
            {
                "id": 3,
                "title": "Prepare for video verification",
                "description": (
                    "If requested, prepare your required documents, "
                    "camera, microphone, lighting and internet connection."
                )
            },
            {
                "id": 4,
                "title": "Check your next steps",
                "description": (
                    "Follow the instructions in your account. Contact "
                    "PayPal support if you cannot complete a step."
                )
            },
        ],
        "official_help_url": (
            "https://www.paypal.com/in/cshelp/article/"
            "how-do-i-confirm-my-identity--help606"
        )
    }


@app.post("/api/assistant")
def assistant(request: AssistantRequest):
    guidance = find_guidance(request.question.strip())
    if guidance is None:
        return {
            "answer": NO_MATCH_RESPONSE,
            "source_url": "https://www.paypal.com/in/cshelp/home",
            "matched": False,
        }
    return {
        "answer": guidance["answer"],
        "source_url": guidance["source_url"],
        "topic": guidance["topic"],
        "matched": True,
    }
