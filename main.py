import os
import datetime
import asyncio
from telegram import (
    InlineKeyboardButton, InlineKeyboardMarkup, Update, InputMediaPhoto
)
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
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
        pfad = "📂 LOGIN CEO/ FIRMA"
        reply_markup = firma_menu()

    elif query.data == "fahrer":
        pfad = "📂 LOGIN CEO/ FIRMA/ FAHRER"
        reply_markup = fahrer_unter_menu()

    elif query.data == "alle":
        pfad = "📂 LOGIN CEO/ FIRMA/ FAHRER"
        await context.bot.send_message(chat_id, "📋 Fahrerübersicht:\nKeine Fahrer vorhanden.", reply_markup=fahrer_unter_menu())
        return

    elif query.data == "ersatz":
        pfad = "📂 LOGIN CEO/ FIRMA/ FAHRER/ ERSATZ"
        reply_markup = ersatz_menu()

    elif query.data == "back_to_fahrer":
        pfad = "📂 LOGIN CEO/ FIRMA/ FAHRER"
        reply_markup = fahrer_unter_menu()

    elif query.data == "back_to_firma":
        pfad = "📂 LOGIN CEO/ FIRMA"
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