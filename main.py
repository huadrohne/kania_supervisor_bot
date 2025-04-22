import asyncio
import datetime
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    ConversationHandler,
    filters,
)
import os

BRANDING_PATH = "branding.png"
RESET_MINUTES = 2

# Zustände für Fahrer-Anlage
(
    VORNAME,
    NACHNAME,
    GEBURTSTAG,
    NATIONALITÄT,
    SPRACHE,
    MOBIL,
    EINTRITT,
    PIN
) = range(8)

FLAGGEN = {
    "deutschland": "🇩🇪", "polen": "🇵🇱", "türkei": "🇹🇷",
    "rumänien": "🇷🇴", "italien": "🇮🇹"
}
SPRACHEN = {
    "deutsch": "🗣️🇩🇪", "polnisch": "🗣️🇵🇱", "englisch": "🗣️🇬🇧", "türkisch": "🗣️🇹🇷"
}

main_markup = ReplyKeyboardMarkup([['🚚 LOGIN FAHRER', '👔 LOGIN CEO']], resize_keyboard=True)
back_markup = ReplyKeyboardMarkup([['⬅️ ZURÜCK']], resize_keyboard=True)
ceo_markup = ReplyKeyboardMarkup([['🏢 FIRMA', '⬅️ ZURÜCK']], resize_keyboard=True)
firma_markup = ReplyKeyboardMarkup([['👷 FAHRER', '⬅️ ZURÜCK']], resize_keyboard=True)
fahrer_markup = ReplyKeyboardMarkup([['📋 ALLE', '🔄 ERSATZ', '⬅️ ZURÜCK']], resize_keyboard=True)
alle_markup = ReplyKeyboardMarkup([['🆕 NEU', '✏️ ÄNDERN', '⬅️ ZURÜCK']], resize_keyboard=True)

# === Start & Hauptmenü ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    try: await update.message.delete()
    except: pass
    msg = await context.bot.send_message(chat_id, "Willkommen 👋\nBitte wähle deine Rolle:", reply_markup=main_markup)
    context.user_data.update({
        "last_message": msg.message_id,
        "state": "start", "prev_state": "start",
        "last_active": datetime.datetime.utcnow()
    })

# === Menünavigation ===
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text
    chat_id = update.effective_chat.id
    context.user_data["last_active"] = datetime.datetime.utcnow()

    try: await update.message.delete()
    except: pass
    if "last_message" in context.user_data:
        try: await context.bot.delete_message(chat_id, context.user_data["last_message"])
        except: pass

    if msg == '🚚 LOGIN FAHRER':
        m = await context.bot.send_message(chat_id, "✅ Willkommen auf der Fahrer Plattform", reply_markup=back_markup)
        context.user_data.update({"last_message": m.message_id, "state": "fahrer", "prev_state": "start"})
        branding = await context.bot.send_photo(chat_id, photo=open(BRANDING_PATH, "rb"))
        await asyncio.sleep(3); await branding.delete()

    elif msg == '👔 LOGIN CEO':
        m = await context.bot.send_message(chat_id, "✅ Willkommen auf der CEO Plattform", reply_markup=ceo_markup)
        context.user_data.update({"last_message": m.message_id, "state": "ceo", "prev_state": "start"})
        branding = await context.bot.send_photo(chat_id, photo=open(BRANDING_PATH, "rb"))
        await asyncio.sleep(3); await branding.delete()

    elif msg == '🏢 FIRMA':
        m = await context.bot.send_message(chat_id, "📁 Firmenübersicht", reply_markup=firma_markup)
        context.user_data.update({"last_message": m.message_id, "state": "firma", "prev_state": "ceo"})

    elif msg == '👷 FAHRER':
        m = await context.bot.send_message(chat_id, "👷 Fahrerbereich", reply_markup=fahrer_markup)
        context.user_data.update({"last_message": m.message_id, "state": "fahrerverwaltung", "prev_state": "firma"})

    elif msg == '📋 ALLE':
        m = await context.bot.send_message(chat_id, "📋 Fahrerübersicht (Platzhalter)", reply_markup=alle_markup)
        context.user_data.update({"last_message": m.message_id, "state": "alle", "prev_state": "fahrerverwaltung"})

    elif msg == '✏️ ÄNDERN':
        m = await context.bot.send_message(chat_id, "📝 Fahrer bearbeiten (Platzhalter)", reply_markup=alle_markup)
        context.user_data.update({"last_message": m.message_id})

    elif msg == '⬅️ ZURÜCK':
        zurück = {
            "ceo": (ceo_markup, "ceo", "start"),
            "firma": (firma_markup, "firma", "ceo"),
            "fahrerverwaltung": (fahrer_markup, "fahrerverwaltung", "firma"),
            "alle": (fahrer_markup, "fahrerverwaltung", "firma")
        }
        prev = context.user_data.get("prev_state", "start")
        if prev in zurück:
            markup, newstate, pstate = zurück[prev]
            m = await context.bot.send_message(chat_id, "⬅️ Zurück", reply_markup=markup)
            context.user_data.update({"last_message": m.message_id, "state": newstate, "prev_state": pstate})
        else:
            m = await context.bot.send_message(chat_id, "🔄 Zurück zum Hauptmenü", reply_markup=main_markup)
            context.user_data.update({"last_message": m.message_id, "state": "start", "prev_state": "start"})
            # === Fahrer anlegen – Start ===
