"""
Investment Dashboard — Backend
--------------------------------
Flask + yfinance + SQLite. No external API key required.

Run:
    pip install flask yfinance flask-cors
    python app.py

Then open http://localhost:5000 in your browser.
"""

import sqlite3
import time
import threading
import hashlib
import hmac
import os
import json
import traceback
from datetime import datetime
from functools import wraps

from flask import Flask, jsonify, request, session, send_from_directory, g, redirect, url_for
from flask_cors import CORS

try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False
    print("WARNING: yfinance not installed. Run: pip install yfinance")

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

DB_PATH = "dashboard.db"

# Read credentials from environment variables; fall back to defaults for local dev only.
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin123")

# Only 4 stocks allowed
TICKERS = {
    "TSLA": "Tesla",
    "AAPL": "Apple",
    "NVDA": "NVIDIA",
    "MSFT": "Microsoft",
}

PRICE_CACHE: dict = {}
PRICE_CACHE_LOCK = threading.Lock()
CACHE_TTL_SECONDS = 15

app = Flask(__name__, static_folder="static", template_folder="templates")
# Read secret key from environment in production; never commit a real key.
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key-change-in-production")
CORS(app, supports_credentials=True)


# ---------------------------------------------------------------------------
# Password helpers
# ---------------------------------------------------------------------------

def _hash_password(password: str) -> str:
    """Return a hex SHA-256 digest of the password.
    
    For production, replace this with bcrypt or argon2-cffi.
    """
    return hashlib.sha256(password.encode()).hexdigest()


def _check_password(plain: str, stored_hash: str) -> bool:
    return hmac.compare_digest(_hash_password(plain), stored_hash)


# ---------------------------------------------------------------------------
# Database helpers
# ---------------------------------------------------------------------------

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exception):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def ensure_tables():
    """Create tables if they do not already exist."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                name       TEXT    NOT NULL,
                email      TEXT    UNIQUE NOT NULL,
                password   TEXT    NOT NULL,
                created_at TEXT    NOT NULL
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS investments (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                user_name  TEXT    NOT NULL,
                email      TEXT    NOT NULL,
                symbol     TEXT    NOT NULL,
                shares     REAL    NOT NULL,
                buy_price  REAL    NOT NULL,
                created_at TEXT    NOT NULL
            )
            """
        )

        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_investments_user_name ON investments(user_name)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)"
        )

        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Error ensuring tables: {e}")
        print(traceback.format_exc())
        return False


def init_db():
    """Initialize database with all required tables."""
    try:
        db_dir = os.path.dirname(DB_PATH)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)
        ensure_tables()
        return True
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        print(traceback.format_exc())
        return False


def reset_database():
    """Drop all tables and recreate them."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        for (table_name,) in cursor.fetchall():
            if table_name != "sqlite_sequence":
                cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
                print(f"✅ Dropped table: {table_name}")

        conn.commit()
        conn.close()
        ensure_tables()
        print("✅ Database reset successfully")
        return True
    except Exception as e:
        print(f"❌ Error resetting database: {e}")
        print(traceback.format_exc())
        return False


# ============================================================
# Initialize database on startup
# ============================================================
print("🔄 Initializing database on app startup...")
init_db()
print("✅ Database initialization complete")


# ---------------------------------------------------------------------------
# Auth helpers
# ---------------------------------------------------------------------------

def login_required(fn):
    """Decorator: require a logged-in regular user."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get("user"):
            return jsonify({"error": "Authentication required"}), 401
        return fn(*args, **kwargs)
    return wrapper


def admin_required(fn):
    """Decorator: require an admin session."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get("is_admin"):
            return jsonify({"error": "Admin authentication required"}), 401
        return fn(*args, **kwargs)
    return wrapper


# ---------------------------------------------------------------------------
# Live price fetching
# ---------------------------------------------------------------------------

def _fast_info_get(fast_info, *keys):
    """Safely read attributes from yfinance's FastInfo object (not a dict)."""
    for key in keys:
        val = getattr(fast_info, key, None)
        if val is not None:
            return val
    return None


