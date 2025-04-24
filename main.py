import asyncio
import datetime
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    ContextTypes
)

RESET_MINUTEN = 2

def get_main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🚚 LOGIN FAHRER", callback_data="login_fahrer"),
         InlineKeyboardButton("👔 LOGIN CEO", callback_data="login_ceo")]
    ])

def get_ceo_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🏢 BÜRO", callback_data="ceo_buero")],
        [InlineKeyboardButton("📅 KALENDER", callback_data="ceo_kalender")],
        [InlineKeyboardButton("🛟 SUPPORT", callback_data="ceo_support")],
        [InlineKeyboardButton("⬅️ ZURÜCK", callback_data="zurueck_start")]
    ])

def get_firma_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("👷 FAHRER", callback_data="fahrer")],
        [InlineKeyboardButton("⬅️ ZURÜCK", callback_data="zurueck_ceo")]
    ])

def get_fahrer_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📅 KALENDER", callback_data="fahrer_kalender")],
        [InlineKeyboardButton("🛰️ SUPERVISOR", callback_data="fahrer_supervisor")],
        [InlineKeyboardButton("🚛 TOUREN", callback_data="fahrer_touren")],
        [InlineKeyboardButton("⬅️ ZURÜCK", callback_data="zurueck_start")]
    ])

def get_alle_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🆕 NEU", callback_data="neu")],
        [InlineKeyboardButton("✏️ ÄNDERN", callback_data="aendern")],
        [InlineKeyboardButton("⬅️ ZURÜCK", callback_data="zurueck_fahrer")]
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cid = update.effective_chat.id
    context.chat_data[cid] = {"state": "start", "last_active": datetime.datetime.utcnow()}
    await update.message.reply_text("Willkommen 👋\nBitte wähle deine Rolle:", reply_markup=get_main_menu())

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    cid = query.message.chat_id
    data = query.data
    context.chat_data[cid]["last_active"] = datetime.datetime.utcnow()

    if data == "login_fahrer":
        await query.message.reply_text("📂 LOGIN FAHRER", reply_markup=get_fahrer_menu())

    elif data == "login_ceo":
        await query.message.reply_text("📂 LOGIN CEO", reply_markup=get_ceo_menu())

    elif data == "ceo_buero":
        await query.message.reply_text("📂 LOGIN CEO ➜ BÜRO", reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("⬅️ ZURÜCK", callback_data="login_ceo")]
        ]))

    elif data == "ceo_kalender":
        await query.message.reply_text("📂 LOGIN CEO ➜ KALENDER", reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("⬅️ ZURÜCK", callback_data="login_ceo")]
        ]))

    elif data == "ceo_support":
        await query.message.reply_text("📂 LOGIN CEO ➜ SUPPORT", reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("⬅️ ZURÜCK", callback_data="login_ceo")]
        ]))

    elif data == "fahrer":
        await query.message.reply_text("📂 LOGIN CEO ➜ FIRMA ➜ FAHRER", reply_markup=get_alle_menu())

    elif data == "zurueck_ceo":
        await query.message.reply_text("📂 LOGIN CEO", reply_markup=get_ceo_menu())

    elif data == "zurueck_fahrer":
        await query.message.reply_text("📂 LOGIN CEO ➜ FIRMA ➜ FAHRER", reply_markup=get_fahrer_menu())

    elif data == "zurueck_start":
        await query.message.reply_text("Willkommen 👋\nBitte wähle deine Rolle:", reply_markup=get_main_menu())

async def reset_user_menu(context: ContextTypes.DEFAULT_TYPE):
    now = datetime.datetime.utcnow()
    for chat_id, data in context.chat_data.items():
        last = data.get("last_active")
        if last and (now - last).total_seconds() > RESET_MINUTEN * 60:
            await context.bot.send_message(chat_id, "⏳ Zurück zum Hauptmenü", reply_markup=get_main_menu())
            context.chat_data[chat_id] = {"state": "start", "last_active": now}

if __name__ == '__main__':
    app = ApplicationBuilder().token(os.getenv("BOT_TOKEN")).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.job_queue.run_repeating(reset_user_menu, interval=60, first=60)
    app.run_polling()
