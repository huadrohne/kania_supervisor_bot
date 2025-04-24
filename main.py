
import os
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from dotenv import load_dotenv

load_dotenv()

user_state = {}
user_messages = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    if update.message:
        await update.message.delete()

    branding_path = "branding.png"
    branding_msg = await context.bot.send_photo(chat_id=chat_id, photo=open(branding_path, 'rb'))
    await asyncio.sleep(3)
    await context.bot.delete_message(chat_id=chat_id, message_id=branding_msg.message_id)

    msg = await context.bot.send_message(
        chat_id=chat_id,
        text="Willkommen 👋\nBitte wähle deine Rolle:",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🚚 LOGIN FAHRER", callback_data="login_fahrer"),
             InlineKeyboardButton("👔 LOGIN CEO", callback_data="login_ceo")]
        ])
    )
    user_messages[chat_id] = [msg.message_id]
    user_state[chat_id] = "start"

async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    data = query.data
    chat_id = query.message.chat_id

    # Alte Nachrichten löschen
    if chat_id in user_messages:
        for msg_id in user_messages[chat_id]:
            try:
                await context.bot.delete_message(chat_id=chat_id, message_id=msg_id)
            except:
                pass

    if data == "login_fahrer":
        msg = await query.message.reply_text("✅ Willkommen auf der Fahrer Plattform")
        user_state[chat_id] = "login_fahrer"
        user_messages[chat_id] = [msg.message_id]

    elif data == "login_ceo":
        msg = await query.message.reply_text("✅ Willkommen auf der CEO Plattform")
        user_state[chat_id] = "login_ceo"
        user_messages[chat_id] = [msg.message_id]

    elif data == "start":
        return await start(update, context)

if __name__ == "__main__":
    token = os.getenv("BOT_TOKEN")
    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_buttons))
    app.run_polling()
