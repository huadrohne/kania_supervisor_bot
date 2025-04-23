import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
import os

# Branding-Variable
BRANDING_IMAGE = "branding.png"
LICENSE_TEXT = "Lizensiert für Kania Schüttguttransporte"

# /start handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    # Branding anzeigen
    with open(BRANDING_IMAGE, 'rb') as branding:
        branding_msg = await context.bot.send_photo(chat_id=chat_id, photo=branding)
    license_msg = await context.bot.send_message(chat_id=chat_id, text=LICENSE_TEXT)

    # Branding + Lizenztext nach 3 Sekunden löschen
    await asyncio.sleep(3)
    await branding_msg.delete()
    await license_msg.delete()

    # Willkommen + Buttons
    welcome_msg = await context.bot.send_message(
        chat_id=chat_id,
        text="Willkommen 👋\nBitte wähle deine Rolle:",
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🚛 LOGIN FAHRER", callback_data="login_fahrer"),
                InlineKeyboardButton("👔 LOGIN CEO", callback_data="login_ceo")
            ]
        ])
    )
    context.user_data['welcome_msg_id'] = welcome_msg.message_id

# Button-Auswertung
async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "login_fahrer":
        await query.message.reply_text("✅ Willkommen auf der Fahrer Plattform")

    elif query.data == "login_ceo":
        await query.message.reply_text("✅ Willkommen auf der CEO Plattform")

# Hauptfunktion
if __name__ == "__main__":
    TOKEN = os.getenv("BOT_TOKEN")
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_buttons))

    print("Bot läuft...")
    app.run_polling()