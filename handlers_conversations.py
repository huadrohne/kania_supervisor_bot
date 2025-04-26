# handlers_conversations.py
import datetime
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
import keyboard_manager as kb
from config import AWAITING_FAHRER_TELEFON

async def handle_fahrer_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Dummy handler for fahrer name."""
    cid = update.effective_chat.id
    # Einfacher Platzhalter
    msg = await update.message.reply_text("Dummy-Funktion - Noch nicht implementiert", reply_markup=kb.ZURÜCK_BUTTON)
    context.chat_data[cid]["status_msg"] = msg.message_id
    return AWAITING_FAHRER_TELEFON