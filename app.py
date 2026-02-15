from flask import Flask, send_from_directory, make_response, request, jsonify
import os, sqlite3, datetime

app = Flask(__name__)

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "emails.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""CREATE TABLE IF NOT EXISTS subscribers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        subscribed_at TEXT NOT NULL
    )""")
    conn.commit()
    conn.close()

init_db()

@app.after_request
def add_no_cache(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

@app.route("/")
def index():
    return send_from_directory("templates", "index.html")

@app.route("/api/subscribe", methods=["POST"])
def subscribe():
    data = request.get_json()
    email = data.get("email", "").strip().lower()
    if not email or "@" not in email:
        return jsonify({"error": "Invalid email"}), 400
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute("INSERT OR IGNORE INTO subscribers (email, subscribed_at) VALUES (?, ?)",
                     (email, datetime.datetime.utcnow().isoformat()))
        conn.commit()
        conn.close()
        return jsonify({"success": True, "coupon": "nothingisforbidden"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/subscribers")
def list_subscribers():
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute("SELECT email, subscribed_at FROM subscribers ORDER BY id DESC").fetchall()
    conn.close()
    return jsonify([{"email": r[0], "date": r[1]} for r in rows])

@app.route("/static/<path:filename>")
def serve_static(filename):
    return send_from_directory("static", filename)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
