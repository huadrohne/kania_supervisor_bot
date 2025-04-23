import os
import datetime
import asyncio
from telegram import Update, ReplyKeyboardMarkup, InputFile
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    filters, ContextTypes
)

# Menü-Layouts
main_markup = ReplyKeyboardMarkup([['🚚 LOGIN FAHRER', '👔 LOGIN CEO']], resize_keyboard=True)
fahrer_markup = ReplyKeyboardMarkup([['⬅️ ZURÜCK']], resize_keyboard=True)
ceo_markup = ReplyKeyboardMarkup([['🏢 FIRMA', '⬅️ ZURÜCK']], resize_keyboard=True)
firma_markup = ReplyKeyboardMarkup([['👤 FAHRER', '⬅️ ZURÜCK']], resize_keyboard=True)

RESET_MINUTES = 2

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cid = update.effective_chat.id

    # Branding anzeigen
    with open("branding.png", "rb") as img:
        await context.bot.send_photo(chat_id=cid, photo=InputFile(img))
    await update.message.reply_text("Lizensiert für Kania Schüttguttransporte")

    await asyncio.sleep(3)
    await update.message.reply_text("Willkommen 👋\nBitte wähle deine Rolle:", reply_markup=main_markup)
    context.chat_data[cid] = {"state": "start", "last_active": datetime.datetime.utcnow()}

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cid = update.effective_chat.id
    msg = update.message.text
    context.chat_data[cid]["last_active"] = datetime.datetime.utcnow()

    if msg == "⬅️ ZURÜCK":
        state = context.chat_data[cid].get("state", "start")
        if state == "fahrer" or state == "ceo":
            await update.message.reply_text("Zurück zum Hauptmenü", reply_markup=main_markup)
            context.chat_data[cid]["state"] = "start"
        elif state == "firma":
            await update.message.reply_text("Zurück zur CEO Plattform", reply_markup=ceo_markup)
            context.chat_data[cid]["state"] = "ceo"

    elif msg == "🚚 LOGIN FAHRER":
        await update.message.reply_text("✅ Willkommen auf der Fahrer Plattform", reply_markup=fahrer_markup)
        context.chat_data[cid]["state"] = "fahrer"

    elif msg == "👔 LOGIN CEO":
        await update.message.reply_text("✅ Willkommen auf der CEO Plattform", reply_markup=ceo_markup)
        context.chat_data[cid]["state"] = "ceo"

    elif msg == "🏢 FIRMA":
        await update.message.reply_text("🏢 Firmenbereich", reply_markup=firma_markup)
        context.chat_data[cid]["state"] = "firma"

    elif msg == "👤 FAHRER":
        await update.message.reply_text("📋 Fahrerübersicht: Keine Fahrer vorhanden.", reply_markup=ReplyKeyboardMarkup([['⬅️ ZURÜCK']], resize_keyboard=True))
        context.chat_data[cid]["state"] = "fahrer_alle"

if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)

    TOKEN = os.getenv("BOT_TOKEN")
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling()