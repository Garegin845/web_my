from flask import Flask, request, jsonify, render_template
import json
import os
from telegram.ext import WebAppInfoHandler

# Բոտի initialization
app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))

# Նոր WebApp data handler
async def webapp_data_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.web_app_data:   # ստուգում, որ WebApp-ից տվյալներ կան
        await webapp_data(update, context)

app.add_handler(CallbackQueryHandler(webapp_data_handler))

app = Flask(__name__)

USERS_FILE = "users.json"

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=4, ensure_ascii=False)

@app.route("/")
def index():
    return render_template("index.html")  # Login/Register HTML

@app.route("/register", methods=["POST"])
def register():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    users = load_users()
    if any(u["username"] == username for u in users):
        return jsonify({"success": False, "message": "Օգտվողը արդեն գոյություն ունի"})
    
    users.append({"username": username, "password": password})
    save_users(users)
    return jsonify({"success": True, "message": "Գրանցումը հաջողությամբ ավարտվեց"})

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    users = load_users()
    user = next((u for u in users if u["username"] == username and u["password"] == password), None)
    if user:
        return jsonify({"success": True, "message": f"Բարի գալուստ {username}"})
    return jsonify({"success": False, "message": "Սխալ օգտվողի անուն կամ գաղտնաբառ"})

if __name__ == "__main__":
    app.run(port=8000)
