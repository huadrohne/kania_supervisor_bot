from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def create_inline_keyboard(buttons):
    """Creates an inline keyboard from a list of (text, callback_data) tuples."""
    return InlineKeyboardMarkup([[InlineKeyboardButton(text, callback_data=data)] for text, data in buttons])

# Main Menu
MAIN_MENU = create_inline_keyboard([
    ("🚛 LOGIN FAHRER", "login_fahrer"), 
    ("👔 LOGIN CEO", "login_ceo")
])

# Universal Back Button
ZURÜCK_BUTTON = create_inline_keyboard([("⬅️ ZURÜCK", "zurück")])

# Fahrer Area Menus
FAHRER_BEREICH_MENU = create_inline_keyboard([
    ("📅 KALENDER", "fahrer_kalender"),
    ("🛣️ TOUR", "fahrer_tour"),
    ("🪄 SUPERVISOR", "fahrer_supervisor"),
    ("⬅️ ZURÜCK", "zurück")
])

# CEO Area Menus
CEO_MENU = create_inline_keyboard([
    ("🗂️ BÜRO", "büro"),
    ("🏢 FIRMA", "firma"),
    ("📰 NEWS", "news"),
    ("📅 KALENDER CEO", "kalender_ceo"),
    ("⬅️ ZURÜCK", "zurück")
])

# Büro Bereich
BÜRO_MENU = create_inline_keyboard([
    ("⬅️ ZURÜCK", "zurück")
])

# Firma Bereich
FIRMA_MENU = create_inline_keyboard([
    ("👷 FAHRER", "fahrer"),
    ("🛻 FAHRZEUGE", "fahrzeuge"),
    ("⬅️ ZURÜCK", "zurück")
])

# News Bereich
NEWS_MENU = create_inline_keyboard([
    ("⬅️ ZURÜCK", "zurück")
])

# Kalender CEO Bereich
KALENDER_CEO_MENU = create_inline_keyboard([
    ("⬅️ ZURÜCK", "zurück")
])

# Fahrer Bereich (unter Firma)
FAHRER_MENU = create_inline_keyboard([
    ("📋 ÜBERSICHT", "übersicht"),
    ("🔄 ERSATZFAHRER", "ersatz"),
    ("⬅️ ZURÜCK", "zurück")
])

# Übersicht Bereich
ÜBERSICHT_MENU = create_inline_keyboard([
    ("➕ NEUER FAHRER", "neuer_fahrer"),
    ("🔍 FAHRER SUCHEN", "fahrer_suchen"),
    ("⬅️ ZURÜCK", "zurück")
])

# Ersatzfahrer Bereich
ERSATZ_MENU = create_inline_keyboard([
    ("➕ NEUER ERSATZFAHRER", "neuer_ersatzfahrer"),
    ("⬅️ ZURÜCK", "zurück")
])

# Fahrzeuge Bereich
FAHRZEUGE_MENU = create_inline_keyboard([
    ("🚚 LKW", "lkw"),
    ("🚗 KFZ", "kfz"),
    ("🗓 TÜV", "tuev"),
    ("🔧 SCHÄDEN", "schaeden"),
    ("⬅️ ZURÜCK", "zurück")
])

# LKW Bereich
LKW_MENU = create_inline_keyboard([
    ("➕ NEUER LKW", "neuer_lkw"),
    ("🔍 LKW SUCHEN", "lkw_suchen"),
    ("⬅️ ZURÜCK", "zurück")
])

# KFZ Bereich
KFZ_MENU = create_inline_keyboard([
    ("➕ NEUER PKW", "neuer_pkw"),
    ("🔍 PKW SUCHEN", "pkw_suchen"),
    ("⬅️ ZURÜCK", "zurück")
])

# TÜV Bereich
TUEV_MENU = create_inline_keyboard([
    ("📊 TÜV ÜBERSICHT", "tuev_übersicht"),
    ("⬅️ ZURÜCK", "zurück")
])

# Schäden Bereich
SCHAEDEN_MENU = create_inline_keyboard([
    ("➕ SCHADEN MELDEN", "schaden_melden"),
    ("📋 SCHADENSLISTE", "schadensliste"),
    ("⬅️ ZURÜCK", "zurück")
])

# Confirm keyboard for various actions
CONFIRM_KEYBOARD = create_inline_keyboard([
    ("✅ JA", "confirm_yes"), 
    ("❌ NEIN", "confirm_no")
])

# Tour Bereich (für Fahrer)
TOUR_MENU = create_inline_keyboard([
    ("🚀 TOUR STARTEN", "tour_starten"),
    ("⏹️ TOUR BEENDEN", "tour_beenden"),
    ("⬅️ ZURÜCK", "zurück")
])

# Supervisor Bereich (für Fahrer)
SUPERVISOR_MENU = create_inline_keyboard([
    ("📞 KONTAKT", "supervisor_kontakt"),
    ("📝 NACHRICHT", "supervisor_nachricht"),
    ("⬅️ ZURÜCK", "zurück")
])

# Kalender Bereich (für Fahrer)
KALENDER_MENU = create_inline_keyboard([
    ("📊 ÜBERSICHT", "kalender_übersicht"),
    ("📝 MEINE TOUREN", "kalender_touren"),
    ("⬅️ ZURÜCK", "zurück")
])
