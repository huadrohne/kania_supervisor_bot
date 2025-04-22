from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode
import os

# Pfad zum Branding-Bild (Railway nutzt lokalen Pfad im Root-Ordner)
BRANDING_PATH = "branding.png"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [['🔐 LOGIN FAHRER', '👑 LOGIN CEO']]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Willkommen 👋\nBitte wähle deine Rolle:", reply_markup=reply_markup)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text
    if msg == '🔐 LOGIN FAHRER':
        await update.message.reply_text("✅ Willkommen auf der Fahrer Plattform")
        await update.message.reply_photo(photo=open(BRANDING_PATH, "rb"))
    elif msg == '👑 LOGIN CEO':
        await update.message.reply_text("✅ Willkommen auf der CEO Plattform")
        await update.message.reply_photo(photo=open(BRANDING_PATH, "rb"))
    else:
        await update.message.reply_text("Bitte wähle eine gültige Option.")

if __name__ == '__main__':
    TOKEN = os.getenv("BOT_TOKEN")
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()