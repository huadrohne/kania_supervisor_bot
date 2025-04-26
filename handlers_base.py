import asyncio
import datetime
import logging
from telegram import Update
from telegram.ext import ContextTypes

import keyboard_manager as kb
from config import RESET_MINUTES, BRANDING_PATH

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command handler."""
    context.chat_data[update.effective_chat.id] = {"state": "start", "last_active": datetime.datetime.utcnow()}
    await update.message.delete()
    msg = await update.message.reply_text("Willkommen 👋\nBitte wähle deine Rolle:", reply_markup=kb.MAIN_MENU)
    context.chat_data[update.effective_chat.id]["menu_msg"] = msg.message_id

async def reset_user_menu(context: ContextTypes.DEFAULT_TYPE):
    """Reset user menu after inactivity period."""
    now = datetime.datetime.utcnow()
    for chat_id, data in context.chat_data.items():
        last_active = data.get("last_active")
        if last_active and (now - last_active).total_seconds() > RESET_MINUTES * 60:
            await context.bot.send_message(chat_id, "⏳ Zurück zum Hauptmenü aufgrund Inaktivität", reply_markup=kb.MAIN_MENU)
            context.chat_data[chat_id] = {"state": "start", "last_active": now}

async def send_branding(context, chat_id):
    """Send branding image and message."""
    try:
        branding = await context.bot.send_photo(chat_id, photo=open(BRANDING_PATH, "rb"))
        text = await context.bot.send_message(chat_id, "Lizensiert für Kania Schüttguttransporte")
        await asyncio.sleep(2)
        await branding.delete()
        await text.delete()
    except Exception as e:
        logging.error(f"Error sending branding: {e}")