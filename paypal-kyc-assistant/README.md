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
python -m pip install -r requirements.txt
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
