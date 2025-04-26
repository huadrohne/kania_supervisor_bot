import asyncio
import datetime
import logging
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

import keyboard_manager as kb
from config import (RESET_MINUTES, BRANDING_PATH, 
                   AWAITING_FAHRER_NAME, AWAITING_FAHRER_TELEFON, AWAITING_FAHRER_EMAIL, AWAITING_FAHRER_ID)
from db_manager import get_db_manager

# Get database manager
db = get_db_manager()

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

async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks."""
    query = update.callback_query
    cid = query.message.chat_id
    await query.answer()
    
    # Get or create user state
    state = context.chat_data.setdefault(cid, {"state": "start", "last_active": datetime.datetime.utcnow()})
    state["last_active"] = datetime.datetime.utcnow()

    # Delete old messages
    for key in ["status_msg", "menu_msg"]:
        if key in state:
            try:
                await context.bot.delete_message(cid, state[key])
            except:
                pass

    cmd = query.data

    # Basic menu handling only
    if cmd == "login_fahrer":
        await send_branding(context, cid)
        msg = await query.message.reply_text("✅ Willkommen auf der Fahrer Plattform", reply_markup=kb.ZURÜCK_BUTTON)
        state.update({"state": "login_fahrer", "status_msg": msg.message_id})

    elif cmd == "login_ceo":
        await send_branding(context, cid)
        msg = await query.message.reply_text("✅ Willkommen auf der CEO Plattform", reply_markup=kb.ZURÜCK_BUTTON)
        state.update({"state": "ceo", "status_msg": msg.message_id})

    elif cmd == "zurück":
        msg = await query.message.reply_text("Willkommen 👋\nBitte wähle deine Rolle:", reply_markup=kb.MAIN_MENU)
        state.update({"state": "start", "menu_msg": msg.message_id})
    
    return ConversationHandler.END

# Dummy handlers for conversations
async def handle_fahrer_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Dummy handler for testing."""
    cid = update.effective_chat.id
    await update.message.delete()
    msg = await update.message.reply_text("Diese Funktion ist noch nicht implementiert.", reply_markup=kb.ZURÜCK_BUTTON)
    context.chat_data[cid]["status_msg"] = msg.message_id
    return AWAITING_FAHRER_TELEFON

async def handle_fahrer_telefon(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return AWAITING_FAHRER_EMAIL

async def handle_fahrer_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return AWAITING_FAHRER_ID

async def handle_fahrer_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return ConversationHandler.END

async def handle_search_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle search term input."""
    return ConversationHandler.END