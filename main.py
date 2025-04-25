import asyncio
import datetime
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    ContextTypes, ConversationHandler, MessageHandler, filters
)

RESET_MINUTES = 2
BRANDING_PATH = "branding.png"

def inline_keyboard(buttons):
    return InlineKeyboardMarkup([[InlineKeyboardButton(text, callback_data=data)] for text, data in buttons])

main_menu = inline_keyboard([("🚛 LOGIN FAHRER", "login_fahrer"), ("👔 LOGIN CEO", "login_ceo")])
zurück_button = inline_keyboard([("⬅️ ZURÜCK", "zurück")])
firma_menu = inline_keyboard([("🏢 FIRMA", "firma"), ("⬅️ ZURÜCK", "zurück")])
fahrer_menu = inline_keyboard([("👷 FAHRER", "fahrer"), ("⬅️ ZURÜCK", "zurück")])
alle_menu = inline_keyboard([("📋 ALLE", "alle"), ("🔄 ERSATZ", "ersatz"), ("⬅️ ZURÜCK", "zurück")])
ersatz_menu = inline_keyboard([("⬅️ ZURÜCK", "zurück")])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.chat_data[update.effective_chat.id] = {"state": "start", "last_active": datetime.datetime.utcnow()}
    await update.message.delete()
    msg = await update.message.reply_text("Willkommen 👋\nBitte wähle deine Rolle:", reply_markup=main_menu)
    context.chat_data[update.effective_chat.id]["menu_msg"] = msg.message_id

async def reset_user_menu(context: ContextTypes.DEFAULT_TYPE):
    now = datetime.datetime.utcnow()
    for chat_id, data in context.chat_data.items():
        last_active = data.get("last_active")
        if last_active and (now - last_active).total_seconds() > RESET_MINUTES * 60:
            await context.bot.send_message(chat_id, "⏳ Zurück zum Hauptmenü", reply_markup=main_menu)
            context.chat_data[chat_id] = {"state": "start", "last_active": now}

async def send_branding(context, chat_id):
    branding = await context.bot.send_photo(chat_id, photo=open(BRANDING_PATH, "rb"))
    text = await context.bot.send_message(chat_id, "Lizensiert für Kania Schüttguttransporte")
    await asyncio.sleep(2)
    await branding.delete()
    await text.delete()

async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    cid = query.message.chat_id
    await query.answer()
    state = context.chat_data.setdefault(cid, {"state": "start", "last_active": datetime.datetime.utcnow()})
    state["last_active"] = datetime.datetime.utcnow()

    # alte Statusnachricht löschen
    if "status_msg" in state:
        try:
            await context.bot.delete_message(cid, state["status_msg"])
        except:
            pass

    # Menü-Nachricht löschen
    if "menu_msg" in state:
        try:
            await context.bot.delete_message(cid, state["menu_msg"])
        except:
            pass

    cmd = query.data

    if cmd == "login_fahrer":
        await send_branding(context, cid)
        msg = await query.message.reply_text("✅ Willkommen auf der Fahrer Plattform", reply_markup=zurück_button)
        state.update({"state": "login_fahrer", "status_msg": msg.message_id})

    elif cmd == "login_ceo":
        await send_branding(context, cid)
        msg = await query.message.reply_text("✅ Willkommen auf der CEO Plattform", reply_markup=firma_menu)
        state.update({"state": "ceo", "status_msg": msg.message_id})

    elif cmd == "firma":
        msg = await query.message.reply_text("LOGIN CEO/ FIRMA", reply_markup=fahrer_menu)
        state.update({"state": "firma", "status_msg": msg.message_id})

    elif cmd == "fahrer":
        msg = await query.message.reply_text("LOGIN CEO/ FIRMA/ FAHRER", reply_markup=alle_menu)
        state.update({"state": "fahrer", "status_msg": msg.message_id})

    elif cmd == "alle":
        msg = await query.message.reply_text("📋 Fahrerübersicht: Keine Fahrer vorhanden.", reply_markup=alle_menu)
        state.update({"state": "alle", "status_msg": msg.message_id})

    elif cmd == "ersatz":
        msg = await query.message.reply_text("🔄 Ersatzfahrer-Verwaltung", reply_markup=ersatz_menu)
        state.update({"state": "ersatz", "status_msg": msg.message_id})

    elif cmd == "zurück":
        prev = state.get("state")
        if prev == "alle" or prev == "ersatz":
            msg = await query.message.reply_text("LOGIN CEO/ FIRMA/ FAHRER", reply_markup=alle_menu)
            state.update({"state": "fahrer", "status_msg": msg.message_id})
        elif prev == "fahrer":
            msg = await query.message.reply_text("LOGIN CEO/ FIRMA", reply_markup=fahrer_menu)
            state.update({"state": "firma", "status_msg": msg.message_id})
        elif prev == "firma":
            msg = await query.message.reply_text("✅ Willkommen auf der CEO Plattform", reply_markup=firma_menu)
            state.update({"state": "ceo", "status_msg": msg.message_id})
        elif prev == "login_fahrer" or prev == "ceo":
            msg = await query.message.reply_text("Willkommen 👋\nBitte wähle deine Rolle:", reply_markup=main_menu)
            state.update({"state": "start", "menu_msg": msg.message_id})
        else:
            msg = await query.message.reply_text("Willkommen 👋\nBitte wähle deine Rolle:", reply_markup=main_menu)
            state.update({"state": "start", "menu_msg": msg.message_id})

if __name__ == '__main__':
    app = ApplicationBuilder().token(os.getenv("BOT_TOKEN")).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_buttons))
    app.job_queue.run_repeating(reset_user_menu, interval=60, first=60)
    app.run_polling()
