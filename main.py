import os
import json
import time
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
    await delete_previous_messages(context, chat_id)

    # Branding
    branding = await context.bot.send_photo(chat_id=chat_id, photo=InputFile(branding_path))
    await asyncio.sleep(3)
    await context.bot.delete_message(chat_id=chat_id, message_id=branding.message_id)

    # Starttext mit Buttons
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

    # LOGIN FAHRER
    if data == "login_fahrer":
        msg = await query.message.reply_text("✅ Willkommen auf der Fahrer Plattform")
        keyboard = [
            [InlineKeyboardButton("📅 KALENDER", callback_data="kalender_fahrer")],
            [InlineKeyboardButton("🛠️ SUPERVISOR", callback_data="supervisor")],
            [InlineKeyboardButton("🌄 TOUREN", callback_data="touren")],
            [InlineKeyboardButton("⬅️ ZURÜCK", callback_data="start")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        user_state[chat_id] = "login_fahrer"
        await context.bot.send_message(chat_id=chat_id, text="📂 LOGIN FAHRER", reply_markup=reply_markup)
        user_messages[chat_id] = [msg.message_id]

    # LOGIN CEO
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
        user_state[chat_id] = "login_ceo"
        await context.bot.send_message(chat_id=chat_id, text="📂 LOGIN CEO", reply_markup=reply_markup)
        user_messages[chat_id] = [msg.message_id]

    # ZURÜCK
    elif data == "start":
        await start(update, context)

def reset_inactive_users(app):
    async def reset():
        while True:
            now = time.time()
            for chat_id in list(user_last_active):
                if now - user_last_active[chat_id] > 120:
                    user_state[chat_id] = "start"
                    del user_last_active[chat_id]
            await asyncio.sleep(60)
    app.create_task(reset())

if __name__ == "__main__":
    token = os.getenv("BOT_TOKEN")
    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    reset_inactive_users(app)
    app.run_polling()