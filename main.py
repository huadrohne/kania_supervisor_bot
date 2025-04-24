import asyncio
import datetime
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    ContextTypes, ConversationHandler
)

# Fahrerdaten-Stati
(VORNAME, NACHNAME, GEBURTSTAG, NATIONALITÄT, SPRACHE, MOBIL, EINTRITT, PIN) = range(8)

# Flaggen & Sprachicons
FLAGGEN = {
    "deutschland": "🇩🇪", "polen": "🇵🇱", "türkei": "🇹🇷", "rumänien": "🇷🇴", "italien": "🇮🇹"
}
SPRACHEN = {
    "deutsch": "🗣️🇩🇪", "polnisch": "🗣️🇵🇱", "englisch": "🗣️🇬🇧", "türkisch": "🗣️🇹🇷"
}

RESET_MINUTES = 2
BRANDING_PATH = "branding.png"

# Hilfsfunktion für Inline-Buttons
def inline_buttons(buttons):
    return InlineKeyboardMarkup([[InlineKeyboardButton(text, callback_data=data)] for text, data in buttons])

# Hauptmenü
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cid = update.effective_chat.id
    await update.message.delete()
    context.chat_data[cid] = {"state": "start", "last_active": datetime.datetime.utcnow()}
    await context.bot.send_message(cid, "Willkommen 👋\nBitte wähle deine Rolle:", reply_markup=inline_buttons([
        ("🚚 LOGIN FAHRER", "login_fahrer"),
        ("👔 LOGIN CEO", "login_ceo")
    ]))

# Automatischer Reset
async def reset_user_menu(context: ContextTypes.DEFAULT_TYPE):
    now = datetime.datetime.utcnow()
    for cid, data in context.chat_data.items():
        last_active = data.get("last_active")
        if last_active and (now - last_active).total_seconds() > RESET_MINUTES * 60:
            await context.bot.send_message(cid, "⏳ Zurück zum Hauptmenü", reply_markup=inline_buttons([
                ("🚚 LOGIN FAHRER", "login_fahrer"),
                ("👔 LOGIN CEO", "login_ceo")
            ]))
            context.chat_data[cid] = {"state": "start", "last_active": now}

# Callback Handler
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    cid = query.message.chat.id
    context.chat_data[cid]["last_active"] = datetime.datetime.utcnow()

    await query.message.delete()

    if query.data == "login_fahrer":
        await show_branding(cid, context)
        await context.bot.send_message(cid, "✅ Willkommen auf der Fahrer Plattform", reply_markup=inline_buttons([
            ("⬅️ ZURÜCK", "start")
        ]))
        context.chat_data[cid]["state"] = "login_fahrer"

    elif query.data == "login_ceo":
        await show_branding(cid, context)
        await context.bot.send_message(cid, "✅ Willkommen auf der CEO Plattform", reply_markup=inline_buttons([
            ("🏢 FIRMA", "firma"),
            ("⬅️ ZURÜCK", "start")
        ]))
        context.chat_data[cid]["state"] = "login_ceo"

    elif query.data == "firma":
        await context.bot.send_message(cid, "LOGIN CEO/ FIRMA", reply_markup=inline_buttons([
            ("👷 FAHRER", "fahrer"),
            ("⬅️ ZURÜCK", "login_ceo")
        ]))
        context.chat_data[cid]["state"] = "firma"

    elif query.data == "fahrer":
        await context.bot.send_message(cid, "LOGIN CEO/ FIRMA/ FAHRER", reply_markup=inline_buttons([
            ("📋 ALLE", "alle"),
            ("🔄 ERSATZ", "ersatz"),
            ("⬅️ ZURÜCK", "firma")
        ]))
        context.chat_data[cid]["state"] = "fahrer"

    elif query.data == "ersatz":
        await context.bot.send_message(cid, "LOGIN CEO/ FIRMA/ FAHRER/ ERSATZ", reply_markup=inline_buttons([
            ("⬅️ ZURÜCK", "fahrer")
        ]))
        context.chat_data[cid]["state"] = "ersatz"

    elif query.data == "alle":
        fahrerliste = context.application.bot_data.get("fahrer", [])
        if not fahrerliste:
            text = "Keine Fahrer vorhanden."
        else:
            text = "\n".join([f"{f['id']} – {f['vorname']} {f['nachname']} {f['sprache']} {f['nationalität']}" for f in fahrerliste])
        await context.bot.send_message(cid, f"📋 Fahrerübersicht:\n{text}", reply_markup=inline_buttons([
            ("🆕 NEU", "neu"),
            ("✏️ ÄNDERN", "ändern"),
            ("⬅️ ZURÜCK", "fahrer")
        ]))
        context.chat_data[cid]["state"] = "alle"

    elif query.data == "start":
        await context.bot.send_message(cid, "Willkommen 👋\nBitte wähle deine Rolle:", reply_markup=inline_buttons([
            ("🚚 LOGIN FAHRER", "login_fahrer"),
            ("👔 LOGIN CEO", "login_ceo")
        ]))
        context.chat_data[cid]["state"] = "start"

    elif query.data == "neu":
        await context.bot.send_message(cid, "Bitte gib den Vornamen des Fahrers ein:")
        return VORNAME

# Branding
async def show_branding(cid, context):
    branding = await context.bot.send_photo(cid, photo=InputFile(BRANDING_PATH))
    text = await context.bot.send_message(cid, "Lizensiert für Kania Schüttguttransporte")
    await asyncio.sleep(2)
    await branding.delete()
    await text.delete()

# Fahrer-Anlage (wie gehabt)
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
    fahrerliste = context.application.bot_data.setdefault("fahrer", [])
    neue_id = f"F{len(fahrerliste)+1:04}"
    context.user_data["fahrer"]["id"] = neue_id
    fahrerliste.append(context.user_data["fahrer"])
    await update.message.reply_text("✅ Fahrer gespeichert.")
    return ConversationHandler.END

# === MAIN ===
if __name__ == '__main__':
    app = ApplicationBuilder().token(os.getenv("BOT_TOKEN")).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_callback))

    conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(handle_callback, pattern="^neu$")],
        states={
            VORNAME: [CommandHandler("start", start), MessageHandler(filters.TEXT, vorname)],
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