def fetch_price(symbol: str) -> dict:
    """Fetch the latest price + daily change for a symbol via yfinance."""
    now = time.time()
    with PRICE_CACHE_LOCK:
        cached = PRICE_CACHE.get(symbol)
        if cached and (now - cached["fetched_at"]) < CACHE_TTL_SECONDS:
            return cached

    if not YFINANCE_AVAILABLE:
        return {
            "symbol": symbol, "price": None, "change": None,
            "change_pct": None, "error": "yfinance not installed",
            "fetched_at": now,
        }

    try:
        ticker = yf.Ticker(symbol)
        # fast_info is an object — use getattr, not .get()
        info = ticker.fast_info
        price = _fast_info_get(info, "lastPrice", "last_price")
        prev_close = _fast_info_get(info, "previousClose", "previous_close")

        if price is None:
            hist = ticker.history(period="2d")
            if not hist.empty:
                price = float(hist["Close"].iloc[-1])
                prev_close = float(hist["Close"].iloc[-2]) if len(hist) > 1 else price

        change = (price - prev_close) if (price is not None and prev_close) else 0.0
        change_pct = (change / prev_close * 100) if prev_close else 0.0

        result = {
            "symbol": symbol,
            "price": round(float(price), 2) if price is not None else None,
            "change": round(float(change), 2),
            "change_pct": round(float(change_pct), 2),
            "error": None,
            "fetched_at": now,
        }
    except Exception as exc:
        result = {
            "symbol": symbol, "price": None, "change": None,
            "change_pct": None, "error": str(exc), "fetched_at": now,
        }

    with PRICE_CACHE_LOCK:
        PRICE_CACHE[symbol] = result
    return result


# ---------------------------------------------------------------------------
# Routes — static frontend
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    return send_from_directory("templates", "index.html")


@app.route("/dashboard")
def dashboard():
    if not session.get("user"):
        return redirect(url_for("index"))
    return send_from_directory("templates", "dashboard.html")


@app.route("/admin")
def admin_page():
    if not session.get("is_admin"):
        return redirect(url_for("index"))
    return send_from_directory("templates", "admin.html")


@app.route("/static/<path:path>")
def static_files(path):
    return send_from_directory("static", path)


# ---------------------------------------------------------------------------
# Routes — User Registration & Login
# ---------------------------------------------------------------------------

@app.route("/api/register", methods=["POST"])
def register():
    """Register a new user (passwords are hashed before storage)."""
    try:
        payload = request.get_json(force=True) or {}
    except Exception as e:
        return jsonify({"error": f"Invalid JSON: {e}"}), 400

    try:
        name = (payload.get("name") or "").strip()
        email = (payload.get("email") or "").strip().lower()
        password = payload.get("password", "").strip()

        if not name or not email or not password:
            return jsonify({"error": "Name, email, and password are required"}), 400
        if len(password) < 6:
            return jsonify({"error": "Password must be at least 6 characters"}), 400

        db = get_db()
        if db.execute("SELECT 1 FROM users WHERE email = ?", (email,)).fetchone():
            return jsonify({"error": "Email already registered"}), 400

        db.execute(
            "INSERT INTO users (name, email, password, created_at) VALUES (?, ?, ?, ?)",
            (name, email, _hash_password(password), datetime.utcnow().isoformat()),
        )
        db.commit()
        return jsonify({"ok": True, "message": "User registered successfully"}), 201
    except Exception as e:
        print(f"Error in register: {e}\n{traceback.format_exc()}")
        return jsonify({"error": "Registration failed"}), 500


@app.route("/api/login", methods=["POST"])
def login():
    """Authenticate a user."""
    try:
        payload = request.get_json(force=True) or {}
    except Exception as e:
        return jsonify({"error": f"Invalid JSON: {e}"}), 400

    try:
        email = (payload.get("email") or "").strip().lower()
        password = payload.get("password", "").strip()

        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400

        db = get_db()
        user = db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()

        # Use constant-time comparison to avoid timing attacks
        if not user or not _check_password(password, user["password"]):
            return jsonify({"error": "Invalid email or password"}), 401

        session["user"] = {"id": user["id"], "name": user["name"], "email": user["email"]}
        return jsonify({"ok": True, "user": dict(session["user"])})
    except Exception as e:
        print(f"Error in login: {e}\n{traceback.format_exc()}")
        return jsonify({"error": "Login failed"}), 500


@app.route("/api/logout", methods=["POST"])
def logout():
    """Log out the current regular user."""
    session.pop("user", None)
    return jsonify({"ok": True})


# ---------------------------------------------------------------------------
# Routes — live prices
# ---------------------------------------------------------------------------

@app.route("/api/prices")
@login_required
def api_prices():
    results = {}
    for symbol, label in TICKERS.items():
        data = fetch_price(symbol)
        data["label"] = label
        results[symbol] = data
    return jsonify({"prices": results, "server_time": datetime.utcnow().isoformat()})


