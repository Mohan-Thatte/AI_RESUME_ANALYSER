# ResumeMatch AI

AI-powered resume ↔ job-description matcher. Upload a PDF resume + paste a job
description, and get a match score, skill breakdown, matched/missing skills,
and improvement tips. Requires a Groq API key — there is no mock/fallback
mode; every request is analyzed live.

## What was fixed

- **Dashboard was reading the wrong fields.** The backend returns
  `{ score, skill_breakdown, evidence, partial_skills, missing_skills,
  improvement_path, recruiter_decision }`, but `ResultsDashboard.jsx` was
  destructuring `matched_skills` / `recommendations`, which don't exist in
  the response — so those sections always rendered empty, even on a
  successful analysis. Rewrote the component to match the real schema and
  added a score-breakdown bar chart, partial-matches section, and a
  recruiter-decision badge.
- **Deprecated PDF library.** `PyPDF2` (unmaintained, merged into `pypdf`)
  is replaced with `pypdf` everywhere, matching the parser already used
  elsewhere in the codebase. Also guarded against `None` returns from
  `extract_text()` on image-only PDF pages, which previously could crash
  with a `TypeError`.
- **Packaging.** The zip you sent included a `node_modules` folder built on
  Windows (a Windows-only native `lightningcss` binary) and a Windows venv
  (`.venv/Scripts/*.exe`) — neither works on Linux/Mac. Removed both; you
  reinstall clean with `npm install` / `pip install` below, which pulls the
  correct binaries for your machine.
- Added `app/__init__.py` files for the backend package and a
  `.env.example` for the API key.

## Stack

- **Backend:** FastAPI + Uvicorn, `pypdf` for PDF text extraction, Groq
  (`openai/gpt-oss-120b`) for the matching analysis. No mock fallback — if
  the API key is missing or the request fails, `/api/match` returns a real
  502 error instead of static data.
- **Frontend:** React 19 + Vite, plain CSS (no framework).

## Run it

### 1. Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

Visit `http://localhost:8000/health` — you should see `{"status":"healthy"}`.

**Groq API key (required):** open `.env` and set
`GROQ_API_KEY=your_key_here` (free key at
https://console.groq.com/keys). Without it, `/api/match` returns a 502
error — the analysis only runs with a valid key, there's no fallback data.

### 2. Frontend

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open the printed URL (typically `http://localhost:5173`). Upload a PDF
resume, paste a job description, click **Analyze Match**.

The frontend calls the backend at `http://localhost:8000` — hardcoded in
`src/App.jsx`. Change that if you deploy the backend elsewhere.

## What I'd extend first

1. **Move the API URL to an env var** (`VITE_API_URL` via Vite's `import.meta.env`)
   instead of hardcoding `localhost:8000`, so the same build works in
   dev/staging/prod.
2. **Persist analyses.** Right now nothing is saved — add a small SQLite
   table (resume text, JD, result, timestamp) so users can revisit past
   matches, and so you can build history/trends later.
3. **Wire up `app/api/resume.py`.** It has a working standalone
   `/upload-resume` text-extraction endpoint that isn't currently mounted
   in `main.py` — useful if you want to preview extracted resume text
   before running the full match, or split extraction from analysis for
   caching.
4. **Real cover-letter endpoint.** `matching_service.py` already has
   `generate_cover_letter()` fully implemented but no route calls it — a
   `/api/cover-letter` endpoint plus a button in the results dashboard
   would be a quick, high-value addition.
5. **Input limits & validation.** Cap PDF size/page count and job-description
   length server-side before sending to Groq, and add a friendlier
   error state in the UI for parse failures (currently just a red line of
   text).
