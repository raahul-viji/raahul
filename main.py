import json, os, sqlite3, uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, Request, Form, File, UploadFile, HTTPException, Depends
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
import hashlib, hmac

from gemini_utils import generate_recommendation, parse_ai_json

load_dotenv()
BASE = Path(__file__).resolve().parent
DB_PATH = BASE / os.getenv("DATABASE_PATH", "pocketsmart.db")
SECRET = os.getenv("SECRET_KEY", "change-this-secret-key")

def hash_password(password):
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 180000)
    return salt.hex() + ":" + digest.hex()

def verify_password(password, stored):
    try:
        salt_hex, digest_hex = stored.split(":", 1)
        digest = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt_hex), 180000)
        return hmac.compare_digest(digest.hex(), digest_hex)
    except Exception:
        return False


app = FastAPI(title="PocketSmart AI", version="2.0.0", description="Smart Budget & Recommendation Assistant")
app.add_middleware(SessionMiddleware, secret_key=SECRET, max_age=60 * 60 * 24 * 7, same_site="lax")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.mount("/static", StaticFiles(directory=BASE / "static"), name="static")
app.mount("/uploads", StaticFiles(directory=BASE / "uploads"), name="uploads")
templates = Jinja2Templates(directory=str(BASE / "templates"))


def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with db() as c:
        c.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, email TEXT UNIQUE NOT NULL, password_hash TEXT NOT NULL, created_at TEXT NOT NULL)")
        c.execute("CREATE TABLE IF NOT EXISTS recommendations (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, planner_type TEXT NOT NULL, title TEXT NOT NULL, request_json TEXT NOT NULL, result_json TEXT NOT NULL, created_at TEXT NOT NULL, FOREIGN KEY(user_id) REFERENCES users(id))")


@app.on_event("startup")
async def startup():
    init_db()


def current_user(request: Request):
    uid = request.session.get("user_id")
    if not uid:
        return None
    with db() as c:
        row = c.execute("SELECT id,name,email,created_at FROM users WHERE id=?", (uid,)).fetchone()
    return dict(row) if row else None


def require_user(request: Request):
    user = current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Login required")
    return user


def render(request, name, **context):
    return templates.TemplateResponse(name, {"request": request, "user": current_user(request), **context})


@app.get("/", response_class=HTMLResponse)
async def index(request: Request): return render(request, "index.html")

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request): return render(request, "register.html")

@app.post("/register")
async def register(request: Request, name: str = Form(...), email: str = Form(...), password: str = Form(...)):
    if len(password) < 6: return render(request, "register.html", error="Password must contain at least 6 characters.")
    try:
        with db() as c:
            cur = c.execute("INSERT INTO users(name,email,password_hash,created_at) VALUES(?,?,?,?)", (name.strip(), email.strip().lower(), hash_password(password), datetime.utcnow().isoformat()))
            request.session["user_id"] = cur.lastrowid
        return RedirectResponse("/dashboard", status_code=303)
    except sqlite3.IntegrityError:
        return render(request, "register.html", error="An account with that email already exists.")

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request): return render(request, "login.html")

@app.post("/login")
async def login(request: Request, email: str = Form(...), password: str = Form(...)):
    with db() as c: row = c.execute("SELECT * FROM users WHERE email=?", (email.strip().lower(),)).fetchone()
    if not row or not verify_password(password, row["password_hash"]): return render(request, "login.html", error="Invalid email or password.")
    request.session["user_id"] = row["id"]
    return RedirectResponse("/dashboard", status_code=303)

@app.get("/logout")
async def logout(request: Request):
    request.session.clear(); return RedirectResponse("/", status_code=303)

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    user = require_user(request)
    with db() as c: rows = c.execute("SELECT * FROM recommendations WHERE user_id=? ORDER BY id DESC LIMIT 6", (user["id"],)).fetchall()
    return render(request, "dashboard.html", recommendations=[dict(x) for x in rows])

@app.get("/home-planner", response_class=HTMLResponse)
async def home_planner(request: Request): require_user(request); return render(request, "home_planner.html")
@app.get("/party-planner", response_class=HTMLResponse)
async def party_planner(request: Request): require_user(request); return render(request, "party_planner.html")
@app.get("/jewelry-planner", response_class=HTMLResponse)
async def jewelry_planner(request: Request): require_user(request); return render(request, "jewelry_planner.html")

