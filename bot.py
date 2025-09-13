import json
import hashlib
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = "8215149186:AAExc5YdyNSZatM4npizcuvkV8z1ulG7lk8"
USERS_FILE = "users.json"

def load_users():
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2, ensure_ascii=False)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton(
            "🚀 Գրանցվել / Մուտք WebApp",
            web_app=WebAppInfo(url="https://garegin845.github.io/web_my/")
        )],
        [InlineKeyboardButton("ℹ️ Օգնություն", callback_data="help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Բարև ✨\nԸնտրիր գործողություն՝",
        reply_markup=reply_markup
    )

# Callback
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data=="help":
        await query.edit_message_text("Օգտագործիր WebApp կոճակը՝ գրանցվելու կամ մուտք գործելու համար")
    else:
        await query.edit_message_text("Այս ընտրանքն դեռ չի հասանելի 😅")

# WebApp Data
async def handle_webapp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if not msg or not msg.web_app_data:
        return
    try:
        payload = json.loads(msg.web_app_data.data)
        logger.info(f"Payload: {payload}")
    except Exception as e:
        await msg.reply_text(f"❌ Սխալ JSON ({e})")
        return

    action = payload.get("action")
    username = payload.get("username", "").strip()
    password = payload.get("password", "")

    if not username or not password:
        await msg.reply_text("❌ Լրացրու username և password")
        return

    users = load_users()
    hpass = hash_password(password)

    if action=="register":
        if username in users:
            await msg.reply_text(f"❌ {username} արդեն գրանցված է")
        else:
            users[username] = {"password": hpass}
            save_users(users)
            await msg.reply_text(f"✅ Գրանցվեցիր որպես {username}")

    elif action=="login":
        if username in users and users[username]["password"]==hpass:
            await msg.reply_text(f"🔑 Մուտք հաջողված {username}!")
        else:
            await msg.reply_text("❌ Սխալ անուն կամ գաղտնաբառ")
    else:
        await msg.reply_text(f"⚠️ Անհայտ գործողություն {action}")

    # Ուղարկել Telegram-ում գրանցված օգտատերերի ցուցակը
    if users:
        user_list = list(users.keys())
        await msg.reply_text(f"📋 Գրանցված օգտատերեր: {', '.join(user_list)}")
    else:
        await msg.reply_text("📋 Գրանցված օգտատերեր չկան")

# Run bot
def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, handle_webapp))
    logger.info("Bot started...")
    app.run_polling()

if __name__=="__main__":
    main()
