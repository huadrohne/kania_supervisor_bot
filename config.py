# config.py
import os

# Bot configuration
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("No BOT_TOKEN environment variable set!")

# Reset time in minutes (4 hours)
RESET_MINUTES = 240

# File paths
BRANDING_PATH = "branding.png"
DATABASE_PATH = "transport_bot.db"

# States for ConversationHandler - Fahrer
AWAITING_FAHRER_NAME = 1
AWAITING_FAHRER_TELEFON = 2
AWAITING_FAHRER_EMAIL = 3
AWAITING_FAHRER_ID = 4

# States for ConversationHandler - Fahrzeuge
AWAITING_LKW_KENNZEICHEN = 5
AWAITING_LKW_MARKE = 6
AWAITING_LKW_MODELL = 7
AWAITING_LKW_BAUJAHR = 8
AWAITING_LKW_TUEV = 9

AWAITING_PKW_KENNZEICHEN = 10
AWAITING_PKW_MARKE = 11
AWAITING_PKW_MODELL = 12
AWAITING_PKW_BAUJAHR = 13
AWAITING_PKW_TUEV = 14

# States for ConversationHandler - Schäden
AWAITING_SCHADEN_FAHRZEUG = 15
AWAITING_SCHADEN_BESCHREIBUNG = 16
AWAITING_SCHADEN_DATUM = 17
AWAITING_SCHADEN_BILD = 18

# States for ConversationHandler - Supervisor
AWAITING_SUPERVISOR_NACHRICHT = 19

# States for ConversationHandler - Tour
AWAITING_TOUR_START_KM = 20
AWAITING_TOUR_ZIEL = 21
AWAITING_TOUR_ENDE_KM = 22
