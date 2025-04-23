import asyncio
import datetime
import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    filters, ContextTypes
)

main_markup = ReplyKeyboardMarkup([['🚚 LOGIN FAHRER', '👔 LOGIN CEO']], resize_keyboard=True)
RESET_MINUTES = 2

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cid = update.effective_chat.id
    await update.message.reply_text("Willkommen 👋\nBitte wähle deine Rolle:", reply_markup=main_markup)
    context.chat_data[cid] = {
        "state": "start",
        "last_active": datetime.datetime.utcnow()
    }

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cid = update.effective_chat.id
    msg = update.message.text
    context.chat_data[cid]["last_active"] = datetime.datetime.utcnow()

    if msg == "⬅️ ZURÜCK":
        await update.message.reply_text("Zurück zum Hauptmenü", reply_markup=main_markup)
        context.chat_data[cid]["state"] = "start"

if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)

    TOKEN = os.getenv("BOT_TOKEN")
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling()