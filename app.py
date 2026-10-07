import json
import sqlite3
import secrets
from functools import wraps
from pathlib import Path

from flask import Flask, jsonify, render_template, request, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from google import genai

load_dotenv()

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)  # regenerates each restart — see README for persistent-secret note

# genai.Client() automatically reads GEMINI_API_KEY from the environment —
# never hardcode the key in source. Set it in .env (see .env.example).
client = genai.Client()

# ---------------------------------------------------------------------------
# Auth — simple session-based login backed by a local SQLite users table.
# ---------------------------------------------------------------------------

DB_PATH = Path(__file__).parent / "users.db"


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL
            )
        """)


init_db()


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("user_id"):
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html", error=None)

    username = (request.form.get("username") or "").strip()
    password = request.form.get("password") or ""

    if not username or not password:
        return render_template("register.html", error="Username and password are both required.")
    if len(password) < 6:
        return render_template("register.html", error="Password must be at least 6 characters.")

    try:
        with get_db() as conn:
            conn.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                (username, generate_password_hash(password)),
            )
        return redirect(url_for("login", registered="1"))
    except sqlite3.IntegrityError:
        return render_template("register.html", error="That username is already taken.")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        just_registered = request.args.get("registered") == "1"
        return render_template("login.html", error=None, just_registered=just_registered)

    username = (request.form.get("username") or "").strip()
    password = request.form.get("password") or ""

    with get_db() as conn:
        user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()

    if user is None or not check_password_hash(user["password_hash"], password):
        return render_template("login.html", error="Incorrect username or password.", just_registered=False)

    session["user_id"] = user["id"]
    session["username"] = user["username"]
    return redirect(url_for("index"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# ---------------------------------------------------------------------------
# Mock data — stands in for a real FRAC dictionary + iGOT Karmayogi
# learner-analytics API. Swap this for real API calls once you have access.
# ---------------------------------------------------------------------------

OFFICERS = [
    {
        "id": "nair",
        "name": "R. Nair",
        "role": "Assistant Director",
        "org": "NSO — Field Operations Division",
        "competencies": [
            {"name": "Survey Sampling Design", "category": "Domain", "required": 4, "acquired": 2},
            {"name": "Statistical Data Analysis", "category": "Domain", "required": 4, "acquired": 3},
            {"name": "Data Quality Assurance", "category": "Domain", "required": 3, "acquired": 3},
            {"name": "MIS & Digital Reporting", "category": "Functional", "required": 3, "acquired": 1},
            {"name": "Field Team Supervision", "category": "Functional", "required": 3, "acquired": 3},
            {"name": "Stakeholder Coordination", "category": "Behavioural", "required": 3, "acquired": 2},
        ],
    },
    {
        "id": "verma",
        "name": "S. Verma",
        "role": "Statistical Officer",
        "org": "State DES — Punjab",
        "competencies": [
            {"name": "Survey Sampling Design", "category": "Domain", "required": 3, "acquired": 3},
            {"name": "Statistical Data Analysis", "category": "Domain", "required": 3, "acquired": 2},
            {"name": "Data Quality Assurance", "category": "Domain", "required": 4, "acquired": 2},
            {"name": "GIS Mapping for Enumeration", "category": "Functional", "required": 3, "acquired": 1},
            {"name": "MIS & Digital Reporting", "category": "Functional", "required": 3, "acquired": 2},
            {"name": "Public Data Communication", "category": "Behavioural", "required": 2, "acquired": 2},
        ],
    },
    {
        "id": "iyer",
        "name": "K. Iyer",
        "role": "Deputy Director",
        "org": "MoSPI — Economic Statistics",
        "competencies": [
            {"name": "National Accounts Methodology", "category": "Domain", "required": 5, "acquired": 3},
            {"name": "Statistical Data Analysis", "category": "Domain", "required": 4, "acquired": 4},
            {"name": "Policy Interpretation", "category": "Functional", "required": 4, "acquired": 3},
            {"name": "MIS & Digital Reporting", "category": "Functional", "required": 3, "acquired": 3},
            {"name": "Ethics in Official Statistics", "category": "Behavioural", "required": 4, "acquired": 3},
            {"name": "Stakeholder Coordination", "category": "Behavioural", "required": 4, "acquired": 2},
        ],
    },
    {
        "id": "bhattacharya",
        "name": "A. Bhattacharya",
        "role": "Senior Statistical Officer",
        "org": "NSO — Survey Design Division",
        "competencies": [
            {"name": "Survey Sampling Design", "category": "Domain", "required": 4, "acquired": 4},
            {"name": "Statistical Data Analysis", "category": "Domain", "required": 4, "acquired": 3},
            {"name": "Data Quality Assurance", "category": "Domain", "required": 4, "acquired": 3},
            {"name": "GIS Mapping for Enumeration", "category": "Functional", "required": 2, "acquired": 1},
            {"name": "Field Team Supervision", "category": "Functional", "required": 3, "acquired": 3},
            {"name": "Ethics in Official Statistics", "category": "Behavioural", "required": 3, "acquired": 3},
        ],
    },
    {
        "id": "reddy",
        "name": "P. Reddy",
        "role": "Statistical Officer",
        "org": "State DES — Telangana",
        "competencies": [
            {"name": "Survey Sampling Design", "category": "Domain", "required": 3, "acquired": 1},
            {"name": "Data Quality Assurance", "category": "Domain", "required": 3, "acquired": 1},
            {"name": "MIS & Digital Reporting", "category": "Functional", "required": 3, "acquired": 1},
            {"name": "GIS Mapping for Enumeration", "category": "Functional", "required": 3, "acquired": 2},
            {"name": "Public Data Communication", "category": "Behavioural", "required": 2, "acquired": 2},
            {"name": "Stakeholder Coordination", "category": "Behavioural", "required": 3, "acquired": 1},
        ],
    },
    {
        "id": "chauhan",
        "name": "M. Chauhan",
        "role": "Joint Director",
        "org": "MoSPI — Social Statistics",
        "competencies": [
            {"name": "National Accounts Methodology", "category": "Domain", "required": 4, "acquired": 3},
            {"name": "Statistical Data Analysis", "category": "Domain", "required": 4, "acquired": 4},
            {"name": "Policy Interpretation", "category": "Functional", "required": 4, "acquired": 4},
            {"name": "MIS & Digital Reporting", "category": "Functional", "required": 3, "acquired": 3},
            {"name": "Ethics in Official Statistics", "category": "Behavioural", "required": 4, "acquired": 4},
            {"name": "Stakeholder Coordination", "category": "Behavioural", "required": 4, "acquired": 3},
        ],
    },
]

# competency name -> mock iGOT Karmayogi course
COURSE_CATALOGUE = {
    "Survey Sampling Design": {"title": "Foundations of Survey Sampling for Official Statistics", "code": "IGOT-MOSPI-104", "duration": "6 hrs"},
    "Statistical Data Analysis": {"title": "Applied Statistical Analysis for Field Officers", "code": "IGOT-MOSPI-118", "duration": "8 hrs"},
    "MIS & Digital Reporting": {"title": "Digital MIS Reporting for State & Central Cadres", "code": "IGOT-MOSPI-072", "duration": "3 hrs"},
    "GIS Mapping for Enumeration": {"title": "GIS Tools for Enumeration Block Mapping", "code": "IGOT-MOSPI-091", "duration": "5 hrs"},
    "Data Quality Assurance": {"title": "Data Quality & Validation Protocols", "code": "IGOT-MOSPI-057", "duration": "4 hrs"},
    "Stakeholder Coordination": {"title": "Inter-Departmental Coordination for Statistical Programmes", "code": "IGOT-DOPT-233", "duration": "2 hrs"},
    "National Accounts Methodology": {"title": "National Accounts: Concepts & Current Revisions", "code": "IGOT-MOSPI-140", "duration": "10 hrs"},
    "Policy Interpretation": {"title": "Translating Statistics into Policy Briefs", "code": "IGOT-MOSPI-085", "duration": "3 hrs"},
    "Ethics in Official Statistics": {"title": "UN Fundamental Principles of Official Statistics", "code": "IGOT-MOSPI-011", "duration": "2 hrs"},
    "Public Data Communication": {"title": "Communicating Statistical Findings to the Public", "code": "IGOT-MOSPI-063", "duration": "3 hrs"},
    "Field Team Supervision": {"title": "Leading Field Enumeration Teams", "code": "IGOT-MOSPI-045", "duration": "4 hrs"},
}


def officers_with_courses():
    """Attach the matched course (if any) to each competency, for the frontend."""
    out = []
    for officer in OFFICERS:
        comps = []
        for c in officer["competencies"]:
            comps.append({**c, "course": COURSE_CATALOGUE.get(c["name"])})
        out.append({**officer, "competencies": comps})
    return out


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/")
@login_required
def index():
    return render_template("index.html", username=session.get("username"))


@app.route("/api/officers")
@login_required
def get_officers():
    return jsonify(officers_with_courses())


@app.route("/api/generate-quiz", methods=["POST"])
@login_required
def generate_quiz():
    data = request.get_json(force=True) or {}
    material = (data.get("material") or "").strip()
    tag = (data.get("tag") or "General").strip()
    count = int(data.get("count", 5))

    if not material:
        return jsonify({"error": "Paste or upload some training material first."}), 400

    prompt = f"""You are generating a training quiz for Indian government officers in the Official Statistical System.

Source material:
\"\"\"
{material[:6000]}
\"\"\"

Write exactly {count} multiple-choice questions that test understanding of this material. Tag every question with the competency "{tag}".

Respond with ONLY a raw JSON array (no markdown fences, no preamble, no commentary), where each item has this exact shape:
{{"question": string, "options": [string, string, string, string], "correctIndex": number (0-3), "explanation": string, "competency": "{tag}"}}"""

    try:
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt,
        )
        text = response.text or ""
        clean = text.replace("```json", "").replace("```", "").strip()
        questions = json.loads(clean)
        if not isinstance(questions, list) or not questions:
            raise ValueError("empty or malformed response")
        return jsonify({"questions": questions})
    except Exception as e:
        print(f"[generate_quiz] {type(e).__name__}: {e}")
        return jsonify({
            "error": "Couldn't generate questions from that material — try shortening it or rephrasing, then generate again."
        }), 502


if __name__ == "__main__":
    app.run(debug=True, port=5000)