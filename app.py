from flask import Flask, send_from_directory, make_response, request, jsonify
import os, sqlite3, datetime, json
try:
    import urllib.request
except:
    pass

app = Flask(__name__)

DB_DIR = "/data" if os.path.isdir("/data") else os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(DB_DIR, "emails.db")

BOURBON_SYSTEM = """You are the Forbidden Bourbon assistant. You help visitors learn about Forbidden Bourbon and navigate the app. Keep answers concise (2-3 sentences max). Be warm and knowledgeable.

Key facts:
- Forbidden Bourbon is crafted by Marianne Eaves, Kentucky's first female Master Distiller
- Mashbill: 75% White Corn, 12% White Wheat, 13% Malted Barley — first bourbon made with this combination
- Two expressions: Small Batch (95.2 proof, 47.6% ABV, 5+ years) and Single Barrel (cask strength, 7+ years)
- Small Batch tasting notes: Nose has sweet floral, spice, oak, tobacco, citrus. Taste is warm spice, sorghum, oak sugar, dried fruit, baked bread. Finish is creamy, butter, sweet lingering warmth.
- Awards: Double Gold at New York & San Francisco International Spirits, Platinum at LA Spirits, Double Gold at Denver, Double Platinum at Ascot
- Featured in Forbes, Today Show (Craig Melvin called it "some of the best bourbon I've ever had"), Maxim
- Available in 12 states: KY, TN, GA, SC, NC, TX, CA, FL, NY, IL, OH, IN
- Buy online at shop.drinkforbidden.com
- Company: Small Batch Medicinal Spirits Company, LLC
- Website: drinkforbidden.com
- Contact: info@drinkforbidden.com
- App tabs: Home, Bourbons (product details), Find (store locator), Barrel (single barrel program coming soon), About (story & videos), News, Contact

If someone asks about the barrel program, say details are coming soon and to email info@drinkforbidden.com.
If asked about cocktail recipes, suggest the bourbon works great in an Old Fashioned, Manhattan, or Whiskey Sour given its warm spice and citrus notes.
Never make up information you don't have. If unsure, direct them to info@drinkforbidden.com."""

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

@app.route("/api/chat", methods=["POST"])
def chat():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return jsonify({"reply": "Chat assistant is not configured yet. Please email info@drinkforbidden.com for help."})
    data = request.get_json()
    messages = data.get("messages", [])
    try:
        payload = json.dumps({
            "model": "claude-sonnet-4-20250514",
            "max_tokens": 300,
            "system": BOURBON_SYSTEM,
            "messages": messages
        }).encode("utf-8")
        req = urllib.request.Request(
            "https://api.anthropic.com/v1/messages",
            data=payload,
            headers={
                "Content-Type": "application/json",
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01"
            },
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            reply = result.get("content", [{}])[0].get("text", "Sorry, I couldn't process that.")
            return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"reply": "I'm having trouble right now. Please email info@drinkforbidden.com for help."})

@app.route("/static/<path:filename>")
def serve_static(filename):
    return send_from_directory("static", filename)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