# ---------------------------------------------------------------------------
# Routes — investments (user-facing: own records only)
# ---------------------------------------------------------------------------
    
@app.route("/api/investments", methods=["GET"])
@login_required
def list_investments():
    """Return investments belonging to the currently logged-in user only."""
    try:
        user_email = session["user"]["email"]
        user_name = session["user"]["name"]
        db = get_db()
        # Try to fetch by email first (primary key), fallback to user_name
        rows = db.execute(
            "SELECT * FROM investments WHERE email = ? OR user_name = ? ORDER BY created_at DESC",
            (user_email, user_name),
        ).fetchall()
        return jsonify([dict(r) for r in rows])
    except Exception as e:
        print(f"Error in list_investments: {e}\n{traceback.format_exc()}")
        return jsonify({"error": "Could not retrieve investments"}), 500


@app.route("/api/investments", methods=["POST"])
@login_required
def create_investment():
    """Logged-in user creates an investment (user identity taken from session)."""
    try:
        payload = request.get_json(force=True) or {}
    except Exception as e:
        return jsonify({"error": f"Invalid JSON: {e}"}), 400

    try:
        # Identity comes from the verified session, not the request body
        user_name = session["user"]["name"]
        user_email = session["user"]["email"]

        symbol = (payload.get("symbol") or "").strip().upper()
        shares = payload.get("shares")
        buy_price = payload.get("buy_price")

        if symbol not in TICKERS or shares is None or buy_price is None:
            return jsonify({"error": "Valid symbol, shares, and buy_price are required"}), 400

        try:
            shares = float(shares)
            buy_price = float(buy_price)
        except (TypeError, ValueError):
            return jsonify({"error": "shares and buy_price must be numbers"}), 400

        db = get_db()
        cur = db.execute(
            "INSERT INTO investments (user_name, email, symbol, shares, buy_price, created_at)"
            " VALUES (?, ?, ?, ?, ?, ?)",
            (user_name, user_email, symbol, shares, buy_price, datetime.utcnow().isoformat()),
        )
        db.commit()
        new_row = db.execute(
            "SELECT * FROM investments WHERE id = ?", (cur.lastrowid,)
        ).fetchone()
        return jsonify(dict(new_row)), 201
    except Exception as e:
        print(f"Error in create_investment: {e}\n{traceback.format_exc()}")
        return jsonify({"error": "Could not create investment"}), 500


# ---------------------------------------------------------------------------
# Routes — admin auth
# ---------------------------------------------------------------------------

@app.route("/api/admin/login", methods=["POST"])
def admin_login():
    try:
        payload = request.get_json(force=True) or {}
    except Exception as e:
        return jsonify({"error": f"Invalid JSON: {e}"}), 400

    username = payload.get("username", "")
    password = payload.get("password", "")
    if hmac.compare_digest(username, ADMIN_USERNAME) and hmac.compare_digest(password, ADMIN_PASSWORD):
        session["is_admin"] = True
        return jsonify({"ok": True})
    return jsonify({"error": "Invalid username or password"}), 401


@app.route("/api/admin/logout", methods=["POST"])
def admin_logout():
    session.pop("is_admin", None)
    return jsonify({"ok": True})


@app.route("/api/admin/session")
def admin_session():
    return jsonify({"is_admin": bool(session.get("is_admin"))})


# ---------------------------------------------------------------------------
# Routes — admin CRUD on investments (full control)
# ---------------------------------------------------------------------------

@app.route("/api/admin/investments", methods=["GET"])
@admin_required
def admin_list_investments():
    try:
        db = get_db()
        rows = db.execute(
            "SELECT * FROM investments ORDER BY created_at DESC"
        ).fetchall()
        return jsonify([dict(r) for r in rows])
    except Exception as e:
        print(f"Error in admin_list_investments: {e}\n{traceback.format_exc()}")
        return jsonify({"error": "Could not retrieve investments"}), 500


