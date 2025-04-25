import logging
import os
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    ConversationHandler, MessageHandler, filters
)

from config import BOT_TOKEN, AWAITING_FAHRER_NAME, AWAITING_FAHRER_TELEFON, AWAITING_FAHRER_EMAIL, AWAITING_FAHRER_ID
from config import (AWAITING_LKW_KENNZEICHEN, AWAITING_LKW_MARKE, AWAITING_LKW_MODELL, AWAITING_LKW_BAUJAHR, AWAITING_LKW_TUEV,
                   AWAITING_PKW_KENNZEICHEN, AWAITING_PKW_MARKE, AWAITING_PKW_MODELL, AWAITING_PKW_BAUJAHR, AWAITING_PKW_TUEV,
                   AWAITING_SCHADEN_FAHRZEUG, AWAITING_SCHADEN_BESCHREIBUNG, AWAITING_SCHADEN_DATUM,
                   AWAITING_SUPERVISOR_NACHRICHT, AWAITING_TOUR_START_KM, AWAITING_TOUR_ZIEL, AWAITING_TOUR_ENDE_KM)
import handlers

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def main():
    """Start the bot."""
    # Create the Application
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", handlers.start))
    
    # Add conversation handler for adding new drivers
    fahrer_conv_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(handlers.handle_buttons, pattern="neuer_fahrer"),
            CallbackQueryHandler(handlers.handle_buttons, pattern="neuer_ersatzfahrer")
        ],
        states={
            AWAITING_FAHRER_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.handle_fahrer_name)],
            AWAITING_FAHRER_TELEFON: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.handle_fahrer_telefon)],
            AWAITING_FAHRER_EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.handle_fahrer_email)],
            AWAITING_FAHRER_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.handle_fahrer_id)],
        },
        fallbacks=[CallbackQueryHandler(handlers.handle_buttons, pattern="zurück")],
    )
    application.add_handler(fahrer_conv_handler)
    
    # Add conversation handler for adding new LKW
    lkw_conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(handlers.handle_buttons, pattern="neuer_lkw")],
        states={
            AWAITING_LKW_KENNZEICHEN: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.handle_lkw_kennzeichen)],
            AWAITING_LKW_MARKE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.handle_lkw_marke)],
            AWAITING_LKW_MODELL: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.handle_lkw_modell)],
            AWAITING_LKW_BAUJAHR: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.handle_lkw_baujahr)],
            AWAITING_LKW_TUEV: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.handle_lkw_tuev)],
        },
        fallbacks=[CallbackQueryHandler(handlers.handle_buttons, pattern="zurück")],
    )
    application.add_handler(lkw_conv_handler)
    
    # Add conversation handler for adding new PKW
    pkw_conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(handlers.handle_buttons, pattern="neuer_pkw")],
        states={
            AWAITING_PKW_KENNZEICHEN: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.handle_pkw_kennzeichen)],
            AWAITING_PKW_MARKE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.handle_pkw_marke)],
            AWAITING_PKW_MODELL: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.handle_pkw_modell)],
            AWAITING_PKW_BAUJAHR: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.handle_pkw_baujahr)],
            AWAITING_PKW_TUEV: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.handle_pkw_tuev)],
        },
        fallbacks=[CallbackQueryHandler(handlers.handle_buttons, pattern="zurück")],
    )
    application.add_handler(pkw_conv_handler)
    
    # Add conversation handler for reporting damages
    schaden_conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(handlers.handle_buttons, pattern="schaden_melden")],
        states={
            AWAITING_SCHADEN_FAHRZEUG: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.handle_schaden_fahrzeug)],
            AWAITING_SCHADEN_BESCHREIBUNG: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.handle_schaden_beschreibung)],
            AWAITING_SCHADEN_DATUM: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.handle_schaden_datum)],
        },
        fallbacks=[CallbackQueryHandler(handlers.handle_buttons, pattern="zurück")],
    )
    application.add_handler(schaden_conv_handler)
    
    # Add conversation handler for supervisor messages
    supervisor_conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(handlers.handle_buttons, pattern="supervisor_nachricht")],
        states={
            AWAITING_SUPERVISOR_NACHRICHT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.handle_supervisor_nachricht)],
        },
        fallbacks=[CallbackQueryHandler(handlers.handle_buttons, pattern="zurück")],
    )
    application.add_handler(supervisor_conv_handler)
    
    # Add conversation handler for tours
    tour_conv_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(handlers.handle_buttons, pattern="tour_starten"),
            CallbackQueryHandler(handlers.handle_buttons, pattern="tour_beenden")
        ],
        states={
            AWAITING_TOUR_START_KM: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.handle_tour_start_km)],
            AWAITING_TOUR_ZIEL: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.handle_tour_ziel)],
            AWAITING_TOUR_ENDE_KM: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.handle_tour_ende_km)],
        },
        fallbacks=[CallbackQueryHandler(handlers.handle_buttons, pattern="zurück")],
    )
    application.add_handler(tour_conv_handler)
    
    # Add callback query handler for buttons
    application.add_handler(CallbackQueryHandler(handlers.handle_buttons))
    
    # Add message handler for search input
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND & filters.ChatType.PRIVATE,
        handlers.handle_search_input
    ))
    
    # Add job for resetting inactive users
    application.job_queue.run_repeating(handlers.reset_user_menu, interval=60, first=60)
    
    # Start the Bot
    application.run_polling()

if __name__ == '__main__':
    main()
