import os
import datetime
import asyncio
from telegram import Update, ReplyKeyboardMarkup, InputFile
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    filters, ContextTypes
)

main_menu = ReplyKeyboardMarkup([['🚚 LOGIN FAHRER', '👔 LOGIN CEO']], resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cid = update.effective_chat.id
    context.chat_data[cid] = {"state": "start", "msg_ids": []}

    # Branding-Bild
    branding_msg = await context.bot.send_photo(chat_id=cid, photo=InputFile("branding.png"))
    context.chat_data[cid]["msg_ids"].append(branding_msg.message_id)

    # Lizenztext
    lizenz_msg = await update.message.reply_text("Lizensiert für Kania Schüttguttransporte")
    context.chat_data[cid]["msg_ids"].append(lizenz_msg.message_id)

    # Nach 3 Sekunden löschen
    await asyncio.sleep(3)
    for mid in context.chat_data[cid]["msg_ids"]:
        try:
            await context.bot.delete_message(chat_id=cid, message_id=mid)
        except:
            pass

    welcome = await update.message.reply_text("Willkommen 👋\nBitte wähle deine Rolle:", reply_markup=main_menu)
    context.chat_data[cid]["msg_ids"] = [welcome.message_id]

if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)

    TOKEN = os.getenv("BOT_TOKEN")
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.run_polling()