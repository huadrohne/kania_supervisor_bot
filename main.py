import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler
import os

# Variablen für Branding und Lizenz
BRANDING_IMAGE = "branding.png"
LICENSE_TEXT = "Lizensiert für Kania Schüttguttransporte"

# Start-Handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Branding anzeigen
    with open(BRANDING_IMAGE, 'rb') as photo:
        branding_msg = await update.message.reply_photo(photo=photo)

    # Lizenztext anzeigen
    license_msg = await update.message.reply_text(LICENSE_TEXT)

    # Branding & Lizenz nach 3 Sekunden löschen
    await asyncio.sleep(3)
    await branding_msg.delete()
    await license_msg.delete()

    # Hauptmenü anzeigen
    welcome_msg = await update.message.reply_text(
        "Willkommen 👋\nBitte wähle deine Rolle:",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🚛 LOGIN FAHRER", callback_data="login_fahrer")],
            [InlineKeyboardButton("🧑‍💼 LOGIN CEO", callback_data="login_ceo")]
        ])
    )
    # Message ID speichern für möglichen Reset
    context.user_data['welcome_msg_id'] = welcome_msg.message_id

# Callback-Handler für die Buttons
async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "login_fahrer":
        await query.message.reply_text("✅ Willkommen auf der Fahrer Plattform")

    elif query.data == "login_ceo":
        await query.message.reply_text("✅ Willkommen auf der CEO Plattform")

# Bot starten
if __name__ == '__main__':
    TOKEN = os.getenv("BOT_TOKEN")

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_buttons))

    print("Bot läuft...")
    app.run_polling()