@app.route("/api/admin/investments", methods=["POST"])
@admin_required
def admin_create_investment():
    try:
        payload = request.get_json(force=True) or {}
    except Exception as e:
        return jsonify({"error": f"Invalid JSON: {e}"}), 400

    try:
        user_name = (payload.get("user_name") or "").strip()
        email = (payload.get("email") or "").strip()
        symbol = (payload.get("symbol") or "").strip().upper()
        shares = payload.get("shares")
        buy_price = payload.get("buy_price")

        if not user_name or symbol not in TICKERS or shares is None or buy_price is None:
            return jsonify({"error": "user_name, symbol, shares, and buy_price are required"}), 400

        try:
            shares = float(shares)
            buy_price = float(buy_price)
        except (TypeError, ValueError):
            return jsonify({"error": "shares and buy_price must be numbers"}), 400

        db = get_db()
        cur = db.execute(
            "INSERT INTO investments (user_name, email, symbol, shares, buy_price, created_at)"
            " VALUES (?, ?, ?, ?, ?, ?)",
            (user_name, email, symbol, shares, buy_price, datetime.utcnow().isoformat()),
        )
        db.commit()
        new_row = db.execute(
            "SELECT * FROM investments WHERE id = ?", (cur.lastrowid,)
        ).fetchone()
        return jsonify(dict(new_row)), 201
    except Exception as e:
        print(f"Error in admin_create_investment: {e}\n{traceback.format_exc()}")
        return jsonify({"error": "Could not create investment"}), 500


@app.route("/api/admin/investments/<int:investment_id>", methods=["PUT"])
@admin_required
def admin_update_investment(investment_id):
    try:
        payload = request.get_json(force=True) or {}
    except Exception as e:
        return jsonify({"error": f"Invalid JSON: {e}"}), 400

    try:
        db = get_db()
        existing = db.execute(
            "SELECT * FROM investments WHERE id = ?", (investment_id,)
        ).fetchone()
        if not existing:
            return jsonify({"error": "Investment not found"}), 404

        user_name = payload.get("user_name", existing["user_name"])
        email = payload.get("email", existing["email"])
        symbol = (payload.get("symbol", existing["symbol"]) or "").upper()
        shares = payload.get("shares", existing["shares"])
        buy_price = payload.get("buy_price", existing["buy_price"])

        if symbol not in TICKERS:
            return jsonify({"error": f"symbol must be one of {list(TICKERS.keys())}"}), 400

        try:
            shares = float(shares)
            buy_price = float(buy_price)
        except (TypeError, ValueError):
            return jsonify({"error": "shares and buy_price must be numbers"}), 400

        db.execute(
            "UPDATE investments SET user_name=?, email=?, symbol=?, shares=?, buy_price=? WHERE id=?",
            (user_name, email, symbol, shares, buy_price, investment_id),
        )
        db.commit()
        updated = db.execute(
            "SELECT * FROM investments WHERE id = ?", (investment_id,)
        ).fetchone()
        return jsonify(dict(updated))
    except Exception as e:
        print(f"Error in admin_update_investment: {e}\n{traceback.format_exc()}")
        return jsonify({"error": "Could not update investment"}), 500


@app.route("/api/admin/investments/<int:investment_id>", methods=["DELETE"])
@admin_required
def admin_delete_investment(investment_id):
    try:
        db = get_db()
        if not db.execute(
            "SELECT 1 FROM investments WHERE id = ?", (investment_id,)
        ).fetchone():
            return jsonify({"error": "Investment not found"}), 404
        db.execute("DELETE FROM investments WHERE id = ?", (investment_id,))
        db.commit()
        return jsonify({"ok": True, "deleted_id": investment_id})
    except Exception as e:
        print(f"Error in admin_delete_investment: {e}\n{traceback.format_exc()}")
        return jsonify({"error": "Could not delete investment"}), 500


@app.route("/api/admin/reset-db", methods=["POST"])
@admin_required
def reset_db_route():
    if reset_database():
        return jsonify({"ok": True, "message": "Database reset successfully"})
    return jsonify({"error": "Failed to reset database"}), 500


@app.route("/api/admin/verify-db", methods=["GET"])
@admin_required
def verify_db_route():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()
        return jsonify({"tables": tables, "ok": True})
    except Exception as e:
        return jsonify({"error": str(e), "ok": False}), 500


# ---------------------------------------------------------------------------
# Error handlers
# ---------------------------------------------------------------------------

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Resource not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500


@app.errorhandler(400)
def bad_request(error):
    return jsonify({"error": "Bad request"}), 400


@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({"error": "Method not allowed"}), 405



# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 60)
    print(" Investment Dashboard")
    print(" Landing Page : http://localhost:5000")
    print(" Dashboard    : http://localhost:5000/dashboard")
    print(" Admin        : http://localhost:5000/admin")
    print(f" Admin login  : {ADMIN_USERNAME} / {ADMIN_PASSWORD}")
    print(" Allowed stocks: TSLA, AAPL, NVDA, MSFT")
    print("=" * 60)
    app.run(debug=True, host="0.0.0.0", port=5000)
