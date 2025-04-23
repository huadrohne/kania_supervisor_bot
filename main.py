import asyncio
import datetime
import os
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    filters, ContextTypes, ConversationHandler
)

(VORNAME, NACHNAME, GEBURTSTAG, NATIONALITÄT, SPRACHE, MOBIL, EINTRITT, PIN) = range(8)

FLAGGEN = {
    "deutschland": "🇩🇪", "polen": "🇵🇱", "türkei": "🇹🇷", "rumänien": "🇷🇴", "italien": "🇮🇹"
}
SPRACHEN = {
    "deutsch": "🗣️🇩🇪", "polnisch": "🗣️🇵🇱", "englisch": "🗣️🇬🇧", "türkisch": "🗣️🇹🇷"
}

main_markup = ReplyKeyboardMarkup([['🚚 LOGIN FAHRER', '👔 LOGIN CEO']], resize_keyboard=True, one_time_keyboard=True)
ceo_markup = ReplyKeyboardMarkup([['🏢 FIRMA', '⬅️ ZURÜCK']], resize_keyboard=True, one_time_keyboard=True)
firma_markup = ReplyKeyboardMarkup([['👷 FAHRER', '⬅️ ZURÜCK']], resize_keyboard=True, one_time_keyboard=True)
fahrer_markup = ReplyKeyboardMarkup([['📋 ALLE', '🔄 ERSATZ', '⬅️ ZURÜCK']], resize_keyboard=True, one_time_keyboard=True)
alle_markup = ReplyKeyboardMarkup([['🆕 NEU', '✏️ ÄNDERN', '⬅️ ZURÜCK']], resize_keyboard=True, one_time_keyboard=True)
fahrer_login_markup = ReplyKeyboardMarkup([['⬅️ ZURÜCK']], resize_keyboard=True, one_time_keyboard=True)

RESET_MINUTES = 2
BRANDING_PATH = "branding.png"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.chat_data[update.effective_chat.id] = {"state": "start", "last_active": datetime.datetime.utcnow()}
    await update.message.reply_text("Willkommen 👋\nBitte wähle deine Rolle:", reply_markup=main_markup)

async def reset_user_menu(context: ContextTypes.DEFAULT_TYPE):
    now = datetime.datetime.utcnow()
    for chat_id, data in context.chat_data.items():
        last_active = data.get("last_active")
        if last_active and (now - last_active).total_seconds() > RESET_MINUTES * 60:
            await context.bot.send_message(chat_id, "⏳ Zurück zum Hauptmenü", reply_markup=main_markup)
            context.chat_data[chat_id] = {"state": "start", "last_active": now}

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text
    cid = update.effective_chat.id
    await update.message.delete()

    chat_state = context.chat_data.setdefault(cid, {"state": "start", "last_active": datetime.datetime.utcnow()})
    chat_state["last_active"] = datetime.datetime.utcnow()

    old_message = chat_state.get("status_msg")
    if old_message:
        try:
            await context.bot.delete_message(cid, old_message)
        except:
            pass
        chat_state["status_msg"] = None

    if msg == "🚚 LOGIN FAHRER":
        m = await context.bot.send_message(cid, "✅ Willkommen auf der Fahrer Plattform", reply_markup=fahrer_login_markup)
        img = await context.bot.send_photo(cid, photo=open(BRANDING_PATH, "rb"))
        await asyncio.sleep(3)
        await img.delete()
        chat_state["state"] = "login_fahrer"
        chat_state["status_msg"] = m.message_id

    elif msg == "👔 LOGIN CEO":
        m = await context.bot.send_message(cid, "✅ Willkommen auf der CEO Plattform", reply_markup=ceo_markup)
        img = await context.bot.send_photo(cid, photo=open(BRANDING_PATH, "rb"))
        await asyncio.sleep(3)
        await img.delete()
        chat_state["state"] = "ceo"
        chat_state["status_msg"] = m.message_id

    elif msg == "🏢 FIRMA":
        m = await context.bot.send_message(cid, "Firmenbereich", reply_markup=firma_markup)
        chat_state["state"] = "firma"
        chat_state["status_msg"] = m.message_id

    elif msg == "👷 FAHRER":
        m = await context.bot.send_message(cid, "Fahrerbereich", reply_markup=fahrer_markup)
        chat_state["state"] = "fahrer"
        chat_state["status_msg"] = m.message_id

    elif msg == "📋 ALLE":
        fahrerliste = context.application.bot_data.get("fahrer", [])
        if not fahrerliste:
            text = "Keine Fahrer vorhanden."
        else:
            text = "\n".join([f"{f['id']} – {f['vorname']} {f['nachname']} {f['sprache']} {f['nationalität']}" for f in fahrerliste])
        m = await context.bot.send_message(cid, f"📋 Fahrerübersicht:\n{text}", reply_markup=alle_markup)
        chat_state["state"] = "alle"
        chat_state["status_msg"] = m.message_id

    elif msg == "⬅️ ZURÜCK":
        if chat_state.get("state") == "alle":
            m = await context.bot.send_message(cid, "⬅️ Zurück zum Fahrerbereich", reply_markup=fahrer_markup)
            chat_state["state"] = "fahrer"
            chat_state["status_msg"] = m.message_id
        elif chat_state.get("state") == "fahrer":
            m = await context.bot.send_message(cid, "⬅️ Zurück zum Firmenbereich", reply_markup=firma_markup)
            chat_state["state"] = "firma"
            chat_state["status_msg"] = m.message_id
        elif chat_state.get("state") == "login_fahrer":
            m = await context.bot.send_message(cid, "⬅️ Zurück zum Hauptmenü", reply_markup=main_markup)
            chat_state["state"] = "start"
            chat_state["status_msg"] = m.message_id
        else:
            await context.bot.send_message(cid, "⬅️ Zurück zum Hauptmenü", reply_markup=main_markup)
            chat_state["state"] = "start"

# === Bot starten ===
if __name__ == '__main__':
    app = ApplicationBuilder().token(os.getenv("BOT_TOKEN")).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.job_queue.run_repeating(reset_user_menu, interval=60, first=60)
    app.run_polling()