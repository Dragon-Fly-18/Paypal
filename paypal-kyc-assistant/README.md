# PayReady India

PayReady India is an independent React/Vite and FastAPI prototype that helps
merchants prepare for PayPal India onboarding. It does **not** connect to a live
PayPal account, submit KYC documents, or make verification decisions.

## Features

- Personal and business preparation checklists with a dynamic readiness score.
- Verified, source-linked guidance with an optional Gemini grounded-answer mode.
- Synthetic/redacted document field and readability demonstration.
- Optional PayPal Sandbox Checkout order creation through the backend.
- Sensitive-value rejection and explicit KYC/Sandbox disclaimers.

## Local setup

Requirements: Node.js 20+, Python 3.10+.

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-foundation.txt
Copy-Item ..\.env.example .env
python -m uvicorn main:app --reload
```

In another terminal:

```powershell
cd frontend
npm ci
npm run dev
```

Open `http://localhost:5173`. API documentation is at
`http://127.0.0.1:8000/docs`.

The foundation requirements include the HTTP clients needed for API tests and
Sandbox requests. The existing `requirements.txt` contains the broader optional
dependency collection, including Gemini. Install optional integrations separately
when you enable them.

### Foundation verification

Verified on October 26, 2026: 11 backend tests pass, dependency checks pass,
frontend lint and production build pass. Browser checks confirmed checklist
progress (one of seven items = 14%), API-backed assistant answers and sources,
disabled whitespace submission, connection errors with the backend stopped,
and successful checklist recovery through Try again after restarting the backend.

The verified knowledge base covers identity verification, merchant onboarding,
receiving payments, bank confirmation, domestic payments, common verification
problems, account limitations, and the PayPal Sandbox. Each answer links to an
official source and unknown questions return a neutral fallback without claiming
access to account status or KYC approval.

The API tests cover health, personal/business checklists, score calculation,
assistant answers, missing/empty/whitespace input, incorrect types, overlong input,
malformed JSON, and unknown questions. Tests override integration credentials to
avoid external service calls even when a local `.env` exists.

For the browser smoke check, start both servers, select checklist items and confirm
the percentage updates, then submit a suggested assistant question and check its
source link. Blank or one-character questions should leave Submit disabled.
Stop the backend, refresh the dashboard, and confirm the connection error and
Try again button appear. Restart the backend and click Try again to recover.
Also submit a question while the backend is stopped and check the assistant error.

## Optional integrations

Keep all secrets in `backend/.env` or a production secrets manager. Never use a
`VITE_` variable for a secret because Vite exposes those values to the browser.

- `GEMINI_API_KEY`: enables Gemini answers grounded only in matched knowledge-base
  entries. Without it, the same endpoint returns deterministic verified guidance.
- `PAYPAL_SANDBOX_CLIENT_ID` and `PAYPAL_SANDBOX_CLIENT_SECRET`: enable a Sandbox-only
  USD 1.00 order demonstration. The server is hardcoded to the PayPal Sandbox host.
- `CORS_ORIGINS`: comma-separated trusted frontend origins.

The Sandbox workflow demonstrates payment API authentication and order creation;
it is intentionally separate from KYC readiness and cannot approve KYC.

## Tests

```powershell
cd backend
python -m unittest -v test.py

cd ..\frontend
npm run lint
npm run build
```

The backend tests do not require Gemini or PayPal credentials and never call live
external services. A real Sandbox order must be tested manually after credentials
are configured.

## Privacy boundaries

- Do not enter passwords, OTPs, PAN/Aadhaar numbers, or real document details.
- Questions and sample text are processed in memory and are not stored by this app.
- The document lab accepts only synthetic or fully redacted text samples.
- All results are preparation guidance, never an official PayPal account decision.

## Official references

- [PayPal India identity confirmation](https://www.paypal.com/in/cshelp/article/how-do-i-confirm-my-identity--help606)
- [PayPal India receiving payments](https://www.paypal.com/in/cshelp/article/how-do-i-receive-payments-through-paypal-HELP667)
- [PayPal REST API authentication](https://developer.paypal.com/api/rest/authentication/)
- [PayPal REST API requests](https://developer.paypal.com/api/make-api-requests/)
- [Gemini API getting started](https://ai.google.dev/gemini-api/docs/get-started)
