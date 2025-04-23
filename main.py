import asyncio
import datetime
import os
from telegram import Update, ReplyKeyboardMarkup
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

main_markup = ReplyKeyboardMarkup([['🚚 LOGIN FAHRER', '👔 LOGIN CEO']], resize_keyboard=True)
ceo_markup = ReplyKeyboardMarkup([['🏢 FIRMA', '⬅️ ZURÜCK']], resize_keyboard=True)
firma_markup = ReplyKeyboardMarkup([['👷 FAHRER', '⬅️ ZURÜCK']], resize_keyboard=True)
fahrer_markup = ReplyKeyboardMarkup([['📋 ALLE', '🔄 ERSATZ', '⬅️ ZURÜCK']], resize_keyboard=True)
alle_markup = ReplyKeyboardMarkup([['🆕 NEU', '✏️ ÄNDERN', '⬅️ ZURÜCK']], resize_keyboard=True)

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
    chat_state = context.chat_data.setdefault(cid, {"state": "start", "last_active": datetime.datetime.utcnow()})
    context.chat_data[cid]["last_active"] = datetime.datetime.utcnow()

    await update.message.delete()

    if msg == "🚚 LOGIN FAHRER":
        m = await context.bot.send_message(cid, "✅ Willkommen auf der Fahrer Plattform", reply_markup=ReplyKeyboardMarkup([['⬅️ ZURÜCK']], resize_keyboard=True))
        img = await context.bot.send_photo(cid, photo=open(BRANDING_PATH, "rb"))
        await asyncio.sleep(3)
        await img.delete()

    elif msg == "👔 LOGIN CEO":
        m = await context.bot.send_message(cid, "✅ Willkommen auf der CEO Plattform", reply_markup=ceo_markup)
        img = await context.bot.send_photo(cid, photo=open(BRANDING_PATH, "rb"))
        await asyncio.sleep(3)
        await img.delete()

    elif msg == "🏢 FIRMA":
        await context.bot.send_message(cid, "Firmenbereich", reply_markup=firma_markup)
        chat_state["prev"] = "ceo"
        chat_state["state"] = "firma"

    elif msg == "👷 FAHRER":
        await context.bot.send_message(cid, "Fahrerbereich", reply_markup=fahrer_markup)
        chat_state["prev"] = "firma"
        chat_state["state"] = "fahrer"

    elif msg == "📋 ALLE":
        fahrerliste = context.application.bot_data.get("fahrer", [])
        if not fahrerliste:
            text = "Keine Fahrer vorhanden."
        else:
            text = "\n".join([f"{f['id']} – {f['vorname']} {f['nachname']} {f['sprache']} {f['nationalität']}" for f in fahrerliste])
        await context.bot.send_message(cid, f"📋 Fahrerübersicht:\n{text}", reply_markup=alle_markup)
        chat_state["prev"] = "fahrer"
        chat_state["state"] = "alle"

    elif msg == "⬅️ ZURÜCK":
        if chat_state.get("state") == "fahrer":
            await context.bot.send_message(cid, "⬅️ Zurück zur Firma", reply_markup=firma_markup)
            chat_state["state"] = "firma"
            chat_state["prev"] = "ceo"
        elif chat_state.get("state") == "ceo":
            await context.bot.send_message(cid, "⬅️ Zurück zum Hauptmenü", reply_markup=main_markup)
            chat_state["state"] = "start"
        elif chat_state.get("state") == "start":
            await context.bot.send_message(cid, "⬅️ Bereits im Hauptmenü", reply_markup=main_markup)
        else:
            await context.bot.send_message(cid, "⬅️ Zurück", reply_markup=main_markup)
            chat_state["state"] = "start"

# === Fahrer anlegen ===
async def neu_fahrer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.delete()
    await context.bot.send_message(update.effective_chat.id, "Bitte gib den Vornamen des Fahrers ein:")
    return VORNAME

async def vorname(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["fahrer"] = {"vorname": update.message.text}
    await update.message.delete()
    await update.message.reply_text("Nachname:")
    return NACHNAME

async def nachname(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["fahrer"]["nachname"] = update.message.text
    await update.message.delete()
    await update.message.reply_text("Geburtstag:")
    return GEBURTSTAG

async def geburtstag(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["fahrer"]["geburtstag"] = update.message.text
    await update.message.delete()
    await update.message.reply_text("Nationalität:")
    return NATIONALITÄT

async def nationalität(update: Update, context: ContextTypes.DEFAULT_TYPE):
    flag = FLAGGEN.get(update.message.text.lower(), "🌍")
    context.user_data["fahrer"]["nationalität"] = flag
    await update.message.delete()
    await update.message.reply_text("Sprache:")
    return SPRACHE

async def sprache(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sprache = SPRACHEN.get(update.message.text.lower(), "🗣️")
    context.user_data["fahrer"]["sprache"] = sprache
    await update.message.delete()
    await update.message.reply_text("Mobilnummer:")
    return MOBIL

async def mobil(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["fahrer"]["mobil"] = update.message.text
    await update.message.delete()
    await update.message.reply_text("Angestellt seit:")
    return EINTRITT

async def eintritt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["fahrer"]["seit"] = update.message.text
    await update.message.delete()
    await update.message.reply_text("4-stelliger PIN:")
    return PIN

async def pin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["fahrer"]["pin"] = update.message.text
    fahrerliste = context.application.bot_data.setdefault("fahrer", [])
    neue_id = f"F{len(fahrerliste)+1:04}"
    context.user_data["fahrer"]["id"] = neue_id
    fahrerliste.append(context.user_data["fahrer"])
    await update.message.delete()
    await update.message.reply_text("✅ Fahrer gespeichert. Übersicht:")
    text = "\n".join([f"{f['id']} – {f['vorname']} {f['nachname']} {f['sprache']} {f['nationalität']}" for f in fahrerliste])
    await update.message.reply_text(f"📋 Fahrerübersicht:\n{text}", reply_markup=alle_markup)
    return ConversationHandler.END

# === Setup ===
if __name__ == '__main__':
    app = ApplicationBuilder().token(os.getenv("BOT_TOKEN")).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.job_queue.run_repeating(reset_user_menu, interval=60, first=60)

    conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^(🆕 NEU|🆕\\sNEU)$"), neu_fahrer)],
        states={
            VORNAME: [MessageHandler(filters.TEXT, vorname)],
            NACHNAME: [MessageHandler(filters.TEXT, nachname)],
            GEBURTSTAG: [MessageHandler(filters.TEXT, geburtstag)],
            NATIONALITÄT: [MessageHandler(filters.TEXT, nationalität)],
            SPRACHE: [MessageHandler(filters.TEXT, sprache)],
            MOBIL: [MessageHandler(filters.TEXT, mobil)],
            EINTRITT: [MessageHandler(filters.TEXT, eintritt)],
            PIN: [MessageHandler(filters.TEXT, pin)],
        },
        fallbacks=[]
    )
    app.add_handler(conv)
    app.run_polling()