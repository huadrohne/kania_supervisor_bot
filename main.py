import asyncio
import datetime
import os
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    filters, ContextTypes, ConversationHandler
)

# Konstanten
(VORNAME, NACHNAME, GEBURTSTAG, NATIONALITÄT, SPRACHE, MOBIL, EINTRITT, PIN) = range(8)

FLAGGEN = {
    "deutschland": "🇩🇪", "polen": "🇵🇱", "türkei": "🇹🇷", "rumänien": "🇷🇴", "italien": "🇮🇹"
}
SPRACHEN = {
    "deutsch": "🗣️🇩🇪", "polnisch": "🗣️🇵🇱", "englisch": "🗣️🇬🇧", "türkisch": "🗣️🇹🇷"
}

def markup(buttons):
    return ReplyKeyboardMarkup(
        buttons,
        resize_keyboard=True,
        one_time_keyboard=False,
        is_persistent=True,
        selective=True,
        input_field_placeholder="",
        placeholder=""
    )

# Menüs
main_markup = markup([['🚚 LOGIN FAHRER', '👔 LOGIN CEO']])
ceo_markup = markup([['🏢 FIRMA', '⬅️ ZURÜCK']])
firma_markup = markup([['👷 FAHRER', '⬅️ ZURÜCK']])
fahrer_markup = markup([['📋 ALLE', '🔄 ERSATZ', '⬅️ ZURÜCK']])
ersatz_markup = markup([['⬅️ ZURÜCK']])
alle_markup = markup([['🆕 NEU', '✏️ ÄNDERN', '⬅️ ZURÜCK']])
fahrer_login_markup = markup([['⬅️ ZURÜCK']])

RESET_MINUTES = 2
BRANDING_PATH = "branding.png"

# Start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cid = update.effective_chat.id
    if update.message:
        await update.message.delete()
    msg = await context.bot.send_message(cid, "Willkommen 👋\nBitte wähle deine Rolle:", reply_markup=main_markup)
    context.chat_data[cid] = {
        "state": "start",
        "last_active": datetime.datetime.utcnow(),
        "start_msg": msg.message_id
    }

# Reset bei Inaktivität
async def reset_user_menu(context: ContextTypes.DEFAULT_TYPE):
    now = datetime.datetime.utcnow()
    for chat_id, data in context.chat_data.items():
        last_active = data.get("last_active")
        if last_active and (now - last_active).total_seconds() > RESET_MINUTES * 60:
            await context.bot.send_message(chat_id, "⏳ Zurück zum Hauptmenü", reply_markup=main_markup)
            context.chat_data[chat_id] = {"state": "start", "last_active": now}

# Button Handling
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text
    cid = update.effective_chat.id
    await update.message.delete()

    chat_state = context.chat_data.setdefault(cid, {"state": "start", "last_active": datetime.datetime.utcnow()})
    chat_state["last_active"] = datetime.datetime.utcnow()

    if chat_state.get("status_msg"):
        try:
            await context.bot.delete_message(cid, chat_state["status_msg"])
        except:
            pass
        chat_state["status_msg"] = None

    if chat_state.get("start_msg"):
        try:
            await context.bot.delete_message(cid, chat_state["start_msg"])
        except:
            pass
        chat_state["start_msg"] = None

    if msg == "🚚 LOGIN FAHRER":
        m = await context.bot.send_message(cid, "✅ Willkommen auf der Fahrer Plattform", reply_markup=fahrer_login_markup)
        branding = await context.bot.send_photo(cid, photo=open(BRANDING_PATH, "rb"))
        lizenz = await context.bot.send_message(cid, "Lizensiert für Kania Schüttguttransporte")
        await asyncio.sleep(2)
        await branding.delete()
        await lizenz.delete()
        chat_state["state"] = "login_fahrer"
        chat_state["status_msg"] = m.message_id

    elif msg == "👔 LOGIN CEO":
        m = await context.bot.send_message(cid, "✅ Willkommen auf der CEO Plattform", reply_markup=ceo_markup)
        branding = await context.bot.send_photo(cid, photo=open(BRANDING_PATH, "rb"))
        lizenz = await context.bot.send_message(cid, "Lizensiert für Kania Schüttguttransporte")
        await asyncio.sleep(2)
        await branding.delete()
        await lizenz.delete()
        chat_state["state"] = "ceo"
        chat_state["status_msg"] = m.message_id

    elif msg == "🏢 FIRMA":
        m = await context.bot.send_message(cid, "LOGIN CEO/ FIRMA", reply_markup=firma_markup)
        chat_state["state"] = "firma"
        chat_state["status_msg"] = m.message_id

    elif msg == "👷 FAHRER":
        m = await context.bot.send_message(cid, "LOGIN CEO/ FIRMA/ FAHRER", reply_markup=fahrer_markup)
        chat_state["state"] = "fahrer"
        chat_state["status_msg"] = m.message_id

    elif msg == "🔄 ERSATZ":
        m = await context.bot.send_message(cid, "LOGIN CEO/ FIRMA/ FAHRER/ ERSATZ", reply_markup=ersatz_markup)
        chat_state["state"] = "ersatz"
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
        if chat_state.get("state") == "alle" or chat_state.get("state") == "ersatz":
            m = await context.bot.send_message(cid, "LOGIN CEO/ FIRMA/ FAHRER", reply_markup=fahrer_markup)
            chat_state["state"] = "fahrer"
            chat_state["status_msg"] = m.message_id
        elif chat_state.get("state") == "fahrer":
            m = await context.bot.send_message(cid, "LOGIN CEO/ FIRMA", reply_markup=firma_markup)
            chat_state["state"] = "firma"
            chat_state["status_msg"] = m.message_id
        elif chat_state.get("state") == "login_fahrer":
            msg = await context.bot.send_message(cid, "Willkommen 👋\nBitte wähle deine Rolle:", reply_markup=main_markup)
            chat_state["state"] = "start"
            chat_state["start_msg"] = msg.message_id
        else:
            msg = await context.bot.send_message(cid, "Willkommen 👋\nBitte wähle deine Rolle:", reply_markup=main_markup)
            chat_state["state"] = "start"
            chat_state["start_msg"] = msg.message_id

# === Fahreranlage ===
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
    await update.message.reply_text("✅ Fahrer gespeichert.")
    text = "\n".join([f"{f['id']} – {f['vorname']} {f['nachname']} {f['sprache']} {f['nationalität']}" for f in fahrerliste])
    await update.message.reply_text(f"📋 Fahrerübersicht:\n{text}", reply_markup=alle_markup)
    return ConversationHandler.END

# === Main Start ===
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