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

main_markup = ReplyKeyboardMarkup([['🚚 LOGIN FAHRER', '👔 LOGIN CEO']], resize_keyboard=True)
ceo_markup = ReplyKeyboardMarkup([['🏢 FIRMA', '⬅️ ZURÜCK']], resize_keyboard=True)
firma_markup = ReplyKeyboardMarkup([['👷 FAHRER', '⬅️ ZURÜCK']], resize_keyboard=True)
fahrer_markup = ReplyKeyboardMarkup([['📋 ALLE', '🔄 ERSATZ', '⬅️ ZURÜCK']], resize_keyboard=True)
alle_markup = ReplyKeyboardMarkup([['🆕 NEU', '✏️ ÄNDERN', '⬅️ ZURÜCK']], resize_keyboard=True)

RESET_MINUTES = 2
BRANDING_PATH = "branding.png"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cid = update.effective_chat.id
    context.chat_data[cid] = {"state": "start", "last_active": datetime.datetime.utcnow()}

    # alte Statusnachrichten löschen
    for key in ["welcome_msg", "plattform_msg"]:
        if mid := context.chat_data[cid].get(key):
            try: await context.bot.delete_message(cid, mid)
            except: pass

    msg = await update.message.reply_text("Willkommen 👋\nBitte wähle deine Rolle:", reply_markup=main_markup)
    context.chat_data[cid]["welcome_msg"] = msg.message_id

async def reset_user_menu(context: ContextTypes.DEFAULT_TYPE):
    now = datetime.datetime.utcnow()
    for chat_id, data in context.chat_data.items():
        last_active = data.get("last_active")
        if last_active and (now - last_active).total_seconds() > RESET_MINUTES * 60:
            await context.bot.send_message(chat_id, "⏳ Zurück zum Hauptmenü", reply_markup=main_markup)
            context.chat_data[chat_id] = {"state": "start", "last_active": now}

async def delete_last_status(update, context):
    cid = update.effective_chat.id
    for key in ["plattform_msg", "welcome_msg"]:
        if mid := context.chat_data[cid].get(key):
            try: await context.bot.delete_message(cid, mid)
            except: pass
        context.chat_data[cid][key] = None

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text
    cid = update.effective_chat.id
    await update.message.delete()
    chat_state = context.chat_data.setdefault(cid, {"state": "start", "last_active": datetime.datetime.utcnow()})
    chat_state["last_active"] = datetime.datetime.utcnow()

    await delete_last_status(update, context)

    if msg == "🚚 LOGIN FAHRER":
        m = await context.bot.send_message(cid, "✅ Willkommen auf der Fahrer Plattform", reply_markup=ReplyKeyboardMarkup([['⬅️ ZURÜCK']], resize_keyboard=True))
        img = await context.bot.send_photo(cid, photo=open(BRANDING_PATH, "rb"))
        await asyncio.sleep(3)
        await img.delete()
        chat_state["plattform_msg"] = m.message_id
        chat_state["state"] = "login_fahrer"

    elif msg == "👔 LOGIN CEO":
        m = await context.bot.send_message(cid, "✅ Willkommen auf der CEO Plattform", reply_markup=ceo_markup)
        img = await context.bot.send_photo(cid, photo=open(BRANDING_PATH, "rb"))
        await asyncio.sleep(3)
        await img.delete()
        chat_state["plattform_msg"] = m.message_id
        chat_state["state"] = "ceo"

    elif msg == "🏢 FIRMA":
        m = await context.bot.send_message(cid, "Firmenbereich", reply_markup=firma_markup, reply_markup_message_id=0)
        chat_state["plattform_msg"] = m.message_id
        chat_state["state"] = "firma"

    elif msg == "👷 FAHRER":
        m = await context.bot.send_message(cid, "📂 LOGIN CEO ➜ FIRMA ➜ FAHRER", reply_markup=fahrer_markup, reply_markup_message_id=0)
        chat_state["plattform_msg"] = m.message_id
        chat_state["state"] = "fahrer"

    elif msg == "📋 ALLE":
        fahrerliste = context.application.bot_data.get("fahrer", [])
        text = "Keine Fahrer vorhanden." if not fahrerliste else "\n".join([f"{f['id']} – {f['vorname']} {f['nachname']} {f['sprache']} {f['nationalität']}" for f in fahrerliste])
        await context.bot.send_message(cid, f"📋 Fahrerübersicht:\n{text}")
        chat_state["state"] = "alle"

    elif msg == "⬅️ ZURÜCK":
        match chat_state.get("state"):
            case "alle":
                m = await context.bot.send_message(cid, "⬅️ Zurück zum Fahrerbereich", reply_markup=fahrer_markup)
                chat_state["plattform_msg"] = m.message_id
                chat_state["state"] = "fahrer"
            case "fahrer":
                m = await context.bot.send_message(cid, "⬅️ Zurück zum Firmenbereich", reply_markup=firma_markup)
                chat_state["plattform_msg"] = m.message_id
                chat_state["state"] = "firma"
            case _:
                m = await context.bot.send_message(cid, "⬅️ Zurück zum Hauptmenü", reply_markup=main_markup)
                chat_state["plattform_msg"] = m.message_id
                chat_state["state"] = "start"
                # === Fahrer anlegen ===
async def neu_fahrer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.delete()
    await context.bot.send_message(update.effective_chat.id, "Bitte gib den Vornamen des Fahrers ein:")
    return VORNAME

async def vorname(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["fahrer"] = {"vorname": update.message.text}
    await update.message.delete()
    await update.message.reply_text("Nachname:", reply_markup=ReplyKeyboardRemove())
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

# === Bot starten ===
if __name__ == '__main__':
    app = ApplicationBuilder().token(os.getenv("BOT_TOKEN")).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

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

    app.job_queue.run_repeating(reset_user_menu, interval=60, first=60)
    app.run_polling()