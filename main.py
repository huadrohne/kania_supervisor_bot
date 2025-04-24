import asyncio
import datetime
import os
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
)
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler,
    filters, ContextTypes, ConversationHandler
)

(VORNAME, NACHNAME, GEBURTSTAG, NATIONALITÄT, SPRACHE, MOBIL, EINTRITT, PIN) = range(8)

FLAGGEN = {
    "deutschland": "🇩🇪", "polen": "🇵🇱", "türkei": "🇹🇷", "rumänien": "🇷🇴", "italien": "🇮🇹"
}
SPRACHEN = {
    "deutsch": "🗣️🇩🇪", "polnisch": "🗣️🇵🇱", "englisch": "🗣️🇬🇧", "türkisch": "🗣️🇹🇷"
}

RESET_MINUTES = 2
BRANDING_PATH = "branding.png"

# === Menübereiche (Inline) ===
def get_main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🚚 LOGIN FAHRER", callback_data="login_fahrer")],
        [InlineKeyboardButton("👔 LOGIN CEO", callback_data="login_ceo")]
    ])

def get_ceo_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🏢 FIRMA", callback_data="firma")],
        [InlineKeyboardButton("⬅️ ZURÜCK", callback_data="zurueck_start")]
    ])

def get_firma_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("👷 FAHRER", callback_data="fahrer")],
        [InlineKeyboardButton("⬅️ ZURÜCK", callback_data="zurueck_ceo")]
    ])

def get_fahrer_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📋 ALLE", callback_data="alle")],
        [InlineKeyboardButton("🔄 ERSATZ", callback_data="ersatz")],
        [InlineKeyboardButton("⬅️ ZURÜCK", callback_data="zurueck_firma")]
    ])

def get_alle_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🆕 NEU", callback_data="neu")],
        [InlineKeyboardButton("✏️ ÄNDERN", callback_data="aendern")],
        [InlineKeyboardButton("⬅️ ZURÜCK", callback_data="zurueck_fahrer")]
    ])

# === Start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cid = update.effective_chat.id
    context.chat_data[cid] = {"state": "start", "last_active": datetime.datetime.utcnow()}

    # Entferne alte Nachrichten falls nötig
    await clear_messages(cid, context)
    msg = await update.message.reply_text("Willkommen 👋\nBitte wähle deine Rolle:", reply_markup=get_main_menu())
    context.chat_data[cid]["active_msg"] = msg.message_id

# === Nachricht aufräumen
async def clear_messages(cid, context):
    if "active_msg" in context.chat_data[cid]:
        try:
            await context.bot.delete_message(cid, context.chat_data[cid]["active_msg"])
        except: pass
        context.chat_data[cid]["active_msg"] = None

# === Callback-Hauptsteuerung
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    cid = query.message.chat_id
    data = query.data
    context.chat_data[cid]["last_active"] = datetime.datetime.utcnow()

    await clear_messages(cid, context)

    if data == "login_fahrer":
        m = await query.message.reply_text("✅ Willkommen auf der Fahrer Plattform", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ ZURÜCK", callback_data="zurueck_start")]]))
        img = await context.bot.send_photo(cid, photo=open(BRANDING_PATH, "rb"))
        await asyncio.sleep(3)
        await img.delete()
        context.chat_data[cid]["active_msg"] = m.message_id
        context.chat_data[cid]["state"] = "login_fahrer"

    elif data == "login_ceo":
        m = await query.message.reply_text("✅ Willkommen auf der CEO Plattform", reply_markup=get_ceo_menu())
        img = await context.bot.send_photo(cid, photo=open(BRANDING_PATH, "rb"))
        await asyncio.sleep(3)
        await img.delete()
        context.chat_data[cid]["active_msg"] = m.message_id
        context.chat_data[cid]["state"] = "ceo"

    elif data == "firma":
        m = await query.message.reply_text("📂 LOGIN CEO ➜ FIRMA", reply_markup=get_firma_menu())
        context.chat_data[cid]["active_msg"] = m.message_id
        context.chat_data[cid]["state"] = "firma"

    elif data == "fahrer":
        m = await query.message.reply_text("📂 LOGIN CEO ➜ FIRMA ➜ FAHRER", reply_markup=get_fahrer_menu())
        context.chat_data[cid]["active_msg"] = m.message_id
        context.chat_data[cid]["state"] = "fahrer"

    elif data == "alle":
        fahrerliste = context.application.bot_data.get("fahrer", [])
        text = "Keine Fahrer vorhanden." if not fahrerliste else "\n".join([f"{f['id']} – {f['vorname']} {f['nachname']} {f['sprache']} {f['nationalität']}" for f in fahrerliste])
        m = await query.message.reply_text(f"📋 Fahrerübersicht:\n{text}", reply_markup=get_alle_menu())
        context.chat_data[cid]["active_msg"] = m.message_id
        context.chat_data[cid]["state"] = "alle"

    elif data == "zurueck_start":
        m = await query.message.reply_text("Willkommen 👋\nBitte wähle deine Rolle:", reply_markup=get_main_menu())
        context.chat_data[cid]["active_msg"] = m.message_id
        context.chat_data[cid]["state"] = "start"

    elif data == "zurueck_ceo":
        m = await query.message.reply_text("📂 LOGIN CEO", reply_markup=get_ceo_menu())
        context.chat_data[cid]["active_msg"] = m.message_id
        context.chat_data[cid]["state"] = "ceo"

    elif data == "zurueck_firma":
        m = await query.message.reply_text("📂 LOGIN CEO ➜ FIRMA", reply_markup=get_firma_menu())
        context.chat_data[cid]["active_msg"] = m.message_id
        context.chat_data[cid]["state"] = "firma"

    elif data == "zurueck_fahrer":
        m = await query.message.reply_text("📂 LOGIN CEO ➜ FIRMA ➜ FAHRER", reply_markup=get_fahrer_menu())
        context.chat_data[cid]["active_msg"] = m.message_id
        context.chat_data[cid]["state"] = "fahrer"
        
        # === Fahrer anlegen ===
async def neu_fahrer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.callback_query.message.delete()
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
    await update.message.reply_text(f"📋 Fahrerübersicht:\n{text}", reply_markup=get_alle_menu())
    return ConversationHandler.END

# === Reset nach Inaktivität ===
async def reset_user_menu(context: ContextTypes.DEFAULT_TYPE):
    now = datetime.datetime.utcnow()
    for chat_id, data in context.chat_data.items():
        last_active = data.get("last_active")
        if last_active and (now - last_active).total_seconds() > RESET_MINUTES * 60:
            try:
                await context.bot.send_message(chat_id, "⏳ Zurück zum Hauptmenü", reply_markup=get_main_menu())
                context.chat_data[chat_id] = {"state": "start", "last_active": now}
            except:
                continue

# === Start des Bots ===
if __name__ == '__main__':
    app = ApplicationBuilder().token(os.getenv("BOT_TOKEN")).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))

    conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(neu_fahrer, pattern="^neu$")],
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