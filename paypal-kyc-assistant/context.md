# Reverse Engineering Prompt — PayReady India UI

Act as a senior frontend engineer, UI/UX designer, and codebase analyst. Your task is to reverse-engineer and implement the **PayReady India Merchant Onboarding Dashboard** in my existing project.

## 1. Project Context

Project name: PayReady India  
Purpose: An AI-assisted merchant onboarding and payment-readiness guidance platform for PayPal India merchants.

Technology stack:
- Frontend: React + Vite
- Styling: CSS
- Backend: Python + FastAPI
- Backend base URL: `http://127.0.0.1:8000`
- Existing API endpoint: `/api/readiness`

The backend is already running and returns JSON containing:
- `title`
- `notice`
- `steps` — an array containing `id`, `title`, and `description`
- `official_help_url`

**Important:** Inspect the existing source files before making changes. Reuse working code and preserve the backend API contract.

## 2. UI to Reconstruct

Recreate a polished, professional, responsive SaaS dashboard with the following structure.

### A. Top Navigation
- White navigation bar.
- Left-aligned PayReady India brand.
- Compact blue logo tile with a letter or simple mark.
- Merchant tools label on the right.
- Thin bottom border and consistent spacing.

### B. Hero Section
- Large rounded rectangular panel.
- Soft blue gradient background.
- Eyebrow text: “YOUR ONBOARDING COMPANION”.
- Main headline: “Get ready to accept payments.”
- Short explanatory text about onboarding and payment readiness.
- Primary call-to-action: “Start your checklist”.
- Decorative illustration on desktop using CSS shapes and a floating verification card.
- Hide or simplify decorative elements on small screens.

### C. Main Dashboard Layout
Use a two-column desktop layout:
- Left: Merchant readiness checklist.
- Right: AI assistant and account safety tip.
- On mobile, stack the columns vertically.

### D. Merchant Readiness Checklist
- White card with rounded corners and a subtle border.
- Section label: “STEP-BY-STEP GUIDE”.
- Heading: “Merchant readiness checklist”.
- Display completed-step count.
- Animated progress bar.
- Display the total percentage completed.
- Render each checklist step dynamically from the backend response.
- Each step includes:
  - Accessible checkbox.
  - Step number.
  - Title and description.
  - Status label showing “To do” or “Done”.
- Checked steps should have distinct styling.
- Display a useful loading state while fetching data.
- Display a clear error message and retry option if the API fails.
- Include a link to `official_help_url` from the API response.
- Display the API-provided `notice`.

### E. AI Assistant Card
- Heading: “Ask PayReady”.
- Simple spark or assistant icon.
- Short explanation of the assistant's intended purpose.
- Suggested questions:
  - “Why might verification be delayed?”
  - “How do I prepare for verification?”
  - “What should I check before receiving payments?”
- Text input and submit button.
- Clicking a suggested question should populate the input.
- Until the AI backend is integrated, clearly label this section as a prototype or coming soon.
- Do not pretend to generate AI answers when no AI service is connected.

### F. Account Safety Card
Include a compact green-tinted information card explaining that users must not enter PayPal passwords, PAN/Aadhaar numbers, or identity documents into the prototype.

### G. Footer
- Display “PayReady India · Independent prototype”.
- State that this is not an official PayPal service.
- Use subtle typography and a top border.

## 3. Visual Design System

Use a modern, minimal fintech aesthetic.

Colors:
- Primary navy: `#173C78`
- Primary blue: `#2166D5`
- Page background: `#F5F8FC`
- Card background: `#FFFFFF`
- Primary text: `#172B4D`
- Secondary text: `#697991`
- Border: `#E3EAF3`
- Success: muted green tones.

Typography:
- Use Manrope for headings and DM Sans for body text, with sensible system fallbacks.
- Use a clear hierarchy, readable line heights, and restrained font weights.

Components:
- Rounded cards and buttons.
- Subtle borders and shadows.
- Consistent spacing.
- Clear hover and keyboard-focus states.
- Avoid excessive gradients, oversized decorations, and unnecessary animations.

## 4. Functional Requirements

1. Fetch checklist data from `GET /api/readiness`.
2. Handle loading, HTTP errors, and network failures.
3. Render checklist entries dynamically.
4. Update progress immediately when checkboxes change.
5. Keep progress between zero and one hundred percent.
6. Make external source links open in a new tab securely.
7. Make suggested questions populate the input.
8. Prevent empty question submissions.
9. Make the layout usable at desktop, tablet, and mobile widths.
10. Use semantic HTML and accessible labels.

Do not hardcode checklist entries in the frontend when the backend already supplies them.

## 5. Codebase and File Requirements

Inspect and update the existing files as needed:
- `frontend/src/App.jsx`
- `frontend/src/App.css`
- `frontend/src/index.css`
- `frontend/src/main.jsx` only if required.

Keep the implementation beginner-friendly and maintainable. Use React functional components and hooks. Do not add unnecessary dependencies.

Do not modify the FastAPI backend unless a genuine integration problem requires it.

