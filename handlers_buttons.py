import datetime
import logging
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

import keyboard_manager as kb
from config import AWAITING_FAHRER_NAME
from db_manager import get_db_manager
from handlers_base import send_branding

# Get database manager
db = get_db_manager()

async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks."""
    query = update.callback_query
    cid = query.message.chat_id
    await query.answer()
    
    # Get or create user state
    state = context.chat_data.setdefault(cid, {"state": "start", "last_active": datetime.datetime.utcnow()})
    state["last_active"] = datetime.datetime.utcnow()

    # Delete old status message if exists
    if "status_msg" in state:
        try:
            await context.bot.delete_message(cid, state["status_msg"])
        except Exception as e:
            logging.error(f"Error deleting status message: {e}")

    # Delete menu message if exists
    if "menu_msg" in state:
        try:
            await context.bot.delete_message(cid, state["menu_msg"])
        except Exception as e:
            logging.error(f"Error deleting menu message: {e}")

    cmd = query.data

    # ====== MAIN MENU OPTIONS ======
    if cmd == "login_fahrer":
        await send_branding(context, cid)
        msg = await query.message.reply_text(
            "✅ Willkommen auf der Fahrer Plattform",
            reply_markup=kb.FAHRER_BEREICH_MENU
        )
        state.update({"state": "login_fahrer", "status_msg": msg.message_id})

    elif cmd == "login_ceo":
        await send_branding(context, cid)
        msg = await query.message.reply_text(
            "✅ Willkommen auf der CEO Plattform",
            reply_markup=kb.CEO_MENU
        )
        state.update({"state": "ceo", "status_msg": msg.message_id})

    # ====== CEO UNTERMENÜS ======
    elif cmd == "buero":
        msg = await query.message.reply_text(
            "💼 BÜRO Bereich",
            reply_markup=kb.BUERO_MENU
        )
        state.update({"state": "buero", "status_msg": msg.message_id})

    elif cmd == "firma":
        msg = await query.message.reply_text(
            "🏢 FIRMA Bereich",
            reply_markup=kb.FIRMA_MENU
        )
        state.update({"state": "firma", "status_msg": msg.message_id})

    elif cmd == "kalender_ceo":
        msg = await query.message.reply_text(
            "📅 KALENDER CEO Bereich",
            reply_markup=kb.KALENDER_CEO_MENU
        )
        state.update({"state": "kalender_ceo", "status_msg": msg.message_id})

    elif cmd == "news":
        msg = await query.message.reply_text(
            "📰 NEWS Bereich",
            reply_markup=kb.NEWS_MENU
        )
        state.update({"state": "news", "status_msg": msg.message_id})

    elif cmd == "support":
        msg = await query.message.reply_text(
            "⚙️ SUPPORT Bereich",
            reply_markup=kb.SUPPORT_MENU
        )
        state.update({"state": "support", "status_msg": msg.message_id})

    # ====== ZURÜCK BUTTON ======
    elif cmd == "zurück":
        prev = state.get("state")

        if prev in ["login_fahrer", "ceo", "buero", "firma", "kalender_ceo", "news", "support"]:
            msg = await query.message.reply_text(
                "✅ Willkommen auf der CEO Plattform",
                reply_markup=kb.CEO_MENU
            )
            state.update({"state": "ceo", "menu_msg": msg.message_id})
        else:
            msg = await query.message.reply_text(
                "Willkommen 👋\nBitte wähle deine Rolle:",
                reply_markup=kb.MAIN_MENU
            )
            state.update({"state": "start", "menu_msg": msg.message_id})
        
        return ConversationHandler.END