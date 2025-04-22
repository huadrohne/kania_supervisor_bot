import asyncio
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import os

BRANDING_PATH = "branding.png"

# Tastaturen
main_keyboard = [['🔐 LOGIN FAHRER', '👑 LOGIN CEO']]
main_markup = ReplyKeyboardMarkup(main_keyboard, resize_keyboard=True, one_time_keyboard=False)

back_keyboard = [['🔙 ZURÜCK']]
back_markup = ReplyKeyboardMarkup(back_keyboard, resize_keyboard=True, one_time_keyboard=False)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.delete()
    except:
        pass
    await update.message.chat.send_message(
        "Willkommen 👋\nBitte wähle deine Rolle:",
        reply_markup=main_markup
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.delete()
    except:
        pass

    msg = update.message.text
    chat_id = update.effective_chat.id

    if msg == '🔐 LOGIN FAHRER':
        await context.bot.send_message(chat_id, "✅ Willkommen auf der Fahrer Plattform", reply_markup=back_markup)
        branding_msg = await context.bot.send_photo(chat_id, photo=open(BRANDING_PATH, "rb"))
        await asyncio.sleep(3)
        await branding_msg.delete()

    elif msg == '👑 LOGIN CEO':
        await context.bot.send_message(chat_id, "✅ Willkommen auf der CEO Plattform", reply_markup=back_markup)
        branding_msg = await context.bot.send_photo(chat_id, photo=open(BRANDING_PATH, "rb"))
        await asyncio.sleep(3)
        await branding_msg.delete()

    elif msg == '🔙 ZURÜCK':
        await context.bot.send_message(chat_id, "🔄 Zurück zum Hauptmenü", reply_markup=main_markup)

    else:
        await context.bot.send_message(chat_id, "Bitte wähle eine gültige Option.", reply_markup=main_markup)

if __name__ == '__main__':
    TOKEN = os.getenv("BOT_TOKEN")
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()