Do not expose API keys or secrets in frontend code.

## 6. Constraints

- Do not replace the project with a different framework.
- Do not remove working backend endpoints.
- Do not invent live PayPal account verification capabilities.
- Do not collect sensitive identity information.
- Do not claim the assistant uses AI until the AI integration exists.
- Do not create a blank page or leave the project in a broken state.
- Preserve existing project configuration and dependencies wherever possible.

## 7. Validation and Deliverables

After implementation:

1. Run the frontend development server.
2. Check the browser console for errors.
3. Confirm that the checklist loads from FastAPI.
4. Test checkbox interactions and progress calculations.
5. Test the official guidance link.
6. Test mobile responsiveness.
7. Verify that existing backend routes still work.
8. List the files changed and explain each change.
9. Provide the exact commands to run the frontend and backend.
10. Report any remaining limitations honestly.

**Success criteria:** A working, polished PayReady India dashboard that connects to the existing FastAPI readiness endpoint, looks professional on desktop and mobile, and is ready for subsequent AI integration.

Your project is a solo beginner build, so let's make one feature work end-to-end before adding more complexity.
Today's additional tasks

1. Test error handling

Test what happens if the FastAPI backend stops while the frontend is open.
- Stop the backend with Ctrl + C.
- Refresh the dashboard.
- Confirm the page shows a useful error message instead of a blank screen.
- Restart the backend and confirm the checklist loads again.




2. Build the official knowledge base

Create backend/knowledge_base.py containing verified guidance on:
- Identity verification
- Receiving payments
- Common verification problems
Each topic should have keywords, a short answer, and an official PayPal source URL. Keep the guidance general and link users to the official source for account-specific requirements.




3. Implement a basic assistant endpoint

Add POST /api/assistant to FastAPI.

Initially, it should match a user's question against your knowledge base and return:
- An answer
- A source link
- A message when no relevant answer is found
This is your first working assistant; Gemini integration can come after this endpoint works.




4. Add privacy and safety checks
- Warn users not to enter passwords, PAN, Aadhaar numbers, or identity-document details.
- Don't claim to verify a real PayPal account.
- Don't collect or store submitted questions unnecessarily.
- Make it clear that answers are general guidance, not official account decisions.




5. Save a working checkpoint
- Confirm .gitignore is in the project root.
- Make sure .env, .venv/, and node_modules/ aren't committed.
- Commit your working dashboard and backend to GitHub.
- Test the health, readiness, and assistant endpoints through /docs.



Suggested schedule for today
Time	Task	Expected result
20 min	Backend-offline test	Friendly error and successful recovery
45 min	Create knowledge_base.py	Three grounded knowledge entries
60 min	Implement /api/assistant	Question → answer + source
20 min	Test using /docs	Matching and unknown questions both work
15 min	Git checkpoint	Safe, committed project

Today's definition of done: a user can ask a basic PayPal India question, receive relevant guidance, and open its official source—even before you add Gemini.

Official references to use:
- PayPal India identity confirmation
- PayPal India receiving payments
- PayPal Checkout integration
My recommendation: finish Tasks 1–3 first. Don't spend today's time on animations or extra dashboard styling. A functioning assistant backed by trustworthy sources adds more value to your hackathon demo than visual polish alone.

Your next development checklist
Implementation progress

16/20 implemented

Remaining manual/integration work: enable privacy-reviewed document AI/OCR,
run a credentialed PayPal Sandbox order, run the full backend workflow on a
machine with Python, and record the prepared demo.



Phase 1 — AI KYC assistant
[x] Create FastAPI backend endpoints
[x] Connect Gemini API securely
[x] Build a verified PayPal KYC knowledge base
[x] Display AI answers with official sources


Phase 2 — Smart KYC readiness
[x] Create personal/business account preparation flows
[x] Build a dynamic readiness score
[x] Detect missing checklist requirements
[x] Generate personalized next-step recommendations


Phase 3 — AI document analysis
[x] Support synthetic or redacted sample documents
[ ] Extract document fields using AI/OCR
[x] Check missing fields and image readability
[x] Show a simulated document review result


Phase 4 — PayPal integration
[x] Review PayPal Developer API capabilities
[x] Select a meaningful supported PayPal Sandbox workflow
[ ] Integrate and test the Sandbox API (integration implemented; credentialed test pending)
[x] Clearly separate Sandbox activity from KYC approval


Phase 5 — Submission
[x] Add privacy and error handling
[ ] Test complete application workflow
[x] Prepare GitHub repository and README
[ ] Record demo and prepare submission (script prepared in DEMO_SCRIPT.md)


Example of how your finished project should work
EXAMPLE — SIMULATED KYC READINESS REVIEW
KYC Readiness
Based on sample checklist responses

75%



Account information provided

Business information provided

Sample identity document reviewed

Address information incomplete


AI recommendation

Your address information is incomplete. Review the address requirements in PayPal's official guidance before proceeding.
This is a readiness demonstration, not an actual PayPal KYC status or approval.
