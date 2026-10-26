"""API tests. Run from backend with: python -m unittest -v test.py"""

import os
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from main import app  # noqa: E402


class PayReadyApiTests(unittest.TestCase):
    client = TestClient(app)

    def setUp(self):
        environment = patch.dict(os.environ, {
            "GEMINI_API_KEY": "",
            "PAYPAL_SANDBOX_CLIENT_ID": "",
            "PAYPAL_SANDBOX_CLIENT_SECRET": "",
        })
        environment.start()
        self.addCleanup(environment.stop)

    def test_invalid_assistant_requests(self):
        for payload in ({}, {"question": ""}, {"question": "   "},
                        {"question": 123}, {"question": "x" * 501}):
            with self.subTest(payload=payload):
                self.assertEqual(self.client.post("/api/assistant", json=payload).status_code, 422)

    def test_malformed_json(self):
        response = self.client.post("/api/assistant", content="{broken",
                                    headers={"Content-Type": "application/json"})
        self.assertEqual(response.status_code, 422)

    def test_unknown_question(self):
        response = self.client.post("/api/assistant", json={"question": "Tell me about bananas"})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()["matched"])
        self.assertEqual(response.json()["topic"], None)
        self.assertIn("do not have a verified guidance answer", response.json()["answer"])
        self.assertNotIn("approved", response.json()["answer"].casefold())

    def test_supported_knowledge_topics(self):
        cases = (
            ("How do I prepare for KYC?", "Identity verification"),
            ("How does merchant onboarding work?", "Merchant onboarding"),
            ("What is needed to receive payments?", "Receiving payments"),
            ("How does the penny drop work?", "Confirming a bank account"),
            ("Can I accept domestic payments?", "Domestic payments in India"),
            ("Why is verification delayed?", "Common verification problems"),
            ("How do I remove an account limitation?", "Account limitations"),
        )
        for question, expected_topic in cases:
            with self.subTest(question=question):
                result = self.client.post("/api/assistant", json={"question": question})
                self.assertEqual(result.status_code, 200)
                self.assertTrue(result.json()["matched"])
                self.assertEqual(result.json()["topic"], expected_topic)
                self.assertTrue(result.json()["sources"])
                self.assertTrue(all(
                    source["url"].startswith("https://www.paypal.com/")
                    for source in result.json()["sources"]
                ))

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
