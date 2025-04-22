import asyncio
import datetime
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
import os

BRANDING_PATH = "branding.png"

# Tastaturen
main_keyboard = [['🚛 LOGIN FAHRER', '💻 LOGIN CEO']]
main_markup = ReplyKeyboardMarkup(main_keyboard, resize_keyboard=True, one_time_keyboard=False)
back_markup = ReplyKeyboardMarkup([['🔙 ZURÜCK']], resize_keyboard=True, one_time_keyboard=False)
ceo_markup = ReplyKeyboardMarkup([['🏢 FIRMA', '🔙 ZURÜCK']], resize_keyboard=True, one_time_keyboard=False)
firma_markup = ReplyKeyboardMarkup([['👷 FAHRER', '🔙 ZURÜCK']], resize_keyboard=True, one_time_keyboard=False)
fahrer_button_markup = ReplyKeyboardMarkup([['🔙 ZURÜCK']], resize_keyboard=True, one_time_keyboard=False)

RESET_MINUTES = 2  # für Testphase

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    try:
        await update.message.delete()
    except:
        pass
    msg = await context.bot.send_message(chat_id, "Willkommen 👋\nBitte wähle deine Rolle:", reply_markup=main_markup)
    context.user_data.update({
        "last_message": msg.message_id,
        "last_active": datetime.datetime.utcnow(),
        "state": "start",
        "prev_state": "start"
    })

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text
    chat_id = update.effective_chat.id
    context.user_data["last_active"] = datetime.datetime.utcnow()

    # Letzte Nachricht löschen
    if "last_message" in context.user_data:
        try:
            await context.bot.delete_message(chat_id, context.user_data["last_message"])
        except:
            pass
    try:
        await update.message.delete()
    except:
        pass

    if msg == '🚛 LOGIN FAHRER':
        msg_sent = await context.bot.send_message(chat_id, "✅ Willkommen auf der Fahrer Plattform", reply_markup=back_markup)
        context.user_data.update({"last_message": msg_sent.message_id, "state": "fahrer", "prev_state": "start"})
        branding_msg = await context.bot.send_photo(chat_id, photo=open(BRANDING_PATH, "rb"))
        await asyncio.sleep(3)
        await branding_msg.delete()

    elif msg == '💻 LOGIN CEO':
        msg_sent = await context.bot.send_message(chat_id, "✅ Willkommen auf der CEO Plattform", reply_markup=ceo_markup)
        context.user_data.update({"last_message": msg_sent.message_id, "state": "ceo", "prev_state": "start"})
        branding_msg = await context.bot.send_photo(chat_id, photo=open(BRANDING_PATH, "rb"))
        await asyncio.sleep(3)
        await branding_msg.delete()

    elif msg == '🏢 FIRMA':
        msg_sent = await context.bot.send_message(chat_id, "📁 Firmenübersicht", reply_markup=firma_markup)
        context.user_data.update({"last_message": msg_sent.message_id, "state": "firma", "prev_state": "ceo"})

    elif msg == '👷 FAHRER':
        msg_sent = await context.bot.send_message(chat_id, "👷 Fahrerübersicht (Platzhalter)", reply_markup=fahrer_button_markup)
        context.user_data.update({"last_message": msg_sent.message_id, "state": "fahrerverwaltung", "prev_state": "firma"})

    elif msg == '🔙 ZURÜCK':
        previous = context.user_data.get("prev_state", "start")
        if previous == "ceo":
            msg_sent = await context.bot.send_message(chat_id, "🔙 Zurück zur CEO Plattform", reply_markup=ceo_markup)
            context.user_data.update({"last_message": msg_sent.message_id, "state": "ceo", "prev_state": "start"})
        elif previous == "firma":
            msg_sent = await context.bot.send_message(chat_id, "📁 Zurück zur Firmenübersicht", reply_markup=firma_markup)
            context.user_data.update({"last_message": msg_sent.message_id, "state": "firma", "prev_state": "ceo"})
        else:
            msg_sent = await context.bot.send_message(chat_id, "🔄 Zurück zum Hauptmenü", reply_markup=main_markup)
            context.user_data.update({"last_message": msg_sent.message_id, "state": "start", "prev_state": "start"})

    else:
        msg_sent = await context.bot.send_message(chat_id, "Bitte wähle eine gültige Option.", reply_markup=main_markup)
        context.user_data.update({"last_message": msg_sent.message_id, "state": "start", "prev_state": "start"})

async def reset_user_menu(context: ContextTypes.DEFAULT_TYPE):
    now = datetime.datetime.utcnow()
    for chat_id, data in context.chat_data.items():
        last_active = data.get("last_active")
        if last_active and (now - last_active).total_seconds() > RESET_MINUTES * 60:
            msg = await context.bot.send_message(chat_id, "⏳ Automatischer Reset wegen Inaktivität", reply_markup=main_markup)
            context.chat_data[chat_id].update({
                "last_message": msg.message_id,
                "last_active": now,
                "state": "start",
                "prev_state": "start"
            })

if __name__ == '__main__':
    TOKEN = os.getenv("BOT_TOKEN")
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.job_queue.run_repeating(reset_user_menu, interval=60, first=60)
    app.run_polling()