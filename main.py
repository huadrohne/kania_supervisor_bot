
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv
import json
import time

load_dotenv()

user_state = {}
user_messages = {}
user_data_store = {}
user_last_active = {}

driver_data_file = "fahrer.json"
branding_path = "branding.png"

def save_driver_data(data):
    with open(driver_data_file, "w") as f:
        json.dump(data, f)

def load_driver_data():
    try:
        with open(driver_data_file, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

async def delete_previous_messages(context: ContextTypes.DEFAULT_TYPE, chat_id):
    if chat_id in user_messages:
        for msg_id in user_messages[chat_id]:
            try:
                await context.bot.delete_message(chat_id=chat_id, message_id=msg_id)
            except:
                pass
        user_messages[chat_id] = []

def get_start_buttons():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🚛 LOGIN FAHRER", callback_data="login_fahrer"),
         InlineKeyboardButton("👔 LOGIN CEO", callback_data="login_ceo")]
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_state[chat_id] = "start"
    user_last_active[chat_id] = time.time()
    await delete_previous_messages(context, chat_id)
    await context.bot.send_photo(chat_id=chat_id, photo=InputFile(branding_path))
    msg = await update.message.reply_text("Willkommen 👋
Bitte wähle deine Rolle:", reply_markup=get_start_buttons())
    user_messages[chat_id] = [msg.message_id]

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat_id
    data = query.data
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
        user_state[chat_id] = "login_fahrer"
        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_message(chat_id=chat_id, text="📂 LOGIN FAHRER", reply_markup=reply_markup)
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
        user_state[chat_id] = "login_ceo"
        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_message(chat_id=chat_id, text="📂 LOGIN CEO", reply_markup=reply_markup)
        user_messages[chat_id] = [msg.message_id]

    elif data == "firma":
        msg = await query.message.reply_text("🏢 Firmenbereich")
        keyboard = [
            [InlineKeyboardButton("🧑‍✈️ FAHRER", callback_data="fahrer")],
            [InlineKeyboardButton("⬅️ ZURÜCK", callback_data="login_ceo")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_message(chat_id=chat_id, text="📂 LOGIN CEO ➜ FIRMA", reply_markup=reply_markup)
        user_state[chat_id] = "firma"
        user_messages[chat_id] = [msg.message_id]

    elif data == "fahrer":
        msg = await query.message.reply_text("📋 Fahrerbereich")
        keyboard = [
            [InlineKeyboardButton("📋 ALLE", callback_data="alle")],
            [InlineKeyboardButton("🔄 ERSATZ", callback_data="ersatz")],
            [InlineKeyboardButton("⬅️ ZURÜCK", callback_data="firma")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_message(chat_id=chat_id, text="📂 LOGIN CEO ➜ FIRMA ➜ FAHRER", reply_markup=reply_markup)
        user_state[chat_id] = "fahrer"
        user_messages[chat_id] = [msg.message_id]

    elif data == "alle":
        fahrer = load_driver_data()
        if not fahrer:
            msg = await query.message.reply_text("📋 Fahrerübersicht:
Keine Fahrer vorhanden.")
        else:
            text = "📋 Fahrerübersicht:
"
            for f in fahrer:
                text += f"• {f['vorname']} {f['name']} – ID: {f['id']}
"
            msg = await query.message.reply_text(text)
        keyboard = [
            [InlineKeyboardButton("🆕 NEU", callback_data="neu_fahrer")],
            [InlineKeyboardButton("✏️ ÄNDERN", callback_data="ändern_fahrer")],
            [InlineKeyboardButton("⬅️ ZURÜCK", callback_data="fahrer")]
        ]
        await context.bot.send_message(chat_id=chat_id, text="📂 LOGIN CEO ➜ FIRMA ➜ FAHRER ➜ ALLE", reply_markup=InlineKeyboardMarkup(keyboard))
        user_state[chat_id] = "alle"
        user_messages[chat_id] = [msg.message_id]

    elif data == "start":
        return await start(update, context)

def reset_inactive_users(app):
    async def reset():
        while True:
            now = time.time()
            for chat_id in list(user_last_active):
                if now - user_last_active[chat_id] > 120:
                    user_state[chat_id] = "start"
                    del user_last_active[chat_id]
            await asyncio.sleep(60)
    import asyncio
    app.create_task(reset())

if __name__ == "__main__":
    token = os.getenv("BOT_TOKEN")
    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    reset_inactive_users(app)
    app.run_polling()
