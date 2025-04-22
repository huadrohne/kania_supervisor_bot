import asyncio
import datetime
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, ConversationHandler, filters
)
import os

# Fahreranlage-Zustände
(VORNAME, NACHNAME, GEBURTSTAG, NATIONALITÄT, SPRACHE, MOBIL, EINTRITT, PIN) = range(8)

# Nationalitäten & Sprachen
FLAGGEN = {
    "deutschland": "🇩🇪", "polen": "🇵🇱", "türkei": "🇹🇷", "rumänien": "🇷🇴", "italien": "🇮🇹"
}
SPRACHEN = {
    "deutsch": "🗣️🇩🇪", "polnisch": "🗣️🇵🇱", "englisch": "🗣️🇬🇧", "türkisch": "🗣️🇹🇷"
}

BRANDING_PATH = "branding.png"

# Tastaturen
main_markup = ReplyKeyboardMarkup([['🚚 LOGIN FAHRER', '👔 LOGIN CEO']], resize_keyboard=True)
ceo_markup = ReplyKeyboardMarkup([['🏢 FIRMA', '⬅️ ZURÜCK']], resize_keyboard=True)
firma_markup = ReplyKeyboardMarkup([['👷 FAHRER', '⬅️ ZURÜCK']], resize_keyboard=True)
fahrer_markup = ReplyKeyboardMarkup([['📋 ALLE', '🔄 ERSATZ', '⬅️ ZURÜCK']], resize_keyboard=True)
alle_markup = ReplyKeyboardMarkup([['🆕 NEU', '✏️ ÄNDERN', '⬅️ ZURÜCK']], resize_keyboard=True)

# Start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Willkommen 👋\nBitte wähle deine Rolle:", reply_markup=main_markup)

# Haupt-Handler für alle Buttons
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text
    chat_id = update.effective_chat.id

    if msg == "🚚 LOGIN FAHRER":
        await update.message.reply_text("Willkommen auf der Fahrer Plattform", reply_markup=ReplyKeyboardMarkup([['⬅️ ZURÜCK']], resize_keyboard=True))
        branding = await context.bot.send_photo(chat_id, photo=open(BRANDING_PATH, "rb"))
        await asyncio.sleep(3); await branding.delete()

    elif msg == "👔 LOGIN CEO":
        await update.message.reply_text("Willkommen auf der CEO Plattform", reply_markup=ceo_markup)
        branding = await context.bot.send_photo(chat_id, photo=open(BRANDING_PATH, "rb"))
        await asyncio.sleep(3); await branding.delete()

    elif msg == "🏢 FIRMA":
        await update.message.reply_text("Firmenbereich", reply_markup=firma_markup)

    elif msg == "👷 FAHRER":
        await update.message.reply_text("Fahrerbereich", reply_markup=fahrer_markup)

    elif msg == "📋 ALLE":
        fahrer_liste = context.application.bot_data.get("fahrer", [])
        if not fahrer_liste:
            text = "Keine Fahrer gespeichert."
        else:
            text = "\n".join([f"{f['id']} – {f['vorname']} {f['nachname']} {f['sprache']} {f['nationalität']}" for f in fahrer_liste])
        await update.message.reply_text(f"📋 Fahrerübersicht:\n{text}", reply_markup=alle_markup)

    elif msg == "⬅️ ZURÜCK":
        await update.message.reply_text("Zurück zum Hauptmenü", reply_markup=main_markup)

# === Fahrer anlegen ===
async def neu_fahrer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bitte gib den Vornamen des Fahrers ein:")
    return VORNAME

async def vorname(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["fahrer"] = {"vorname": update.message.text}
    await update.message.reply_text("Nachname:")
    return NACHNAME

async def nachname(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["fahrer"]["nachname"] = update.message.text
    await update.message.reply_text("Geburtstag:")
    return GEBURTSTAG

async def geburtstag(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["fahrer"]["geburtstag"] = update.message.text
    await update.message.reply_text("Nationalität:")
    return NATIONALITÄT

async def nationalität(update: Update, context: ContextTypes.DEFAULT_TYPE):
    flag = FLAGGEN.get(update.message.text.lower(), "🌍")
    context.user_data["fahrer"]["nationalität"] = flag
    await update.message.reply_text("Sprache:")
    return SPRACHE

async def sprache(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sprache = SPRACHEN.get(update.message.text.lower(), "🗣️")
    context.user_data["fahrer"]["sprache"] = sprache
    await update.message.reply_text("Mobilnummer:")
    return MOBIL

async def mobil(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["fahrer"]["mobil"] = update.message.text
    await update.message.reply_text("Angestellt seit:")
    return EINTRITT

async def eintritt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["fahrer"]["seit"] = update.message.text
    await update.message.reply_text("4-stelliger PIN:")
    return PIN

async def pin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["fahrer"]["pin"] = update.message.text
    fahrer_liste = context.application.bot_data.setdefault("fahrer", [])
    neue_id = f"F{len(fahrer_liste)+1:04}"
    context.user_data["fahrer"]["id"] = neue_id
    fahrer_liste.append(context.user_data["fahrer"])
    await update.message.reply_text("✅ Fahrer gespeichert. Übersicht:")
    text = "\n".join([f"{f['id']} – {f['vorname']} {f['nachname']} {f['sprache']} {f['nationalität']}" for f in fahrer_liste])
    await update.message.reply_text(f"📋 Fahrerübersicht:\n{text}", reply_markup=alle_markup)
    return ConversationHandler.END

# Startpunkt
if __name__ == '__main__':
    app = ApplicationBuilder().token(os.getenv("BOT_TOKEN")).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^(🆕 NEU|🆕\sNEU)$"), neu_fahrer)],
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