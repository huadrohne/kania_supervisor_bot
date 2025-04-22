from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import os

BRANDING_PATH = "branding.png"

# Hauptmenü-Tastatur
main_keyboard = [['🔐 LOGIN FAHRER', '👑 LOGIN CEO']]
main_markup = ReplyKeyboardMarkup(main_keyboard, resize_keyboard=True, one_time_keyboard=False)

# Tastatur mit Zurück-Button
back_keyboard = [['🔙 ZURÜCK']]
back_markup = ReplyKeyboardMarkup(back_keyboard, resize_keyboard=True, one_time_keyboard=False)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Willkommen 👋\nBitte wähle deine Rolle:",
        reply_markup=main_markup
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text
    if msg == '🔐 LOGIN FAHRER':
        await update.message.reply_text("✅ Willkommen auf der Fahrer Plattform", reply_markup=back_markup)
        await update.message.reply_photo(photo=open(BRANDING_PATH, "rb"))
    elif msg == '👑 LOGIN CEO':
        await update.message.reply_text("✅ Willkommen auf der CEO Plattform", reply_markup=back_markup)
        await update.message.reply_photo(photo=open(BRANDING_PATH, "rb"))
    elif msg == '🔙 ZURÜCK':
        await update.message.reply_text("🔄 Zurück zum Hauptmenü", reply_markup=main_markup)
    else:
        await update.message.reply_text("Bitte wähle eine gültige Option.", reply_markup=main_markup)

if __name__ == '__main__':
    TOKEN = os.getenv("BOT_TOKEN")
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()