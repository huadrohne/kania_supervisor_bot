from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def create_inline_keyboard(buttons, row_width=2):
    """Creates an inline keyboard with multiple buttons per row."""
    keyboard = []
    row = []
    for text, data in buttons:
        row.append(InlineKeyboardButton(text, callback_data=data))
        if len(row) >= row_width:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    return InlineKeyboardMarkup(keyboard)

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
    ("💼 BÜRO", "buero"),
    ("🏢 FIRMA", "firma"),
    ("📅 KALENDER CEO", "kalender_ceo"),
    ("📰 NEWS", "news"),
    ("⚙️ SUPPORT", "support"),
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

# Support Bereich
SUPPORT_MENU_BUTTONS = [
    ("❓ FAQ", "support_faq"),
    ("✉️ KONTAKT", "support_kontakt"),
    ("⚙️ TECHNIK", "support_technik"),
    ("⬅️ ZURÜCK", "zurück")
]

# Fahrer Bereich unter Firma
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

# Tour Bereich
TOUR_MENU_BUTTONS = [
    ("🚀 TOUR STARTEN", "tour_starten"),
    ("⏹️ TOUR BEENDEN", "tour_beenden"),
    ("⬅️ ZURÜCK", "zurück")
]

# Supervisor Bereich
SUPERVISOR_MENU_BUTTONS = [
    ("📞 KONTAKT", "supervisor_kontakt"),
    ("📝 NACHRICHT", "supervisor_nachricht"),
    ("⬅️ ZURÜCK", "zurück")
]

# Kalender Bereich Fahrer
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

MAIN_MENU = create_inline_keyboard(MAIN_MENU_BUTTONS, row_width=2)
ZURÜCK_BUTTON = create_inline_keyboard(ZURÜCK_BUTTONS, row_width=1)
FAHRER_BEREICH_MENU = create_inline_keyboard(FAHRER_BEREICH_BUTTONS, row_width=2)
CEO_MENU = create_inline_keyboard(CEO_MENU_BUTTONS, row_width=2)
BUERO_MENU = create_inline_keyboard(BUERO_MENU_BUTTONS, row_width=1)
FIRMA_MENU = create_inline_keyboard(FIRMA_MENU_BUTTONS, row_width=2)
NEWS_MENU = create_inline_keyboard(NEWS_MENU_BUTTONS, row_width=1)
KALENDER_CEO_MENU = create_inline_keyboard(KALENDER_CEO_MENU_BUTTONS, row_width=1)
SUPPORT_MENU = create_inline_keyboard(SUPPORT_MENU_BUTTONS, row_width=2)
FAHRER_MENU = create_inline_keyboard(FAHRER_MENU_BUTTONS, row_width=2)
ÜBERSICHT_MENU = create_inline_keyboard(ÜBERSICHT_MENU_BUTTONS, row_width=2)
ERSATZ_MENU = create_inline_keyboard(ERSATZ_MENU_BUTTONS, row_width=1)
FAHRZEUGE_MENU = create_inline_keyboard(FAHRZEUGE_MENU_BUTTONS, row_width=2)
LKW_MENU = create_inline_keyboard(LKW_MENU_BUTTONS, row_width=2)
KFZ_MENU = create_inline_keyboard(KFZ_MENU_BUTTONS, row_width=2)
TUEV_MENU = create_inline_keyboard(TUEV_MENU_BUTTONS, row_width=1)
SCHAEDEN_MENU = create_inline_keyboard(SCHAEDEN_MENU_BUTTONS, row_width=2)
TOUR_MENU = create_inline_keyboard(TOUR_MENU_BUTTONS, row_width=2)
SUPERVISOR_MENU = create_inline_keyboard(SUPERVISOR_MENU_BUTTONS, row_width=2)
KALENDER_MENU = create_inline_keyboard(KALENDER_MENU_BUTTONS, row_width=2)
CONFIRM_KEYBOARD = create_inline_keyboard(CONFIRM_KEYBOARD_BUTTONS, row_width=2)