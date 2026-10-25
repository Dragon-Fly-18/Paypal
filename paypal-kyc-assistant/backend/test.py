"""API tests. Run from backend with: python -m unittest -v test.py"""

import os
import unittest

from fastapi.testclient import TestClient

os.environ.pop("GEMINI_API_KEY", None)
os.environ.pop("PAYPAL_SANDBOX_CLIENT_ID", None)
os.environ.pop("PAYPAL_SANDBOX_CLIENT_SECRET", None)

from main import app  # noqa: E402


class PayReadyApiTests(unittest.TestCase):
    client = TestClient(app)

    def test_health_reports_optional_integrations(self):
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")
        self.assertFalse(response.json()["paypal_sandbox_configured"])

    def test_business_readiness_has_extra_requirement(self):
        personal = self.client.get("/api/readiness?account_type=personal").json()
        business = self.client.get("/api/readiness?account_type=business").json()
        self.assertEqual(len(business["steps"]), len(personal["steps"]) + 1)

    def test_readiness_score_and_recommendation(self):
        response = self.client.post("/api/readiness/evaluate", json={
            "account_type": "personal",
            "answers": {
                "account_info_matches": True,
                "email_confirmed": True,
                "pan_ready": True,
                "bank_added": True,
                "purpose_code_selected": True,
                "video_kyc_ready": False,
                "address_complete": False,
            },
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["score"], 71)
        self.assertEqual(len(response.json()["missing"]), 2)

    def test_assistant_uses_verified_fallback(self):
        response = self.client.post("/api/assistant", json={
            "question": "How can I prepare for identity verification?",
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["matched"])
        self.assertEqual(response.json()["provider"], "verified-knowledge-base")
        self.assertTrue(response.json()["sources"])

    def test_assistant_rejects_sensitive_values(self):
        response = self.client.post("/api/assistant", json={
            "question": "My PAN is ABCDE1234F, can you verify it?",
        })
        self.assertEqual(response.status_code, 422)

    def test_document_review_accepts_only_safe_samples(self):
        accepted = self.client.post("/api/documents/review", json={
            "document_type": "address",
            "sample_text": "Name: SAMPLE USER\nAddress: REDACTED\nIssue date: 2026-01-01",
            "image_quality": 90,
            "is_synthetic_or_redacted": True,
        })
        self.assertEqual(accepted.status_code, 200)
        self.assertEqual(accepted.json()["result"], "sample-ready")

        rejected = self.client.post("/api/documents/review", json={
            "document_type": "identity",
            "sample_text": "Name: Real User",
            "image_quality": 90,
            "is_synthetic_or_redacted": False,
        })
        self.assertEqual(rejected.status_code, 400)

    def test_sandbox_is_disabled_without_credentials(self):
        response = self.client.post("/api/paypal/sandbox/orders", json={
            "amount": "1.00",
            "currency": "USD",
        })
        self.assertEqual(response.status_code, 503)


if __name__ == "__main__":
    unittest.main()
