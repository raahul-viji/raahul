# PocketSmart AI — Smart Budget & Recommendation Assistant

PocketSmart AI is a budget-aware Generative AI assistant for **Home Interior Planning, Party Planning, and Jewelry Recommendations**.

## Features
- FastAPI backend with Jinja2 frontend
- Home, Party and Jewelry planners
- Gemini-powered recommendations when `GEMINI_API_KEY` is configured
- Optional jewelry outfit-image analysis
- Demo/fallback recommendations when Gemini is not configured or returns an incomplete result
- Registration, login, logout and session handling
- SQLite recommendation history and detail pages
- Responsive card-based UI
- JSON/API routes required by the project documentation

## Run locally

```bash
python -m venv venv
# Windows
venv\\Scripts\\activate
# macOS/Linux
source venv/bin/activate
pip install -r requirements.txt
copy .env.example .env   # Windows
# cp .env.example .env   # macOS/Linux
uvicorn main:app --reload
```

Open `http://127.0.0.1:8000`.

### Gemini
Add your Gemini API key to `.env`:

```env
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini-3.8-flash
```

The documentation describes Gemini 1.5 Flash Pro, but that model reference is historical. The implementation uses the current Google GenAI Python SDK and a currently available Gemini model by default; change `GEMINI_MODEL` if your account uses another supported model.

## Main routes
`/`, `/register`, `/login`, `/logout`, `/dashboard`, `/home-planner`, `/party-planner`, `/jewelry-planner`, `/history`, `/generate-home`, `/generate-party`, `/generate-jewelry`, `/recommendations-details/{recommendation_id}`, `/session-info`, `/session-data`, `/token`, `/startup`.

## Notes on recommendations
Unless a live product/vendor API is added, product names, platforms and prices are **AI suggestions or estimates**, not verified live listings. The app intentionally avoids presenting simulated prices as real-time marketplace data.
