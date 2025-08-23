import json
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# Load environment variables (Secrets)
import os
BOT_TOKEN = os.environ.get("8477083597:AAH1eWLudX3FSWmPHZ6vD_CjD_Zkzzlasoc")
OWNER_ID = int(os.environ.get("5168384940"))
SHORTLINK_API = os.environ.get("b13607c2b0e45265591b048e8308e56c7d5ed915")
SHORTLINK_DOMAIN = os.environ.get("SHORTLINK_DOMAIN")

# Data file
DATA_FILE = "data.json"

# Initialize data file if not exists
try:
    with open(DATA_FILE, "r") as f:
        data = json.load(f)
except FileNotFoundError:
    data = {"users": {}, "campaigns": {}}
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# Save function
def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if user_id not in data["users"]:
        data["users"][user_id] = {"balance": 0, "referrals": []}
        save_data()
    await update.message.reply_text(
        f"Welcome to Betboddy Bot!\nYour balance: {data['users'][user_id]['balance']} tk"
    )

# Campaigns command
async def campaigns(update: Update, context: ContextTypes.DEFAULT_TYPE):
    buttons = []
    for cid, camp in data["campaigns"].items():
        buttons.append([InlineKeyboardButton(camp["title"], callback_data=f"camp_{cid}")])
    if buttons:
        reply_markup = InlineKeyboardMarkup(buttons)
        await update.message.reply_text("Available Campaigns:", reply_markup=reply_markup)
    else:
        await update.message.reply_text("No campaigns available now.")

# Callback for campaign click
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = str(query.from_user.id)
    cid = query.data.split("_")[1]
    if cid in data["campaigns"]:
        # Add payout to user balance
        payout = data["campaigns"][cid]["payout"]
        data["users"][user_id]["balance"] += payout
        save_data()
        await query.edit_message_text(f"You completed: {data['campaigns'][cid]['title']}\nEarned: {payout} tk")

# Admin add campaign
async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != OWNER_ID:
        await update.message.reply_text("You are not admin.")
        return
    await update.message.reply_text("Admin Panel: Use /addcamp <title>|<url>|<payout>")

async def addcamp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != OWNER_ID:
        await update.message.reply_text("You are not admin.")
        return
    try:
        args = " ".join(context.args)
        title, url, payout = args.split("|")
        cid = str(len(data["campaigns"]) + 1)
        data["campaigns"][cid] = {"title": title.strip(), "url": url.strip(), "payout": int(payout.strip())}
        save_data()
        await update.message.reply_text(f"Campaign added: {title}")
    except:
        await update.message.reply_text("Format error! Use: /addcamp title|url|payout")

# Bot setup
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("campaigns", campaigns))
app.add_handler(CallbackQueryHandler(button))
app.add_handler(CommandHandler("admin", admin))
app.add_handler(CommandHandler("addcamp", addcamp))

print("Bot Started...")
app.run_polling()