async def neu_fahrer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.delete()
    await context.bot.send_message(update.effective_chat.id, "Vorname des Fahrers:")
    return VORNAME

async def vorname(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["fahrer"] = {"vorname": update.message.text}
    await update.message.delete()
    await update.message.reply_text("Nachname:")
    return NACHNAME

async def nachname(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["fahrer"]["nachname"] = update.message.text
    await update.message.delete()
    await update.message.reply_text("Geburtstag (z.B. 01.01.1990):")
    return GEBURTSTAG

async def geburtstag(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["fahrer"]["geburtstag"] = update.message.text
    await update.message.delete()
    await update.message.reply_text("Nationalität (z.B. Deutschland):")
    return NATIONALITÄT

async def nationalität(update: Update, context: ContextTypes.DEFAULT_TYPE):
    eingabe = update.message.text.lower()
    flagge = FLAGGEN.get(eingabe, "🌍")
    context.user_data["fahrer"]["nationalität"] = flagge
    await update.message.delete()
    await update.message.reply_text("Sprache (z.B. Deutsch):")
    return SPRACHE

async def sprache(update: Update, context: ContextTypes.DEFAULT_TYPE):
    eingabe = update.message.text.lower()
    icon = SPRACHEN.get(eingabe, "🗣️")
    context.user_data["fahrer"]["sprache"] = icon
    await update.message.delete()
    await update.message.reply_text("Mobilnummer:")
    return MOBIL

async def mobil(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["fahrer"]["mobil"] = update.message.text
    await update.message.delete()
    await update.message.reply_text("Angestellt seit (z.B. 01.03.2023):")
    return EINTRITT

async def eintritt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["fahrer"]["seit"] = update.message.text
    await update.message.delete()
    await update.message.reply_text("Bitte 4-stelligen PIN festlegen:")
    return PIN

async def pin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["fahrer"]["pin"] = update.message.text
    fahrerliste = context.application.bot_data.setdefault("fahrer", [])
    neue_id = f"F{len(fahrerliste)+1:04}"
    context.user_data["fahrer"]["id"] = neue_id
    fahrerliste.append(context.user_data["fahrer"])
    data = context.user_data["fahrer"]
    await update.message.delete()
    msg = await update.message.reply_text(
        f"✅ Fahrer angelegt:\n\nID: {data['id']}\n{data['vorname']} {data['nachname']} {data['sprache']} {data['nationalität']}\nMobil: {data['mobil']}\nSeit: {data['seit']}\nPIN: {data['pin']}",
        reply_markup=alle_markup
    )
    context.user_data["last_message"] = msg.message_id
    return ConversationHandler.END

# === Auto Reset nach Inaktivität ===
async def reset_user_menu(context: ContextTypes.DEFAULT_TYPE):
    now = datetime.datetime.utcnow()
    for chat_id, data in context.chat_data.items():
        last_active = data.get("last_active")
        if last_active and (now - last_active).total_seconds() > RESET_MINUTES * 60:
            msg = await context.bot.send_message(chat_id, "⏳ Automatischer Reset", reply_markup=main_markup)
            context.chat_data[chat_id].update({
                "last_message": msg.message_id,
                "last_active": now,
                "state": "start",
                "prev_state": "start"
            })

# === Setup & Start ===
if __name__ == '__main__':
    app = ApplicationBuilder().token(os.getenv("BOT_TOKEN")).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Conversation Handler für "🆕 NEU"
    conv = ConversationHandler(
        entry_points=[MessageHandler(filters.TEXT & filters.Regex("^🆕 NEU$"), neu_fahrer)],
        states={
            VORNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, vorname)],
            NACHNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, nachname)],
            GEBURTSTAG: [MessageHandler(filters.TEXT & ~filters.COMMAND, geburtstag)],
            NATIONALITÄT: [MessageHandler(filters.TEXT & ~filters.COMMAND, nationalität)],
            SPRACHE: [MessageHandler(filters.TEXT & ~filters.COMMAND, sprache)],
            MOBIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, mobil)],
            EINTRITT: [MessageHandler(filters.TEXT & ~filters.COMMAND, eintritt)],
            PIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, pin)],
        },
        fallbacks=[]
    )
    app.add_handler(conv)

    app.job_queue.run_repeating(reset_user_menu, interval=60, first=60)
    app.run_polling()