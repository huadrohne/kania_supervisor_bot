import asyncio
import datetime
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, ConversationHandler, filters
)
import os

# Zustände für Fahreranlage
(VORNAME, NACHNAME, GEBURTSTAG, NATIONALITÄT, SPRACHE, MOBIL, EINTRITT, PIN) = range(8)

# Flaggen und Sprachen
FLAGGEN = {
    "deutschland": "🇩🇪", "polen": "🇵🇱", "türkei": "🇹🇷", "rumänien": "🇷🇴", "italien": "🇮🇹"
}
SPRACHEN = {
    "deutsch": "🗣️🇩🇪", "polnisch": "🗣️🇵🇱", "englisch": "🗣️🇬🇧", "türkisch": "🗣️🇹🇷"
}

# Keyboards
main_markup = ReplyKeyboardMarkup([['🚚 LOGIN FAHRER', '👔 LOGIN CEO']], resize_keyboard=True)
ceo_markup = ReplyKeyboardMarkup([['🏢 FIRMA', '⬅️ ZURÜCK']], resize_keyboard=True)
firma_markup = ReplyKeyboardMarkup([['👷 FAHRER', '⬅️ ZURÜCK']], resize_keyboard=True)
fahrer_markup = ReplyKeyboardMarkup([['📋 ALLE', '🔄 ERSATZ', '⬅️ ZURÜCK']], resize_keyboard=True)
alle_markup = ReplyKeyboardMarkup([['🆕 NEU', '✏️ ÄNDERN', '⬅️ ZURÜCK']], resize_keyboard=True)

RESET_MINUTES = 2

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Willkommen 👋\nBitte wähle deine Rolle:", reply_markup=main_markup)
    context.user_data.update({"state": "start", "prev_state": "start", "last_active": datetime.datetime.utcnow()})

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text
    if msg == "📋 ALLE":
        fahrer_liste = context.application.bot_data.get("fahrer", [])
        if not fahrer_liste:
            text = "Keine Fahrer gespeichert."
        else:
            text = "\n".join([f"{f['id']} – {f['vorname']} {f['nachname']} {f['sprache']} {f['nationalität']}" for f in fahrer_liste])
        await update.message.reply_text(f"📋 Fahrerübersicht:\n{text}", reply_markup=alle_markup)

# === Fahreranlage Schritt für Schritt ===
async def neu_fahrer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bitte gib den Vornamen des Fahrers ein:")
    return VORNAME

async def vorname(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["fahrer"] = {"vorname": update.message.text}
    await update.message.reply_text("Bitte gib den Nachnamen ein:")
    return NACHNAME

async def nachname(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["fahrer"]["nachname"] = update.message.text
    await update.message.reply_text("Bitte gib das Geburtsdatum ein (z. B. 01.01.1990):")
    return GEBURTSTAG

async def geburtstag(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["fahrer"]["geburtstag"] = update.message.text
    await update.message.reply_text("Bitte gib die Nationalität ein (z. B. Deutschland):")
    return NATIONALITÄT

async def nationalität(update: Update, context: ContextTypes.DEFAULT_TYPE):
    flag = FLAGGEN.get(update.message.text.lower(), "🌍")
    context.user_data["fahrer"]["nationalität"] = flag
    await update.message.reply_text("Bitte gib die Sprache ein (z. B. Deutsch):")
    return SPRACHE

async def sprache(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sprache = SPRACHEN.get(update.message.text.lower(), "🗣️")
    context.user_data["fahrer"]["sprache"] = sprache
    await update.message.reply_text("Bitte gib die Mobilnummer ein:")
    return MOBIL

async def mobil(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["fahrer"]["mobil"] = update.message.text
    await update.message.reply_text("Seit wann ist der Fahrer angestellt? (z. B. 01.03.2023):")
    return EINTRITT

async def eintritt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["fahrer"]["seit"] = update.message.text
    await update.message.reply_text("Bitte vergib eine 4-stellige PIN:")
    return PIN

async def pin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["fahrer"]["pin"] = update.message.text
    fahrerliste = context.application.bot_data.setdefault("fahrer", [])
    neue_id = f"F{len(fahrerliste)+1:04}"
    context.user_data["fahrer"]["id"] = neue_id
    fahrerliste.append(context.user_data["fahrer"])
    await update.message.reply_text("✅ Fahrer erfolgreich angelegt. Hier ist die aktuelle Übersicht:")
    
    # Übersicht anzeigen
    text = "\n".join([f"{f['id']} – {f['vorname']} {f['nachname']} {f['sprache']} {f['nationalität']}" for f in fahrerliste])
    await update.message.reply_text(f"📋 Fahrerübersicht:\n{text}", reply_markup=alle_markup)
    return ConversationHandler.END

# === Setup ===
if __name__ == '__main__':
    app = ApplicationBuilder().token(os.getenv("BOT_TOKEN")).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.add_handler(ConversationHandler(
        entry_points=[MessageHandler(filters.TEXT & filters.Regex("^🆕 NEU$"), neu_fahrer)],
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
    ))
    app.run_polling()