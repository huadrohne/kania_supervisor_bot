import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CallbackQueryHandler, CommandHandler,
    ContextTypes, MessageHandler, filters
)

BOT_TOKEN = "DEIN_BOT_TOKEN"

user_states = {}
fahrer_liste = []
branding_message_ids = {}

# Start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    # Branding + Lizenz
    branding = await context.bot.send_photo(chat_id=chat_id, photo=open("branding.png", "rb"))
    lizenz = await context.bot.send_message(chat_id=chat_id, text="Lizensiert für Kania Schüttguttransporte")
    branding_message_ids[chat_id] = [branding.message_id, lizenz.message_id]

    await asyncio.sleep(3)
    for msg_id in branding_message_ids[chat_id]:
        await context.bot.delete_message(chat_id=chat_id, message_id=msg_id)

    await update.message.delete()

    # Willkommen
    msg = await context.bot.send_message(
        chat_id=chat_id,
        text="Willkommen 👋\nBitte wähle deine Rolle:",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🚛 LOGIN FAHRER", callback_data="login_fahrer"),
             InlineKeyboardButton("👔 LOGIN CEO", callback_data="login_ceo")]
        ])
    )
    user_states[chat_id] = {"ebene": "start", "msg_id": msg.message_id}


# Zurück zur Startansicht
async def reset_to_start(context: ContextTypes.DEFAULT_TYPE, chat_id):
    if chat_id in user_states:
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=user_states[chat_id].get("msg_id"))
        except:
            pass
    await context.bot.send_message(
        chat_id=chat_id,
        text="Willkommen 👋\nBitte wähle deine Rolle:",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🚛 LOGIN FAHRER", callback_data="login_fahrer"),
             InlineKeyboardButton("👔 LOGIN CEO", callback_data="login_ceo")]
        ])
    )
    user_states[chat_id] = {"ebene": "start"}


# Button Handler
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat.id

    if chat_id in user_states:
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=user_states[chat_id].get("msg_id"))
        except:
            pass

    match query.data:
        case "login_fahrer":
            msg = await query.message.reply_text("✅ Willkommen auf der Fahrer Plattform",
                                                 reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ ZURÜCK", callback_data="zurueck_start")]]))
            user_states[chat_id] = {"ebene": "login_fahrer", "msg_id": msg.message_id}

        case "login_ceo":
            msg = await query.message.reply_text("✅ Willkommen auf der CEO Plattform",
                                                 reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏢 FIRMA", callback_data="firma"),
                                                                                     InlineKeyboardButton("⬅️ ZURÜCK", callback_data="zurueck_start")]]))
            user_states[chat_id] = {"ebene": "login_ceo", "msg_id": msg.message_id}

        case "firma":
            msg = await query.message.reply_text("🏢 Firmenbereich",
                                                 reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🧍‍♂️ FAHRER", callback_data="fahrer"),
                                                                                     InlineKeyboardButton("⬅️ ZURÜCK", callback_data="zurueck_ceo")]]))
            user_states[chat_id] = {"ebene": "firma", "msg_id": msg.message_id}

        case "fahrer":
            if not fahrer_liste:
                text = "📋 Fahrerübersicht: Keine Fahrer vorhanden."
            else:
                text = "📋 Fahrerübersicht:\n" + "\n".join(fahrer_liste)

            msg = await query.message.reply_text(text,
                                                 reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📂 ALLE", callback_data="alle"),
                                                                                     InlineKeyboardButton("⬅️ ZURÜCK", callback_data="zurueck_firma")]]))
            user_states[chat_id] = {"ebene": "fahrer", "msg_id": msg.message_id}

        case "alle":
            msg = await query.message.reply_text("Fahreraktionen:",
                                                 reply_markup=InlineKeyboardMarkup([
                                                     [InlineKeyboardButton("🆕 NEU", callback_data="neu")],
                                                     [InlineKeyboardButton("📝 ÄNDERN", callback_data="ändern")],
                                                     [InlineKeyboardButton("⬅️ ZURÜCK", callback_data="zurueck_fahrer")]
                                                 ]))
            user_states[chat_id] = {"ebene": "alle", "msg_id": msg.message_id}

        case "neu":
            await query.message.reply_text("Bitte gib den **Vornamen** des Fahrers ein:")
            user_states[chat_id] = {"ebene": "fahrer_neu", "daten": {}}

        case "zurueck_start":
            await reset_to_start(context, chat_id)

        case "zurueck_ceo":
            msg = await query.message.reply_text("✅ Willkommen auf der CEO Plattform",
                                                 reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏢 FIRMA", callback_data="firma"),
                                                                                     InlineKeyboardButton("⬅️ ZURÜCK", callback_data="zurueck_start")]]))
            user_states[chat_id] = {"ebene": "login_ceo", "msg_id": msg.message_id}

        case "zurueck_firma":
            msg = await query.message.reply_text("🏢 Firmenbereich",
                                                 reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🧍‍♂️ FAHRER", callback_data="fahrer"),
                                                                                     InlineKeyboardButton("⬅️ ZURÜCK", callback_data="zurueck_ceo")]]))
            user_states[chat_id] = {"ebene": "firma", "msg_id": msg.message_id}

        case "zurueck_fahrer":
            if not fahrer_liste:
                text = "📋 Fahrerübersicht: Keine Fahrer vorhanden."
            else:
                text = "📋 Fahrerübersicht:\n" + "\n".join(fahrer_liste)
            msg = await query.message.reply_text(text,
                                                 reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📂 ALLE", callback_data="alle"),
                                                                                     InlineKeyboardButton("⬅️ ZURÜCK", callback_data="zurueck_firma")]]))
            user_states[chat_id] = {"ebene": "fahrer", "msg_id": msg.message_id}


# Eingaben erfassen (Fahrer anlegen)
async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    text = update.message.text

    if user_states.get(chat_id, {}).get("ebene") == "fahrer_neu":
        user_states[chat_id]["daten"]["vorname"] = text
        user_states[chat_id]["ebene"] = "fahrer_name"
        await update.message.reply_text("Bitte gib den **Nachnamen** ein:")
    elif user_states.get(chat_id, {}).get("ebene") == "fahrer_name":
        user_states[chat_id]["daten"]["nachname"] = text
        daten = user_states[chat_id]["daten"]
        daten["id"] = f"Fahrer_{len(fahrer_liste)+1:03}"
        fahrer_liste.append(f"{daten['id']}: {daten['vorname']} {daten['nachname']}")
        await update.message.reply_text("✅ Fahrer wurde hinzugefügt!")
        msg = await update.message.reply_text("📋 Fahrerübersicht:\n" + "\n".join(fahrer_liste),
                                              reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📂 ALLE", callback_data="alle"),
                                                                                  InlineKeyboardButton("⬅️ ZURÜCK", callback_data="zurueck_firma")]]))
        user_states[chat_id] = {"ebene": "fahrer", "msg_id": msg.message_id}


# Bot starten
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(buttons))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    app.run_polling()