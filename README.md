
# PragyaSetu — Flask prototype

A Flask app for India's Official Statistical System capacity-building
platform: a competency-gap ledger, iGOT-style course recommendations, and a
real AI-powered MCQ generator.

## Project layout

```
pragyasetu-flask/
├── app.py                  # Flask routes + mock FRAC/iGOT data + AI quiz endpoint
├── requirements.txt
├── .env.example
├── templates/
│   └── index.html          # Page shell (Jinja)
└── static/
    ├── css/style.css       # Styling
    └── js/app.js           # All frontend logic (fetches, rendering, quiz UI)
```

## 1. Open in VS Code

```bash
code pragyasetu-flask
```

## 2. Create a virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

VS Code will usually prompt "Select interpreter" — pick the one inside `venv`.

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

If you're updating an existing project folder rather than starting fresh,
re-run this command every time `requirements.txt` changes — pip won't pick
up new lines in the file on its own.

## 4. Add your API key

```bash
cp .env.example .env
```

Open `.env` and paste your real key:

```
ANTHROPIC_API_KEY=sk-ant-...
```

Never commit `.env` to a shared repo.

## 5. Run it

```bash
python app.py
```

Open **http://127.0.0.1:5000**.

## What's real vs. mocked

- **Real:** the `/api/generate-quiz` call — it hits the actual Claude API
  from your Flask backend and returns genuinely generated MCQs.
- **Mocked:** `OFFICERS` and `COURSE_CATALOGUE` in `app.py` — placeholder
  data standing in for a real FRAC dictionary and iGOT Karmayogi's
  course-catalogue/learner-analytics APIs.
- **Not implemented:** the "Open in iGOT Karmayogi" button doesn't link
  anywhere real — call that out if judges ask.
=======
# PragyaSetu-Capacity-building-layer-for-iGOT-Karmayogi
>>>>>>> 5e2fa5c9663fc6ffb8b3d8d0280673e31627fbd5
