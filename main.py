import asyncio
import datetime
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    ContextTypes, ConversationHandler, MessageHandler, filters
)

# === Konstanten für das Fahrerformular ===
(VORNAME, NACHNAME, GEBURTSTAG, NATIONALITÄT, SPRACHE, MOBIL, EINTRITT, PIN) = range(8)

# === Markups ===
def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🚛 LOGIN FAHRER", callback_data="login_fahrer")],
        [InlineKeyboardButton("👔 LOGIN CEO", callback_data="login_ceo")]
    ])

def ceo_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🏢 FIRMA", callback_data="firma")],
        [InlineKeyboardButton("⬅️ ZURÜCK", callback_data="zurueck_start")]
    ])

def firma_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🧑‍✈️ FAHRER", callback_data="fahrer")],
        [InlineKeyboardButton("⬅️ ZURÜCK", callback_data="zurueck_ceo")]
    ])

def fahrer_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📋 ALLE", callback_data="alle")],
        [InlineKeyboardButton("🔄 ERSATZ", callback_data="ersatz")],
        [InlineKeyboardButton("⬅️ ZURÜCK", callback_data="zurueck_firma")]
    ])

def ersatz_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⬅️ ZURÜCK", callback_data="zurueck_fahrer")]
    ])

# === Start & Branding ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.delete()
    context.user_data.clear()
    msg = await update.message.reply_text("Willkommen 👋\nBitte wähle deine Rolle:", reply_markup=main_menu())
    context.user_data["last_menu_msg"] = msg.message_id

# === Button-Handling ===
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    cid = query.message.chat.id

    # Alte Nachricht löschen
    try:
        await context.bot.delete_message(chat_id=cid, message_id=context.user_data.get("last_menu_msg", 0))
    except:
        pass

    pfad = ""
    reply_markup = None
    branding_needed = False

    if query.data == "login_fahrer":
        pfad = "📂 LOGIN FAHRER"
        reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ ZURÜCK", callback_data="zurueck_start")]])
        branding_needed = True

    elif query.data == "login_ceo":
        pfad = "📂 LOGIN CEO"
        reply_markup = ceo_menu
        branding_needed = True

    elif query.data == "firma":
        pfad = "📂 LOGIN CEO ➜ FIRMA"
        reply_markup = firma_menu()

    elif query.data == "fahrer":
        pfad = "📂 LOGIN CEO ➜ FIRMA ➜ FAHRER"
        reply_markup = fahrer_menu()

    elif query.data == "alle":
        pfad = "📂 LOGIN CEO ➜ FIRMA ➜ FAHRER ➜ ALLE"
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("⬅️ ZURÜCK", callback_data="zurueck_fahrer")]
        ])

    elif query.data == "ersatz":
        pfad = "📂 LOGIN CEO ➜ FIRMA ➜ FAHRER ➜ ERSATZ"
        reply_markup = ersatz_menu()

    elif query.data == "zurueck_start":
        pfad = "Willkommen 👋\nBitte wähle deine Rolle:"
        reply_markup = main_menu()

    elif query.data == "zurueck_ceo":
        pfad = "📂 LOGIN CEO"
        reply_markup = ceo_menu()

    elif query.data == "zurueck_firma":
        pfad = "📂 LOGIN CEO ➜ FIRMA"
        reply_markup = firma_menu()

    elif query.data == "zurueck_fahrer":
        pfad = "📂 LOGIN CEO ➜ FIRMA ➜ FAHRER"
        reply_markup = fahrer_menu()

    else:
        pfad = "❓ Unbekannter Button"
        reply_markup = main_menu()

    if branding_needed:
        branding_img = await context.bot.send_photo(cid, photo=open("branding.png", "rb"))
        branding_txt = await context.bot.send_message(cid, "Lizensiert für Kania Schüttguttransporte")
        await asyncio.sleep(2)
        await branding_img.delete()
        await branding_txt.delete()

    msg = await context.bot.send_message(cid, pfad, reply_markup=reply_markup)
    context.user_data["last_menu_msg"] = msg.message_id

# === Hauptprogramm ===
if __name__ == '__main__':
    app = ApplicationBuilder().token(os.getenv("BOT_TOKEN")).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.run_polling()