@app.get("/history", response_class=HTMLResponse)
async def history(request: Request):
    user = require_user(request)
    with db() as c: rows = c.execute("SELECT * FROM recommendations WHERE user_id=? ORDER BY id DESC", (user["id"],)).fetchall()
    return render(request, "history.html", recommendations=[dict(x) for x in rows])

@app.get("/recommendations-details/{recommendation_id}", response_class=HTMLResponse)
async def recommendation_details(request: Request, recommendation_id: int):
    user = require_user(request)
    with db() as c: row = c.execute("SELECT * FROM recommendations WHERE id=? AND user_id=?", (recommendation_id, user["id"])).fetchone()
    if not row: raise HTTPException(404, "Recommendation not found")
    data = dict(row); data["result"] = json.loads(data["result_json"]); data["request"] = json.loads(data["request_json"])
    return render(request, "recommendation_details.html", recommendation=data)

@app.get("/session-info")
async def session_info(request: Request):
    user = current_user(request); return {"logged_in": bool(user), "user": user}

@app.get("/session-data")
async def session_data(request: Request):
    user = require_user(request)
    with db() as c:
        count = c.execute("SELECT COUNT(*) FROM recommendations WHERE user_id=?", (user["id"],)).fetchone()[0]
    return {"user": user, "recommendation_count": count}

@app.get("/token")
async def token(request: Request):
    user = require_user(request); return {"access_token": f"session-{user['id']}-{uuid.uuid4().hex}", "token_type": "bearer"}


async def save_result(request: Request, planner_type: str, payload: dict, result: dict):
    user = require_user(request)
    with db() as c:
        cur = c.execute("INSERT INTO recommendations(user_id,planner_type,title,request_json,result_json,created_at) VALUES(?,?,?,?,?,?)", (user["id"], planner_type, result.get("title", "PocketSmart AI Recommendation"), json.dumps(payload), json.dumps(result), datetime.utcnow().isoformat()))
    return {"success": True, "recommendation_id": cur.lastrowid, "planner_type": planner_type, "recommendation": result}

@app.post("/generate-home")
async def generate_home(request: Request):
    user = require_user(request); form = await request.form(); payload = dict(form)
    payload["budget"] = float(payload.get("budget", 0)); payload["planner_type"] = "home"
    result = generate_recommendation("home", payload)
    return JSONResponse(await save_result(request, "home", payload, result))

@app.post("/generate-party")
async def generate_party(request: Request):
    user = require_user(request); form = await request.form(); payload = dict(form)
    payload["budget"] = float(payload.get("budget", 0)); payload["guests"] = int(payload.get("guests", 1)); payload["planner_type"] = "party"
    result = generate_recommendation("party", payload)
    return JSONResponse(await save_result(request, "party", payload, result))

@app.post("/generate-jewelry")
async def generate_jewelry(request: Request, outfit_image: Optional[UploadFile] = File(None)):
    user = require_user(request); form = await request.form(); payload = dict(form)
    payload["budget"] = float(payload.get("budget", 0)); payload["planner_type"] = "jewelry"
    image_bytes = await outfit_image.read() if outfit_image and outfit_image.filename else None
    if image_bytes:
        ext = Path(outfit_image.filename).suffix.lower() or ".jpg"; safe = f"{uuid.uuid4().hex}{ext}"; (BASE / "uploads" / safe).write_bytes(image_bytes); payload["image_filename"] = safe
    result = generate_recommendation("jewelry", payload, image_bytes=image_bytes, image_mime=(outfit_image.content_type if outfit_image else None))
    return JSONResponse(await save_result(request, "jewelry", payload, result))

@app.get("/api/recommendations/{recommendation_id}")
async def api_recommendation(recommendation_id: int, request: Request):
    user = require_user(request)
    with db() as c: row = c.execute("SELECT * FROM recommendations WHERE id=? AND user_id=?", (recommendation_id, user["id"])).fetchone()
    if not row: raise HTTPException(404, "Not found")
    data = dict(row); data["result"] = json.loads(data.pop("result_json")); data["request"] = json.loads(data.pop("request_json")); return data

@app.get("/startup")
async def startup_status(): return {"status": "ready", "database": str(DB_PATH), "gemini_configured": bool(os.getenv("GEMINI_API_KEY"))}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", "8000")), reload=True)
