import os
import time
import json
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from dotenv import load_dotenv

load_dotenv()

user_state = {}
user_messages = {}
user_last_active = {}

branding_path = "branding.png"

def get_start_buttons():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🚛 LOGIN FAHRER", callback_data="login_fahrer"),
         InlineKeyboardButton("👔 LOGIN CEO", callback_data="login_ceo")]
    ])

async def delete_previous_messages(context: ContextTypes.DEFAULT_TYPE, chat_id):
    if chat_id in user_messages:
        for msg_id in user_messages[chat_id]:
            try:
                await context.bot.delete_message(chat_id=chat_id, message_id=msg_id)
            except:
                pass
        user_messages[chat_id] = []

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_state[chat_id] = "start"
    user_last_active[chat_id] = time.time()

    # Entferne /start Nachricht
    if update.message:
        try:
            await update.message.delete()
        except:
            pass

    await delete_previous_messages(context, chat_id)

    # Branding
    branding = await context.bot.send_photo(chat_id=chat_id, photo=InputFile(branding_path))
    await asyncio.sleep(3)
    await context.bot.delete_message(chat_id=chat_id, message_id=branding.message_id)

    # Startbuttons
    msg = await context.bot.send_message(
        chat_id=chat_id,
        text="Willkommen 👋\nBitte wähle deine Rolle:",
        reply_markup=get_start_buttons()
    )
    user_messages[chat_id] = [msg.message_id]

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    chat_id = query.message.chat_id
    user_last_active[chat_id] = time.time()

    await delete_previous_messages(context, chat_id)

    if data == "login_fahrer":
        msg = await query.message.reply_text("✅ Willkommen auf der Fahrer Plattform")
        keyboard = [
            [InlineKeyboardButton("📅 KALENDER", callback_data="kalender_fahrer")],
            [InlineKeyboardButton("🛠️ SUPERVISOR", callback_data="supervisor")],
            [InlineKeyboardButton("🌄 TOUREN", callback_data="touren")],
            [InlineKeyboardButton("⬅️ ZURÜCK", callback_data="start")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_message(chat_id=chat_id, text="📂 LOGIN FAHRER", reply_markup=reply_markup)
        user_state[chat_id] = "login_fahrer"
        user_messages[chat_id] = [msg.message_id]

    elif data == "login_ceo":
        msg = await query.message.reply_text("✅ Willkommen auf der CEO Plattform")
        keyboard = [
            [InlineKeyboardButton("🏢 BÜRO", callback_data="buero")],
            [InlineKeyboardButton("📅 KALENDER", callback_data="kalender_ceo")],
            [InlineKeyboardButton("🆘 SUPPORT", callback_data="support")],
            [InlineKeyboardButton("🏢 FIRMA", callback_data="firma")],
            [InlineKeyboardButton("⬅️ ZURÜCK", callback_data="start")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_message(chat_id=chat_id, text="📂 LOGIN CEO", reply_markup=reply_markup)
        user_state[chat_id] = "login_ceo"
        user_messages[chat_id] = [msg.message_id]

    elif data == "firma":
        msg = await query.message.reply_text("🏢 Firmenbereich")
        keyboard = [
            [InlineKeyboardButton("🧑‍✈️ FAHRER", callback_data="fahrer")],
            [InlineKeyboardButton("⬅️ ZURÜCK", callback_data="login_ceo")]
        ]
        await context.bot.send_message(chat_id=chat_id, text="📂 LOGIN CEO ➜ FIRMA", reply_markup=InlineKeyboardMarkup(keyboard))
        user_state[chat_id] = "firma"
        user_messages[chat_id] = [msg.message_id]

    elif data == "fahrer":
        msg = await query.message.reply_text("📋 Fahrerbereich")
        keyboard = [
            [InlineKeyboardButton("📋 ALLE", callback_data="alle")],
            [InlineKeyboardButton("🔄 ERSATZ", callback_data="ersatz")],
            [InlineKeyboardButton("⬅️ ZURÜCK", callback_data="firma")]
        ]
        await context.bot.send_message(chat_id=chat_id, text="📂 LOGIN CEO ➜ FIRMA ➜ FAHRER", reply_markup=InlineKeyboardMarkup(keyboard))
        user_state[chat_id] = "fahrer"
        user_messages[chat_id] = [msg.message_id]

    elif data == "start":
        await start(update, context)

if __name__ == "__main__":
    token = os.getenv("BOT_TOKEN")
    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.run_polling()