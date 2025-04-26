from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def create_inline_keyboard(buttons):
    """Creates an inline keyboard from a list of (text, callback_data) tuples."""
    return InlineKeyboardMarkup([[InlineKeyboardButton(text, callback_data=data)] for text, data in buttons])

# =========================
# Buttons Definitionen
# =========================

# Main Menü
MAIN_MENU_BUTTONS = [
    ("🚛 LOGIN FAHRER", "login_fahrer"),
    ("👔 LOGIN CEO", "login_ceo")
]

# Universal Back Button
ZURÜCK_BUTTONS = [
    ("⬅️ ZURÜCK", "zurück")
]

# Fahrer Bereich Menü
FAHRER_BEREICH_BUTTONS = [
    ("📅 KALENDER", "fahrer_kalender"),
    ("🛣️ TOUR", "fahrer_tour"),
    ("🪄 SUPERVISOR", "fahrer_supervisor"),
    ("⬅️ ZURÜCK", "zurück")
]

# CEO Bereich Menü
CEO_MENU_BUTTONS = [
    ("🗂️ BÜRO", "buero"),
    ("🏢 FIRMA", "firma"),
    ("📰 NEWS", "news"),
    ("📅 KALENDER CEO", "kalender_ceo"),
    ("⬅️ ZURÜCK", "zurück")
]

# Büro Bereich
BUERO_MENU_BUTTONS = [
    ("⬅️ ZURÜCK", "zurück")
]

# Firma Bereich
FIRMA_MENU_BUTTONS = [
    ("👷 FAHRER", "fahrer"),
    ("🛻 FAHRZEUGE", "fahrzeuge"),
    ("⬅️ ZURÜCK", "zurück")
]

# News Bereich
NEWS_MENU_BUTTONS = [
    ("⬅️ ZURÜCK", "zurück")
]

# Kalender CEO Bereich
KALENDER_CEO_MENU_BUTTONS = [
    ("⬅️ ZURÜCK", "zurück")
]

# Fahrer Bereich (unter Firma)
FAHRER_MENU_BUTTONS = [
    ("📋 ÜBERSICHT", "übersicht"),
    ("🔄 ERSATZFAHRER", "ersatz"),
    ("⬅️ ZURÜCK", "zurück")
]

# Übersicht Bereich
ÜBERSICHT_MENU_BUTTONS = [
    ("➕ NEUER FAHRER", "neuer_fahrer"),
    ("🔍 FAHRER SUCHEN", "fahrer_suchen"),
    ("⬅️ ZURÜCK", "zurück")
]

# Ersatzfahrer Bereich
ERSATZ_MENU_BUTTONS = [
    ("➕ NEUER ERSATZFAHRER", "neuer_ersatzfahrer"),
    ("⬅️ ZURÜCK", "zurück")
]

# Fahrzeuge Bereich
FAHRZEUGE_MENU_BUTTONS = [
    ("🚚 LKW", "lkw"),
    ("🚗 KFZ", "kfz"),
    ("🗓 TÜV", "tuev"),
    ("🔧 SCHÄDEN", "schaeden"),
    ("⬅️ ZURÜCK", "zurück")
]

# LKW Bereich
LKW_MENU_BUTTONS = [
    ("➕ NEUER LKW", "neuer_lkw"),
    ("🔍 LKW SUCHEN", "lkw_suchen"),
    ("⬅️ ZURÜCK", "zurück")
]

# KFZ Bereich
KFZ_MENU_BUTTONS = [
    ("➕ NEUER PKW", "neuer_pkw"),
    ("🔍 PKW SUCHEN", "pkw_suchen"),
    ("⬅️ ZURÜCK", "zurück")
]

# TÜV Bereich
TUEV_MENU_BUTTONS = [
    ("📊 TÜV ÜBERSICHT", "tuev_übersicht"),
    ("⬅️ ZURÜCK", "zurück")
]

# Schäden Bereich
SCHAEDEN_MENU_BUTTONS = [
    ("➕ SCHADEN MELDEN", "schaden_melden"),
    ("📋 SCHADENSLISTE", "schadensliste"),
    ("⬅️ ZURÜCK", "zurück")
]

# Tour Bereich (für Fahrer)
TOUR_MENU_BUTTONS = [
    ("🚀 TOUR STARTEN", "tour_starten"),
    ("⏹️ TOUR BEENDEN", "tour_beenden"),
    ("⬅️ ZURÜCK", "zurück")
]

# Supervisor Bereich (für Fahrer)
SUPERVISOR_MENU_BUTTONS = [
    ("📞 KONTAKT", "supervisor_kontakt"),
    ("📝 NACHRICHT", "supervisor_nachricht"),
    ("⬅️ ZURÜCK", "zurück")
]

# Kalender Bereich (für Fahrer)
KALENDER_MENU_BUTTONS = [
    ("📊 ÜBERSICHT", "kalender_übersicht"),
    ("📝 MEINE TOUREN", "kalender_touren"),
    ("⬅️ ZURÜCK", "zurück")
]

# Confirm Buttons
CONFIRM_KEYBOARD_BUTTONS = [
    ("✅ JA", "confirm_yes"),
    ("❌ NEIN", "confirm_no")
]

# =========================
# Keyboards bauen
# =========================

MAIN_MENU = create_inline_keyboard(MAIN_MENU_BUTTONS)
ZURÜCK_BUTTON = create_inline_keyboard(ZURÜCK_BUTTONS)
FAHRER_BEREICH_MENU = create_inline_keyboard(FAHRER_BEREICH_BUTTONS)
CEO_MENU = create_inline_keyboard(CEO_MENU_BUTTONS)
BUERO_MENU = create_inline_keyboard(BUERO_MENU_BUTTONS)
FIRMA_MENU = create_inline_keyboard(FIRMA_MENU_BUTTONS)
NEWS_MENU = create_inline_keyboard(NEWS_MENU_BUTTONS)
KALENDER_CEO_MENU = create_inline_keyboard(KALENDER_CEO_MENU_BUTTONS)
FAHRER_MENU = create_inline_keyboard(FAHRER_MENU_BUTTONS)
ÜBERSICHT_MENU = create_inline_keyboard(ÜBERSICHT_MENU_BUTTONS)
ERSATZ_MENU = create_inline_keyboard(ERSATZ_MENU_BUTTONS)
FAHRZEUGE_MENU = create_inline_keyboard(FAHRZEUGE_MENU_BUTTONS)
LKW_MENU = create_inline_keyboard(LKW_MENU_BUTTONS)
KFZ_MENU = create_inline_keyboard(KFZ_MENU_BUTTONS)
TUEV_MENU = create_inline_keyboard(TUEV_MENU_BUTTONS)
SCHAEDEN_MENU = create_inline_keyboard(SCHAEDEN_MENU_BUTTONS)
TOUR_MENU = create_inline_keyboard(TOUR_MENU_BUTTONS)
SUPERVISOR_MENU = create_inline_keyboard(SUPERVISOR_MENU_BUTTONS)
KALENDER_MENU = create_inline_keyboard(KALENDER_MENU_BUTTONS)
CONFIRM_KEYBOARD = create_inline_keyboard(CONFIRM_KEYBOARD_BUTTONS)