import os
import datetime
import asyncio
from telegram import (
    InlineKeyboardButton, InlineKeyboardMarkup, Update
)
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
)

# === Menüs ===
def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🚛 LOGIN FAHRER", callback_data="login_fahrer")],
        [InlineKeyboardButton("👔 LOGIN CEO", callback_data="login_ceo")]
    ])

def fahrer_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⬅️ ZURÜCK", callback_data="back_to_main")]
    ])

def ceo_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🏢 FIRMA", callback_data="firma")],
        [InlineKeyboardButton("⬅️ ZURÜCK", callback_data="back_to_main")]
    ])

def firma_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🧑‍🔧 FAHRER", callback_data="fahrer")],
        [InlineKeyboardButton("⬅️ ZURÜCK", callback_data="back_to_ceo")]
    ])

def fahrer_unter_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📋 ALLE", callback_data="alle")],
        [InlineKeyboardButton("🔄 ERSATZ", callback_data="ersatz")],
        [InlineKeyboardButton("⬅️ ZURÜCK", callback_data="back_to_firma")]
    ])

def ersatz_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⬅️ ZURÜCK", callback_data="back_to_fahrer")]
    ])

# === Branding-Image Pfad ===
BRANDING_IMAGE = "branding.png"

# === Start-Handler ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        await update.message.delete()
    query = update.callback_query
    if query:
        await query.answer()
    msg = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Willkommen 👋\nBitte wähle deine Rolle:",
        reply_markup=main_menu()
    )
    context.chat_data["welcome_msg"] = msg.message_id

# === Branding anzeigen ===
async def show_branding(chat_id, context):
    branding_img = await context.bot.send_photo(chat_id, photo=open(BRANDING_IMAGE, "rb"))
    text_msg = await context.bot.send_message(chat_id, "Lizensiert für Kania Schüttguttransporte")
    await asyncio.sleep(2)
    await context.bot.delete_message(chat_id, branding_img.message_id)
    await context.bot.delete_message(chat_id, text_msg.message_id)

# === Navigation-Handler ===
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat.id

    # Willkommenstext ggf. löschen
    welcome_id = context.chat_data.get("welcome_msg")
    if welcome_id:
        try:
            await context.bot.delete_message(chat_id, welcome_id)
        except:
            pass
        context.chat_data["welcome_msg"] = None

    pfad = ""
    reply_markup = None
    branding_needed = False

    if query.data == "login_fahrer":
        pfad = "📂 LOGIN FAHRER"
        reply_markup = fahrer_menu()
        branding_needed = True

    elif query.data == "login_ceo":
        pfad = "📂 LOGIN CEO"
        reply_markup = ceo_menu()
        branding_needed = True

    elif query.data == "firma":
        pfad = "📂 LOGIN CEO ➜ FIRMA"
        reply_markup = firma_menu()

    elif query.data == "fahrer":
        pfad = "📂 LOGIN CEO ➜ FIRMA ➜ FAHRER"
        reply_markup = fahrer_unter_menu()

    elif query.data == "alle":
        pfad = "📂 LOGIN CEO ➜ FIRMA ➜ FAHRER"
        await context.bot.send_message(chat_id, "📋 Fahrerübersicht:\nKeine Fahrer vorhanden.", reply_markup=fahrer_unter_menu())
        return

    elif query.data == "ersatz":
        pfad = "📂 LOGIN CEO ➜ FIRMA ➜ FAHRER ➜ ERSATZ"
        reply_markup = ersatz_menu()

    elif query.data == "back_to_fahrer":
        pfad = "📂 LOGIN CEO ➜ FIRMA ➜ FAHRER"
        reply_markup = fahrer_unter_menu()

    elif query.data == "back_to_firma":
        pfad = "📂 LOGIN CEO ➜ FIRMA"
        reply_markup = firma_menu()

    elif query.data == "back_to_ceo":
        pfad = "📂 LOGIN CEO"
        reply_markup = ceo_menu()

    elif query.data == "back_to_main":
        pfad = "Willkommen 👋\nBitte wähle deine Rolle:"
        reply_markup = main_menu()
        context.chat_data["welcome_msg"] = None

    # vorherige Statusnachricht löschen
    old_msg_id = context.chat_data.get("status_msg")
    if old_msg_id:
        try:
            await context.bot.delete_message(chat_id, old_msg_id)
        except:
            pass

    # Branding ggf. anzeigen
    if branding_needed:
        await show_branding(chat_id, context)

    # neue Nachricht schicken
    msg = await context.bot.send_message(chat_id, pfad, reply_markup=reply_markup)
    context.chat_data["status_msg"] = msg.message_id

# === Main ===
if __name__ == '__main__':
    app = ApplicationBuilder().token(os.getenv("BOT_TOKEN")).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.run_polling()
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