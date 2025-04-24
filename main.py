from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import os

user_state = {}
user_messages = {}

START_KEYBOARD = InlineKeyboardMarkup([
    [InlineKeyboardButton("🚚 LOGIN FAHRER", callback_data="login_fahrer"),
     InlineKeyboardButton("👔 LOGIN CEO", callback_data="login_ceo")]
])

def get_ceo_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🏢 FIRMA", callback_data="firma")],
        [InlineKeyboardButton("🏢 BÜRO", callback_data="buero")],
        [InlineKeyboardButton("🗓️ KALENDER", callback_data="kalender_ceo")],
        [InlineKeyboardButton("🆘 SUPPORT", callback_data="support_ceo")],
        [InlineKeyboardButton("⬅️ ZURÜCK", callback_data="start")]
    ])

def get_firma_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📂 FAHRER", callback_data="fahrer")],
        [InlineKeyboardButton("⬅️ ZURÜCK", callback_data="login_ceo")]
    ])

def get_fahrer_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📋 ALLE", callback_data="alle")],
        [InlineKeyboardButton("🔄 ERSATZ", callback_data="ersatz")],
        [InlineKeyboardButton("⬅️ ZURÜCK", callback_data="firma")]
    ])

def get_alle_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🆕 NEU", callback_data="neu")],
        [InlineKeyboardButton("✏️ ÄNDERN", callback_data="aendern")],
        [InlineKeyboardButton("⬅️ ZURÜCK", callback_data="fahrer")]
    ])

def get_fahrer_login_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🛣️ TOUREN", callback_data="touren")],
        [InlineKeyboardButton("🗓️ KALENDER", callback_data="kalender_fahrer")],
        [InlineKeyboardButton("🧑‍💼 SUPERVISOR", callback_data="supervisor")],
        [InlineKeyboardButton("⬅️ ZURÜCK", callback_data="start")]
    ])

def get_leere_ebene_keyboard(zurueck_callback):
    if zurueck_callback == "login_ceo":
        return InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ ZURÜCK", callback_data="login_ceo")]])
    else:
        return InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ ZURÜCK", callback_data="login_fahrer")]])

from telegram.constants import ParseMode

async def delete_old_messages(chat_id, context):
    if chat_id in user_messages:
        for msg_id in user_messages[chat_id]:
            try:
                await context.bot.delete_message(chat_id, msg_id)
            except:
                pass
        user_messages[chat_id] = []

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    await delete_old_messages(chat_id, context)

    msg = await context.bot.send_message(chat_id=chat_id, text="Willkommen 👋\nBitte wähle deine Rolle:", reply_markup=START_KEYBOARD)
    user_messages[chat_id] = [msg.message_id]
    user_state[chat_id] = "start"

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    chat_id = query.message.chat_id

    await delete_old_messages(chat_id, context)

    if data == "login_ceo":
        msg = await query.message.reply_text("✅ Willkommen auf der CEO Plattform", reply_markup=get_ceo_keyboard())
        user_state[chat_id] = "login_ceo"
        user_messages[chat_id] = [msg.message_id]

    elif data == "buero":
        msg = await query.message.reply_text("🏢 Bürobereich", reply_markup=get_leere_ebene_keyboard("login_ceo"))
        user_state[chat_id] = "buero"
        user_messages[chat_id] = [msg.message_id]

    elif data == "kalender_ceo":
        msg = await query.message.reply_text("🗓️ Kalenderbereich (CEO)", reply_markup=get_leere_ebene_keyboard("login_ceo"))
        user_state[chat_id] = "kalender_ceo"
        user_messages[chat_id] = [msg.message_id]

    elif data == "support_ceo":
        msg = await query.message.reply_text("🆘 Supportbereich", reply_markup=get_leere_ebene_keyboard("login_ceo"))
        user_state[chat_id] = "support_ceo"
        user_messages[chat_id] = [msg.message_id]

    elif data == "firma":
        msg = await query.message.reply_text("🏢 Firmenbereich", reply_markup=get_firma_keyboard())
        user_state[chat_id] = "firma"
        user_messages[chat_id] = [msg.message_id]

    elif data == "fahrer":
        msg1 = await query.message.reply_text("📂 LOGIN CEO ➜ FIRMA ➜ FAHRER")
        msg2 = await query.message.reply_text("📋 Fahrerübersicht: Keine Fahrer vorhanden.", reply_markup=get_fahrer_keyboard())
        user_state[chat_id] = "fahrer"
        user_messages[chat_id] = [msg1.message_id, msg2.message_id]

    elif data == "alle":
        msg = await query.message.reply_text("📋 Fahrer – Alle", reply_markup=get_alle_keyboard())
        user_state[chat_id] = "alle"
        user_messages[chat_id] = [msg.message_id]

    elif data == "ersatz":
        msg = await query.message.reply_text("🔄 Ersatzfahrer", reply_markup=get_leere_ebene_keyboard("fahrer"))
        user_state[chat_id] = "ersatz"
        user_messages[chat_id] = [msg.message_id]

    elif data == "login_fahrer":
        msg = await query.message.reply_text("✅ Willkommen auf der Fahrer Plattform", reply_markup=get_fahrer_login_keyboard())
        user_state[chat_id] = "login_fahrer"
        user_messages[chat_id] = [msg.message_id]

    elif data == "touren":
        msg = await query.message.reply_text("🛣️ Tourenbereich", reply_markup=get_leere_ebene_keyboard("login_fahrer"))
        user_state[chat_id] = "touren"
        user_messages[chat_id] = [msg.message_id]

    elif data == "kalender_fahrer":
        msg = await query.message.reply_text("🗓️ Kalenderbereich (Fahrer)", reply_markup=get_leere_ebene_keyboard("login_fahrer"))
        user_state[chat_id] = "kalender_fahrer"
        user_messages[chat_id] = [msg.message_id]

    elif data == "supervisor":
        msg = await query.message.reply_text("🧑‍💼 Supervisorbereich", reply_markup=get_leere_ebene_keyboard("login_fahrer"))
        user_state[chat_id] = "supervisor"
        user_messages[chat_id] = [msg.message_id]

    elif data == "start":
        return await start(update, context)

if __name__ == "__main__":
    token = os.getenv("BOT_TOKEN")
    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("Bot läuft...")
    app.run_polling()