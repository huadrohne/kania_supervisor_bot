import asyncio
import datetime
import logging
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

import keyboard_manager as kb
from config import (RESET_MINUTES, BRANDING_PATH, 
                   AWAITING_FAHRER_NAME, AWAITING_FAHRER_TELEFON, AWAITING_FAHRER_EMAIL, AWAITING_FAHRER_ID,
                   AWAITING_LKW_KENNZEICHEN, AWAITING_LKW_MARKE, AWAITING_LKW_MODELL, AWAITING_LKW_BAUJAHR, AWAITING_LKW_TUEV,
                   AWAITING_PKW_KENNZEICHEN, AWAITING_PKW_MARKE, AWAITING_PKW_MODELL, AWAITING_PKW_BAUJAHR, AWAITING_PKW_TUEV,
                   AWAITING_SCHADEN_FAHRZEUG, AWAITING_SCHADEN_BESCHREIBUNG, AWAITING_SCHADEN_DATUM,
                   AWAITING_SUPERVISOR_NACHRICHT, AWAITING_TOUR_START_KM, AWAITING_TOUR_ZIEL, AWAITING_TOUR_ENDE_KM)
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
        msg = await query.message.reply_text("✅ Willkommen auf der Fahrer Plattform", reply_markup=kb.FAHRER_BEREICH_MENU)
        state.update({"state": "login_fahrer", "status_msg": msg.message_id})

    elif cmd == "login_ceo":
        await send_branding(context, cid)
        msg = await query.message.reply_text("✅ Willkommen auf der CEO Plattform", reply_markup=kb.CEO_MENU)
        state.update({"state": "ceo", "status_msg": msg.message_id})

    # ====== FAHRER BEREICH OPTIONS ======
    elif cmd == "fahrer_kalender":
        msg = await query.message.reply_text("📅 Dein Kalender", reply_markup=kb.KALENDER_MENU)
        state.update({"state": "fahrer_kalender", "status_msg": msg.message_id})

    elif cmd == "fahrer_tour":
        # Check if driver has active tour
        # This is a placeholder - in a real system, we'd identify the driver
        active_tour = None  # db.get_active_tour_for_fahrer(fahrer_id)
        
        if active_tour:
            tour_info = f"🚚 Aktive Tour:\nStart: {active_tour[1]}\nKilometerstand: {active_tour[2]} km\nZiel: {active_tour[3]}"
            msg = await query.message.reply_text(tour_info, reply_markup=kb.TOUR_MENU)
        else:
            msg = await query.message.reply_text("🛣️ Tour-Verwaltung", reply_markup=kb.TOUR_MENU)
        
        state.update({"state": "fahrer_tour", "status_msg": msg.message_id})

    elif cmd == "fahrer_supervisor":
        msg = await query.message.reply_text("🪄 Supervisor-Kontakt", reply_markup=kb.SUPERVISOR_MENU)
        state.update({"state": "fahrer_supervisor", "status_msg": msg.message_id})

    # ====== CEO MENU OPTIONS ======
    elif cmd == "büro":
        msg = await query.message.reply_text("🗂️ Büro-Bereich", reply_markup=kb.BÜRO_MENU)
        state.update({"state": "büro", "status_msg": msg.message_id})

    elif cmd == "firma":
        msg = await query.message.reply_text("🏢 Firma-Verwaltung", reply_markup=kb.FIRMA_MENU)
        state.update({"state": "firma", "status_msg": msg.message_id})

    elif cmd == "news":
        msg = await query.message.reply_text("📰 Neuigkeiten", reply_markup=kb.NEWS_MENU)
        state.update({"state": "news", "status_msg": msg.message_id})

    elif cmd == "kalender_ceo":
        msg = await query.message.reply_text("📅 CEO Kalender", reply_markup=kb.KALENDER_CEO_MENU)
        state.update({"state": "kalender_ceo", "status_msg": msg.message_id})

    # ====== FIRMA MENU OPTIONS ======
    elif cmd == "fahrer":
        msg = await query.message.reply_text("👷 Fahrer-Verwaltung", reply_markup=kb.FAHRER_MENU)
        state.update({"state": "fahrer", "status_msg": msg.message_id})

    elif cmd == "fahrzeuge":
        msg = await query.message.reply_text("🛻 Fahrzeug-Verwaltung", reply_markup=kb.FAHRZEUGE_MENU)
        state.update({"state": "fahrzeuge", "status_msg": msg.message_id})

    # ====== FAHRER MENU OPTIONS ======
    elif cmd == "übersicht":
        # Get all drivers from database
        fahrer_list = db.get_all_fahrer(only_ersatz=False)
        
        if fahrer_list:
            fahrer_text = "📋 Fahrerübersicht:\n\n"
            for f in fahrer_list:
                fahrer_text += f"🚚 {f[1]} - Tel: {f[2]}"
                if f[5]:  # is_ersatz
                    fahrer_text += " (Ersatzfahrer)"
                fahrer_text += "\n"
        else:
            fahrer_text = "📋 Fahrerübersicht: Keine Fahrer vorhanden."
            
        msg = await query.message.reply_text(fahrer_text, reply_markup=kb.ÜBERSICHT_MENU)
        state.update({"state": "übersicht", "status_msg": msg.message_id})

    elif cmd == "ersatz":
        # Get ersatz drivers from database
        ersatz_list = db.get_all_fahrer(only_ersatz=True)
        
        if ersatz_list:
            ersatz_text = "🔄 Ersatzfahrer-Übersicht:\n\n"
            for f in ersatz_list:
                ersatz_text += f"🚚 {f[1]} - Tel: {f[2]}\n"
        else:
            ersatz_text = "🔄 Ersatzfahrer-Übersicht: Keine Ersatzfahrer vorhanden."
            
        msg = await query.message.reply_text(ersatz_text, reply_markup=kb.ERSATZ_MENU)
        state.update({"state": "ersatz", "status_msg": msg.message_id})

    # ====== FAHRZEUGE MENU OPTIONS ======
    elif cmd == "lkw":
        # Get all LKWs from database
        lkw_list = db.get_all_fahrzeuge(typ="LKW")
        
        if lkw_list:
            lkw_text = "🚚 LKW-Übersicht:\n\n"
            for l in lkw_list:
                lkw_text += f"🚚 {l[1]} - {l[2]} {l[3]} ({l[4]})\n"
        else:
            lkw_text = "🚚 LKW-Übersicht: Keine LKWs vorhanden."
            
        msg = await query.message.reply_text(lkw_text, reply_markup=kb.LKW_MENU)
        state.update({"state": "lkw", "status_msg": msg.message_id})

    elif cmd == "kfz":
        # Get all PKWs from database
        pkw_list = db.get_all_fahrzeuge(typ="PKW")
        
        if pkw_list:
            pkw_text = "🚗 PKW-Übersicht:\n\n"
            for p in pkw_list:
                pkw_text += f"🚗 {p[1]} - {p[2]} {p[3]} ({p[4]})\n"
        else:
            pkw_text = "🚗 PKW-Übersicht: Keine PKWs vorhanden."
            
        msg = await query.message.reply_text(pkw_text, reply_markup=kb.KFZ_MENU)
        state.update({"state": "pkw", "status_msg": msg.message_id})

    elif cmd == "tuev":
        # Get upcoming TÜV dates
        tuev_list = db.get_tuev_upcoming(days=60)
        
        if tuev_list:
            tuev_text = "🗓 Anstehende TÜV-Termine (60 Tage):\n\n"
            for t in tuev_list:
                fahrzeug_typ = "🚚" if t[4] == "LKW" else "🚗"
                tuev_text += f"{fahrzeug_typ} {t[1]} - {t[2]} {t[3]} - TÜV: {t[5]}\n"
        else:
            tuev_text = "🗓 TÜV-Übersicht: Keine TÜV-Termine in den nächsten 60 Tagen."
            
        msg = await query.message.reply_text(tuev_text, reply_markup=kb.TUEV_MENU)
        state.update({"state": "tuev", "status_msg": msg.message_id})

    elif cmd == "schaeden":
        # Get all damages
        schaeden_list = db.get_all_schaeden()
        
        if schaeden_list:
            schaeden_text = "🔧 Schadensübersicht:\n\n"
            for s in schaeden_list:
                status_emoji = "🔴" if s[4] == "offen" else "🟡" if s[4] == "in_bearbeitung" else "🟢"
                schaeden_text += f"{status_emoji} {s[1]} - {s[2][:30]}... - {s[3]}\n"
        else:
            schaeden_text = "🔧 Schadensübersicht: Keine Schäden gemeldet."
            
        msg = await query.message.reply_text(schaeden_text, reply_markup=kb.SCHAEDEN_MENU)
        state.update({"state": "schaeden", "status_msg": msg.message_id})

    # ====== ACTION BUTTONS ======
    elif cmd == "neuer_fahrer":
        msg = await query.message.reply_text(
            "Bitte gib den Namen des neuen Fahrers ein:",
            reply_markup=kb.ZURÜCK_BUTTON
        )
        state.update({"state": "awaiting_fahrer_name", "status_msg": msg.message_id})
        return AWAITING_FAHRER_NAME

    elif cmd == "neuer_ersatzfahrer":
        msg = await query.message.reply_text(
            "Bitte gib den Namen des neuen Ersatzfahrers ein:",
            reply_markup=kb.ZURÜCK_BUTTON
        )
        state.update({"state": "awaiting_ersatzfahrer_name", "status_msg": msg.message_id, "is_ersatz": True})
        return AWAITING_FAHRER_NAME

    elif cmd == "fahrer_suchen":
        msg = await query.message.reply_text(
            "🔍 Bitte gib einen Suchbegriff ein (Name, Telefon, Email oder ID):",
            reply_markup=kb.ZURÜCK_BUTTON
        )
        state.update({"state": "awaiting_fahrer_search", "status_msg": msg.message_id})

    elif cmd == "neuer_lkw":
        msg = await query.message.reply_text(
            "Bitte gib das Kennzeichen des neuen LKW ein:",
            reply_markup=kb.ZURÜCK_BUTTON
        )
        state.update({"state": "awaiting_lkw_kennzeichen", "status_msg": msg.message_id})
        return AWAITING_LKW_KENNZEICHEN

    elif cmd == "neuer_pkw":
        msg = await query.message.reply_text(
            "Bitte gib das Kennzeichen des neuen PKW ein:",
            reply_markup=kb.ZURÜCK_BUTTON
        )
        state.update({"state": "awaiting_pkw_kennzeichen", "status_msg": msg.message_id})
        return AWAITING_PKW_KENNZEICHEN

    elif cmd == "schaden_melden":
        # Get all vehicles for selection
        fahrzeuge = db.get_all_fahrzeuge()
        
        if not fahrzeuge:
            msg = await query.message.reply_text(
                "❌ Keine Fahrzeuge vorhanden. Bitte zuerst Fahrzeuge anlegen.",
                reply_markup=kb.ZURÜCK_BUTTON
            )
            state.update({"state": "schaeden", "status_msg": msg.message_id})
        else:
            fahrzeug_list = "\n".join([f"{f[0]}: {f[1]} - {f[2]} {f[3]}" for f in fahrzeuge])
            msg = await query.message.reply_text(
                f"Bitte gib die ID des beschädigten Fahrzeugs ein:\n\n{fahrzeug_list}",
                reply_markup=kb.ZURÜCK_BUTTON
            )
            state.update({"state": "awaiting_schaden_fahrzeug", "status_msg": msg.message_id})
            return AWAITING_SCHADEN_FAHRZEUG

    elif cmd == "schadensliste":
        # Get all damages
        schaeden_list = db.get_all_schaeden()
        
        if schaeden_list:
            schaeden_text = "📋 Detaillierte Schadensliste:\n\n"
            for s in schaeden_list:
                status_emoji = "🔴" if s[4] == "offen" else "🟡" if s[4] == "in_bearbeitung" else "🟢"
                schaeden_text += f"{status_emoji} ID: {s[0]} - {s[1]}\n"
                schaeden_text += f"Beschreibung: {s[2]}\n"
                schaeden_text += f"Datum: {s[3]} - Status: {s[4]}\n\n"
        else:
            schaeden_text = "📋 Schadensliste: Keine Schäden gemeldet."
            
        msg = await query.message.reply_text(schaeden_text, reply_markup=kb.SCHAEDEN_MENU)
        state.update({"state": "schaeden", "status_msg": msg.message_id})

    elif cmd == "tour_starten":
        # This is a placeholder - in a real system, we'd identify the driver
        active_tour = None  # db.get_active_tour_for_fahrer(fahrer_id)
        
        if active_tour:
            msg = await query.message.reply_text(
                "❌ Du hast bereits eine aktive Tour!",
                reply_markup=kb.TOUR_MENU
            )
            state.update({"state": "fahrer_tour", "status_msg": msg.message_id})
        else:
            msg = await query.message.reply_text(
                "Bitte gib den aktuellen Kilometerstand ein:",
                reply_markup=kb.ZURÜCK_BUTTON
            )
            state.update({"state": "awaiting_tour_start_km", "status_msg": msg.message_id})
            return AWAITING_TOUR_START_KM

    elif cmd == "tour_beenden":
        # This is a placeholder - in a real system, we'd identify the driver
        active_tour = None  # db.get_active_tour_for_fahrer(fahrer_id)
        
        if not active_tour:
            msg = await query.message.reply_text(
                "❌ Du hast keine aktive Tour!",
                reply_markup=kb.TOUR_MENU
            )
            state.update({"state": "fahrer_tour", "status_msg": msg.message_id})
        else:
            # Store tour ID in context
            #context.chat_data[cid]["tour_id"] = active_tour[0]
            
            msg = await query.message.reply_text(
                "Bitte gib den aktuellen Kilometerstand ein:",
                reply_markup=kb.ZURÜCK_BUTTON
            )
            state.update({"state": "awaiting_tour_ende_km", "status_msg": msg.message_id})
            return AWAITING_TOUR_ENDE_KM

    elif cmd == "supervisor_nachricht":
        msg = await query.message.reply_text(
            "Bitte gib deine Nachricht an den Supervisor ein:",
            reply_markup=kb.ZURÜCK_BUTTON
        )
        state.update({"state": "awaiting_supervisor_nachricht", "status_msg": msg.message_id})
        return AWAITING_SUPERVISOR_NACHRICHT

    elif cmd == "supervisor_kontakt":
        msg = await query.message.reply_text(
            "📞 Supervisor Kontaktdaten:\n\nTelefon: +49 123 456789\nE-Mail: supervisor@kania-transport.de",
            reply_markup=kb.SUPERVISOR_MENU
        )
        state.update({"state": "fahrer_supervisor", "status_msg": msg.message_id})

    elif cmd == "kalender_übersicht":
        # This is a placeholder - in a real system, we'd show calendar entries
        heute = datetime.datetime.now().strftime("%Y-%m-%d")
        in_einem_monat = (datetime.datetime.now() + datetime.timedelta(days=30)).strftime("%Y-%m-%d")
        
        # Get calendar entries for the driver
        # calendar_entries = db.get_kalender_eintraege(heute, in_einem_monat, fahrer_id)
        
        msg = await query.message.reply_text(
            "📅 Kalenderübersicht (30 Tage):\n\nKeine Einträge vorhanden.",
            reply_markup=kb.KALENDER_MENU
        )
        state.update({"state": "fahrer_kalender", "status_msg": msg.message_id})

    elif cmd == "kalender_touren":
        # This is a placeholder - in a real system, we'd show tours
        # tours = db.get_tours_for_fahrer(fahrer_id)
        
        msg = await query.message.reply_text(
            "📝 Deine Touren:\n\nKeine Touren vorhanden.",
            reply_markup=kb.KALENDER_MENU
        )
        state.update({"state": "fahrer_kalender", "status_msg": msg.message_id})

    # ====== CONFIRM BUTTONS ======
    elif cmd == "confirm_yes":
        prev_state = state.get("state")
        
        if prev_state == "confirm_ersatz":
            name = state.get("fahrer_name", "")
            telefon = state.get("fahrer_telefon", "")
            email = state.get("fahrer_email", "")
            fahrer_id = state.get("fahrer_id_value", "")
            is_ersatz = True
            
            # Save to database
            new_id = db.add_fahrer(name, telefon, email, fahrer_id, is_ersatz)
            
            if new_id:
                success_message = f"✅ Ersatzfahrer {name} wurde erfolgreich hinzugefügt!"
            else:
                success_message = "❌ Es gab einen Fehler beim Hinzufügen des Ersatzfahrers."
                
            msg = await query.message.reply_text(success_message, reply_markup=kb.ERSATZ_MENU)
            state.update({"state": "ersatz", "status_msg": msg.message_id})
            
        elif prev_state == "confirm_fahrer":
            name = state.get("fahrer_name", "")
            telefon = state.get("fahrer_telefon", "")
            email = state.get("fahrer_email", "")
            fahrer_id = state.get("fahrer_id_value", "")
            is_ersatz = False
            
            # Save to database
            new_id = db.add_fahrer(name, telefon, email, fahrer_id, is_ersatz)
            
            if new_id:
                success_message = f"✅ Fahrer {name} wurde erfolgreich hinzugefügt!"
            else:
                success_message = "❌ Es gab einen Fehler beim Hinzufügen des Fahrers."
                
            msg = await query.message.reply_text(success_message, reply_markup=kb.ÜBERSICHT_MENU)
            state.update({"state": "übersicht", "status_msg": msg.message_id})
        
        # Add more confirmation handlers as needed

    elif cmd == "confirm_no":
        prev_state = state.get("state")
        
        if prev_state == "confirm_ersatz" or prev_state == "confirm_fahrer":
            # Return to appropriate menu
            if prev_state == "confirm_ersatz":
                msg = await query.message.reply_text("❌ Vorgang abgebrochen", reply_markup=kb.ERSATZ_MENU)
                state.update({"state": "ersatz", "status_msg": msg.message_id})
            else:
                msg = await query.message.reply_text("❌ Vorgang abgebrochen", reply_markup=kb.ÜBERSICHT_MENU)
                state.update({"state": "übersicht", "status_msg": msg.message_id})
        
        # Add more cancellation handlers as needed

    # ====== ZURÜCK BUTTON ======
    elif cmd == "zurück":
        prev = state.get("state")
        
        # Fahrer Bereich
        if prev == "fahrer_kalender" or prev == "fahrer_tour" or prev == "fahrer_supervisor":
            msg = await query.message.reply_text("✅ Willkommen auf der Fahrer Plattform", reply_markup=kb.FAHRER_BEREICH_MENU)
            state.update({"state": "login_fahrer", "status_msg": msg.message_id})
        
        # CEO Bereich
        elif prev == "büro" or prev == "firma" or prev == "news" or prev == "kalender_ceo":
            msg = await query.message.reply_text("✅ Willkommen auf der CEO Plattform", reply_markup=kb.CEO_MENU)
            state.update({"state": "ceo", "status_msg": msg.message_id})
        
        # Firma Bereich
        elif prev == "fahrer" or prev == "fahrzeuge":
            msg = await query.message.reply_text("🏢 Firma-Verwaltung", reply_markup=kb.FIRMA_MENU)
            state.update({"state": "firma", "status_msg": msg.message_id})
        
        # Fahrer Verwaltung
        elif prev == "übersicht" or prev == "ersatz":
            msg = await query.message.reply_text("👷 Fahrer-Verwaltung", reply_markup=kb.FAHRER_MENU)
            state.update({"state": "fahrer", "status_msg": msg.message_id})
        
        # Fahrzeuge Verwaltung
        elif prev == "lkw" or prev == "pkw" or prev == "tuev" or prev == "schaeden":
            msg = await query.message.reply_text("🛻 Fahrzeug-Verwaltung", reply_markup=kb.FAHRZEUGE_MENU)
            state.update({"state": "fahrzeuge", "status_msg": msg.message_id})
        
        # Root menus
        elif prev == "login_fahrer" or prev == "ceo":
            msg = await query.message.reply_text("Willkommen 👋\nBitte wähle deine Rolle:", reply_markup=kb.MAIN_MENU)
            state.update({"state": "start", "menu_msg": msg.message_id})
        
        # Form inputs (conversations)
        elif prev.startswith("awaiting_"):
            # Return to appropriate menu based on what we were awaiting
            if prev in ["awaiting_fahrer_name", "awaiting_fahrer_telefon", "awaiting_fahrer_email", "awaiting_fahrer_id", "awaiting_fahrer_search"]:
                if state.get("is_ersatz"):
                    msg = await query.message.reply_text("🔄 Ersatzfahrer-Verwaltung", reply_markup=kb.ERSATZ_MENU)
                    state.update({"state": "ersatz", "status_msg": msg.message_id})
                else:
                    msg = await query.message.reply_text("📋 Fahrerübersicht", reply_markup=kb.ÜBERSICHT_MENU)
                    state.update({"state": "übersicht", "status_msg": msg.message_id})
            
            elif prev in ["awaiting_lkw_kennzeichen", "awaiting_lkw_marke", "awaiting_lkw_modell", "awaiting_lkw_baujahr", "awaiting_lkw_tuev"]:
                msg = await query.message.reply_text("🚚 LKW-Verwaltung", reply_markup=kb.LKW_MENU)
                state.update({"state": "lkw", "status_msg": msg.message_id})
            
            elif prev in ["awaiting_pkw_kennzeichen", "awaiting_pkw_marke", "awaiting_pkw_modell", "awaiting_pkw_baujahr", "awaiting_pkw_tuev"]:
                msg = await query.message.reply_text("🚗 PKW-Verwaltung", reply_markup=kb.KFZ_MENU)
                state.update({"state": "pkw", "status_msg": msg.message_id})
            
            elif prev in ["awaiting_schaden_fahrzeug", "awaiting_schaden_beschreibung", "awaiting_schaden_datum"]:
                msg = await query.message.reply_text("🔧 Schäden-Verwaltung", reply_markup=kb.SCHAEDEN_MENU)
                state.update({"state": "schaeden", "status_msg": msg.message_id})
            
            elif prev in ["awaiting_supervisor_nachricht"]:
                msg = await query.message.reply_text("🪄 Supervisor-Kontakt", reply_markup=kb.SUPERVISOR_MENU)
                state.update({"state": "fahrer_supervisor", "status_msg": msg.message_id})
            
            elif prev in ["awaiting_tour_start_km", "awaiting_tour_ziel", "awaiting_tour_ende_km"]:
                msg = await query.message.reply_text("🛣️ Tour-Verwaltung", reply_markup=kb.TOUR_MENU)
                state.update({"state": "fahrer_tour", "status_msg": msg.message_id})
            
            else:
                # Default fallback
                msg = await query.message.reply_text("Willkommen 👋\nBitte wähle deine Rolle:", reply_markup=kb.MAIN_MENU)
                state.update({"state": "start", "menu_msg": msg.message_id})
        
        else:
            # Default fallback
            msg = await query.message.reply_text("Willkommen 👋\nBitte wähle deine Rolle:", reply_markup=kb.MAIN_MENU)
            state.update({"state": "start", "menu_msg": msg.message_id})
        
        return ConversationHandler.END

# ====== CONVERSATION HANDLERS ======

async def handle_fahrer_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle input of new driver name."""
    cid = update.effective_chat.id
    name = update.message.text
    
    # Save in context for later use
    context.chat_data[cid]["fahrer_name"] = name
    
    # Delete user's message
    await update.message.delete()
    
    # Delete previous prompt if exists
    if "status_msg" in context.chat_data[cid]:
        try:
            await context.bot.delete_message(cid, context.chat_data[cid]["status_msg"])
        except:
            pass
    
    # Ask for phone number
    msg = await update.message.reply_text(
        f"Name: {name}\nBitte gib die Telefonnummer des Fahrers ein:",
        reply_markup=kb.ZURÜCK_BUTTON
    )
    context.chat_data[cid]["status_msg"] = msg.message_id
    context.chat_data[cid]["state"] = "awaiting_fahrer_telefon"
    return AWAITING_FAHRER_TELEFON

async def handle_fahrer_telefon(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle input of new driver phone number."""
    cid = update.effective_chat.id
    telefon = update.message.text
    name = context.chat_data[cid].get("fahrer_name", "")
    
    # Save in context
    context.chat_data[cid]["fahrer_telefon"] = telefon
    
    # Delete user's message
    await update.message.delete()
    
    # Delete previous prompt
    if "status_msg" in context.chat_data[cid]:
        try:
            await context.bot.delete_message(cid, context.chat_data[cid]["status_msg"])
        except:
            pass
    
    # Ask for email
    msg = await update.message.reply_text(
        f"Name: {name}\nTelefon: {telefon}\nBitte gib die E-Mail-Adresse des Fahrers ein (optional, 'keine' für keine E-Mail):",
        reply_markup=kb.ZURÜCK_BUTTON
    )
    context.chat_data[cid]["status_msg"] = msg.message_id
    context.chat_data[cid]["state"] = "awaiting_fahrer_email"
    return AWAITING_FAHRER_EMAIL

async def handle_fahrer_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle input of new driver email."""
    cid = update.effective_chat.id
    email = update.message.text
    if email.lower() == "keine":
        email = ""
    
    name = context.chat_data[cid].get("fahrer_name", "")
    telefon = context.chat_data[cid].get("fahrer_telefon", "")
    
    # Save in context
    context.chat_data[cid]["fahrer_email"] = email
    
    # Delete user's message
    await update.message.delete()
    
    # Delete previous prompt
    if "status_msg" in context.chat_data[cid]:
        try:
            await context.bot.delete_message(cid, context.chat_data[cid]["status_msg"])
        except:
            pass
    
    # Ask for Fahrer-ID
    msg = await update.message.reply_text(
        f"Name: {name}\nTelefon: {telefon}\nE-Mail: {email if email else 'keine'}\n"
        f"Bitte gib die Fahrer-ID ein (optional, 'keine' für keine ID):",
        reply_markup=kb.ZURÜCK_BUTTON
    )
    context.chat_data[cid]["status_msg"] = msg.message_id
    context.chat_data[cid]["state"] = "awaiting_fahrer_id"
    return AWAITING_FAHRER_ID

async def handle_fahrer_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle input of new driver ID and complete the process."""
    cid = update.effective_chat.id
    fahrer_id = update.message.text
    if fahrer_id.lower() == "keine":
        fahrer_id = ""
    
    name = context.chat_data[cid].get("fahrer_name", "")
    telefon = context.chat_data[cid].get("fahrer_telefon", "")
    email = context.chat_data[cid].get("fahrer_email", "")
    
    # Delete user's message
    await update.message.delete()
    
    # Delete previous prompt
    if "status_msg" in context.chat_data[cid]:
        try:
            await context.bot.delete_message(cid, context.chat_data[cid]["status_msg"])
        except:
            pass
    
    # Ask if this is an ersatz driver
    if context.chat_data[cid].get("is_ersatz", False):
        # If this was initiated from ersatz menu, skip confirmation
        msg = await update.message.reply_text(
            f"Name: {name}\nTelefon: {telefon}\nE-Mail: {email if email else 'keine'}\n"
            f"Fahrer-ID: {fahrer_id if fahrer_id else 'keine'}\n\n"
            f"Ist diese Information korrekt?",
            reply_markup=kb.CONFIRM_KEYBOARD
        )
        context.chat_data[cid]["status_msg"] = msg.message_id
        context.chat_data[cid]["state"] = "confirm_ersatz"
    else:
        msg = await update.message.reply_text(
            f"Name: {name}\nTelefon: {telefon}\nE-Mail: {email if email else 'keine'}\n"
            f"Fahrer-ID: {fahrer_id if fahrer_id else 'keine'}\n\n"
            f"Ist diese Information korrekt?",
            reply_markup=kb.CONFIRM_KEYBOARD
        )
        context.chat_data[cid]["status_msg"] = msg.message_id
        context.chat_data[cid]["state"] = "confirm_fahrer"
    
    context.chat_data[cid]["fahrer_id_value"] = fahrer_id
    
    # We're done with the conversation handler
    return ConversationHandler.END

async def handle_lkw_kennzeichen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle input of new LKW license plate."""
    cid = update.effective_chat.id
    kennzeichen = update.message.text.upper()
    
    # Save in context
    context.chat_data[cid]["kennzeichen"] = kennzeichen
    
    # Delete user's message
    await update.message.delete()
    
    # Delete previous prompt
    if "status_msg" in context.chat_data[cid]:
        try:
            await context.bot.delete_message(cid, context.chat_data[cid]["status_msg"])
        except:
            pass
    
    # Ask for marke
    msg = await update.message.reply_text(
        f"Kennzeichen: {kennzeichen}\nBitte gib die Marke des LKW ein:",
        reply_markup=kb.ZURÜCK_BUTTON
    )
    context.chat_data[cid]["status_msg"] = msg.message_id
    context.chat_data[cid]["state"] = "awaiting_lkw_marke"
    return AWAITING_LKW_MARKE

async def handle_lkw_marke(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle input of new LKW brand."""
    cid = update.effective_chat.id
    marke = update.message.text
    kennzeichen = context.chat_data[cid].get("kennzeichen", "")
    
    # Save in context
    context.chat_data[cid]["marke"] = marke
    
    # Delete user's message
    await update.message.delete()
    
    # Delete previous prompt
    if "status_msg" in context.chat_data[cid]:
        try:
            await context.bot.delete_message(cid, context.chat_data[cid]["status_msg"])
        except:
            pass
    
    # Ask for model
    msg = await update.message.reply_text(
        f"Kennzeichen: {kennzeichen}\nMarke: {marke}\nBitte gib das Modell des LKW ein:",
        reply_markup=kb.ZURÜCK_BUTTON
    )
    context.chat_data[cid]["status_msg"] = msg.message_id
    context.chat_data[cid]["state"] = "awaiting_lkw_modell"
    return AWAITING_LKW_MODELL

async def handle_lkw_modell(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle input of new LKW model."""
    cid = update.effective_chat.id
    modell = update.message.text
    kennzeichen = context.chat_data[cid].get("kennzeichen", "")
    marke = context.chat_data[cid].get("marke", "")
    
    # Save in context
    context.chat_data[cid]["modell"] = modell
    
    # Delete user's message
    await update.message.delete()
    
    # Delete previous prompt
    if "status_msg" in context.chat_data[cid]:
        try:
            await context.bot.delete_message(cid, context.chat_data[cid]["status_msg"])
        except:
            pass
    
    # Ask for year
    msg = await update.message.reply_text(
        f"Kennzeichen: {kennzeichen}\nMarke: {marke}\nModell: {modell}\nBitte gib das Baujahr des LKW ein:",
        reply_markup=kb.ZURÜCK_BUTTON
    )
    context.chat_data[cid]["status_msg"] = msg.message_id
    context.chat_data[cid]["state"] = "awaiting_lkw_baujahr"
    return AWAITING_LKW_BAUJAHR

async def handle_lkw_baujahr(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle input of new LKW year."""
    cid = update.effective_chat.id
    try:
        baujahr = int(update.message.text)
    except ValueError:
        # Delete user's message
        await update.message.delete()
        
        # Delete previous prompt
        if "status_msg" in context.chat_data[cid]:
            try:
                await context.bot.delete_message(cid, context.chat_data[cid]["status_msg"])
            except:
                pass
        
        # Invalid input, ask again
        msg = await update.message.reply_text(
            "Ungültige Eingabe! Bitte gib das Baujahr als Zahl ein (z.B. 2018):",
            reply_markup=kb.ZURÜCK_BUTTON
        )
        context.chat_data[cid]["status_msg"] = msg.message_id
        return AWAITING_LKW_BAUJAHR
    
    kennzeichen = context.chat_data[cid].get("kennzeichen", "")
    marke = context.chat_data[cid].get("marke", "")
    modell = context.chat_data[cid].get("modell", "")
    
    # Save in context
    context.chat_data[cid]["baujahr"] = baujahr
    
    # Delete user's message
    await update.message.delete()
    
    # Delete previous prompt
    if "status_msg" in context.chat_data[cid]:
        try:
            await context.bot.delete_message(cid, context.chat_data[cid]["status_msg"])
        except:
            pass
    
    # Ask for TÜV date
    msg = await update.message.reply_text(
        f"Kennzeichen: {kennzeichen}\nMarke: {marke}\nModell: {modell}\nBaujahr: {baujahr}\n"
        f"Bitte gib das Datum der nächsten TÜV-Prüfung ein (Format: YYYY-MM-DD):",
        reply_markup=kb.ZURÜCK_BUTTON
    )
    context.chat_data[cid]["status_msg"] = msg.message_id
    context.chat_data[cid]["state"] = "awaiting_lkw_tuev"
    return AWAITING_LKW_TUEV

async def handle_lkw_tuev(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle input of new LKW TÜV date and complete the process."""
    cid = update.effective_chat.id
    tuev_datum = update.message.text
    
    # Validate date format
    try:
        datetime.datetime.strptime(tuev_datum, "%Y-%m-%d")
    except ValueError:
        # Delete user's message
        await update.message.delete()
        
        # Delete previous prompt
        if "status_msg" in context.chat_data[cid]:
            try:
                await context.bot.delete_message(cid, context.chat_data[cid]["status_msg"])
            except:
                pass
        
        # Invalid input, ask again
        msg = await update.message.reply_text(
            "Ungültiges Datumsformat! Bitte verwende das Format YYYY-MM-DD (z.B. 2023-12-31):",
            reply_markup=kb.ZURÜCK_BUTTON
        )
        context.chat_data[cid]["status_msg"] = msg.message_id
        return AWAITING_LKW_TUEV
    
    kennzeichen = context.chat_data[cid].get("kennzeichen", "")
    marke = context.chat_data[cid].get("marke", "")
    modell = context.chat_data[cid].get("modell", "")
    baujahr = context.chat_data[cid].get("baujahr", "")
    
    # Delete user's message
    await update.message.delete()
    
    # Delete previous prompt
    if "status_msg" in context.chat_data[cid]:
        try:
            await context.bot.delete_message(cid, context.chat_data[cid]["status_msg"])
        except:
            pass
    
    # Save to database
    new_id = db.add_fahrzeug(kennzeichen, marke, modell, baujahr, "LKW", tuev_datum)
    
    if new_id:
        success_message = f"✅ LKW {kennzeichen} wurde erfolgreich hinzugefügt!"
    else:
        success_message = "❌ Es gab einen Fehler beim Hinzufügen des LKW."
    
    msg = await update.message.reply_text(success_message, reply_markup=kb.LKW_MENU)
    context.chat_data[cid]["status_msg"] = msg.message_id
    context.chat_data[cid]["state"] = "lkw"
    
    return ConversationHandler.END

# Similar handlers for PKW are needed (handle_pkw_...)

async def handle_pkw_kennzeichen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle input of new PKW license plate."""
    cid = update.effective_chat.id
    kennzeichen = update.message.text.upper()
    
    # Save in context
    context.chat_data[cid]["kennzeichen"] = kennzeichen
    
    # Delete user's message
    await update.message.delete()
    
    # Delete previous prompt
    if "status_msg" in context.chat_data[cid]:
        try:
            await context.bot.delete_message(cid, context.chat_data[cid]["status_msg"])
        except:
            pass
    
    # Ask for marke
    msg = await update.message.reply_text(
        f"Kennzeichen: {kennzeichen}\nBitte gib die Marke des PKW ein:",
        reply_markup=kb.ZURÜCK_BUTTON
    )
    context.chat_data[cid]["status_msg"] = msg.message_id
    context.chat_data[cid]["state"] = "awaiting_pkw_marke"
    return AWAITING_PKW_MARKE

async def handle_pkw_marke(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle input of new PKW brand."""
    # Similar to handle_lkw_marke
    cid = update.effective_chat.id
    marke = update.message.text
    kennzeichen = context.chat_data[cid].get("kennzeichen", "")
    
    # Save in context
    context.chat_data[cid]["marke"] = marke
    
    # Delete user's message
    await update.message.delete()
    
    # Delete previous prompt
    if "status_msg" in context.chat_data[cid]:
        try:
            await context.bot.delete_message(cid, context.chat_data[cid]["status_msg"])
        except:
            pass
    
    # Ask for model
    msg = await update.message.reply_text(
        f"Kennzeichen: {kennzeichen}\nMarke: {marke}\nBitte gib das Modell des PKW ein:",
        reply_markup=kb.ZURÜCK_BUTTON
    )
    context.chat_data[cid]["status_msg"] = msg.message_id
    context.chat_data[cid]["state"] = "awaiting_pkw_modell"
    return AWAITING_PKW_MODELL

async def handle_pkw_modell(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle input of new PKW model."""
    # Similar to handle_lkw_modell
    cid = update.effective_chat.id
    modell = update.message.text
    kennzeichen = context.chat_data[cid].get("kennzeichen", "")
    marke = context.chat_data[cid].get("marke", "")
    
    # Save in context
    context.chat_data[cid]["modell"] = modell
    
    # Delete user's message
    await update.message.delete()
    
    # Delete previous prompt
    if "status_msg" in context.chat_data[cid]:
        try:
            await context.bot.delete_message(cid, context.chat_data[cid]["status_msg"])
        except:
            pass
    
    # Ask for year
    msg = await update.message.reply_text(
        f"Kennzeichen: {kennzeichen}\nMarke: {marke}\nModell: {modell}\nBitte gib das Baujahr des PKW ein:",
        reply_markup=kb.ZURÜCK_BUTTON
    )
    context.chat_data[cid]["status_msg"] = msg.message_id
    context.chat_data[cid]["state"] = "awaiting_pkw_baujahr"
    return AWAITING_PKW_BAUJAHR

async def handle_pkw_baujahr(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle input of new PKW year."""
    # Similar to handle_lkw_baujahr
    cid = update.effective_chat.id
    try:
        baujahr = int(update.message.text)
    except ValueError:
        # Delete user's message
        await update.message.delete()
        
        # Delete previous prompt
        if "status_msg" in context.chat_data[cid]:
            try:
                await context.bot.delete_message(cid, context.chat_data[cid]["status_msg"])
            except:
                pass
        
        # Invalid input, ask again
        msg = await update.message.reply_text(
            "Ungültige Eingabe! Bitte gib das Baujahr als Zahl ein (z.B. 2018):",
            reply_markup=kb.ZURÜCK_BUTTON
        )
        context.chat_data[cid]["status_msg"] = msg.message_id
        return AWAITING_PKW_BAUJAHR
    
    kennzeichen = context.chat_data[cid].get("kennzeichen", "")
    marke = context.chat_data[cid].get("marke", "")
    modell = context.chat_data[cid].get("modell", "")
    
    # Save in context
    context.chat_data[cid]["baujahr"] = baujahr
    
    # Delete user's message
    await update.message.delete()
    
    # Delete previous prompt
    if "status_msg" in context.chat_data[cid]:
        try:
            await context.bot.delete_message(cid, context.chat_data[cid]["status_msg"])
        except:
            pass
    
    # Ask for TÜV date
    msg = await update.message.reply_text(
        f"Kennzeichen: {kennzeichen}\nMarke: {marke}\nModell: {modell}\nBaujahr: {baujahr}\n"
        f"Bitte gib das Datum der nächsten TÜV-Prüfung ein (Format: YYYY-MM-DD):",
        reply_markup=kb.ZURÜCK_BUTTON
    )
    context.chat_data[cid]["status_msg"] = msg.message_id
    context.chat_data[cid]["state"] = "awaiting_pkw_tuev"
    return AWAITING_PKW_TUEV

async def handle_pkw_tuev(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle input of new PKW TÜV date and complete the process."""
    # Similar to handle_lkw_tuev
    cid = update.effective_chat.id
    tuev_datum = update.message.text
    
    # Validate date format
    try:
        datetime.datetime.strptime(tuev_datum, "%Y-%m-%d")
    except ValueError:
        # Delete user's message
        await update.message.delete()
        
        # Delete previous prompt
        if "status_msg" in context.chat_data[cid]:
            try:
                await context.bot.delete_message(cid, context.chat_data[cid]["status_msg"])
            except:
                pass
        
        # Invalid input, ask again
        msg = await update.message.reply_text(
            "Ungültiges Datumsformat! Bitte verwende das Format YYYY-MM-DD (z.B. 2023-12-31):",
            reply_markup=kb.ZURÜCK_BUTTON
        )
        context.chat_data[cid]["status_msg"] = msg.message_id
        return AWAITING_PKW_TUEV
    
    kennzeichen = context.chat_data[cid].get("kennzeichen", "")
    marke = context.chat_data[cid].get("marke", "")
    modell = context.chat_data[cid].get("modell", "")
    baujahr = context.chat_data[cid].get("baujahr", "")
    
    # Delete user's message
    await update.message.delete()
    
    # Delete previous prompt
    if "status_msg" in context.chat_data[cid]:
        try:
            await context.bot.delete_message(cid, context.chat_data[cid]["status_msg"])
        except:
            pass
    
    # Save to database
    new_id = db.add_fahrzeug(kennzeichen, marke, modell, baujahr, "PKW", tuev_datum)
    
    if new_id:
        success_message = f"✅ PKW {kennzeichen} wurde erfolgreich hinzugefügt!"
    else:
        success_message = "❌ Es gab einen Fehler beim Hinzufügen des PKW."
    
    msg = await update.message.reply_text(success_message, reply_markup=kb.KFZ_MENU)
    context.chat_data[cid]["status_msg"] = msg.message_id
    context.chat_data[cid]["state"] = "pkw"
    
    return ConversationHandler.END

# Handlers for schaden_melden
async def handle_schaden_fahrzeug(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle selection of vehicle for damage report."""
    cid = update.effective_chat.id
    try:
        fahrzeug_id = int(update.message.text)
    except ValueError:
        # Delete user's message
        await update.message.delete()
        
        # Delete previous prompt
        if "status_msg" in context.chat_data[cid]:
            try:
                await context.bot.delete_message(cid, context.chat_data[cid]["status_msg"])
            except:
                pass
        
        # Invalid input, ask again
        msg = await update.message.reply_text(
            "Ungültige Eingabe! Bitte gib die ID des Fahrzeugs ein:",
            reply_markup=kb.ZURÜCK_BUTTON
        )
        context.chat_data[cid]["status_msg"] = msg.message_id
        return AWAITING_SCHADEN_FAHRZEUG
    
    # Check if vehicle exists
    fahrzeug = db.get_fahrzeug_by_id(fahrzeug_id)
    if not fahrzeug:
        # Delete user's message
        await update.message.delete()
        
        # Delete previous prompt
        if "status_msg" in context.chat_data[cid]:
            try:
                await context.bot.delete_message(cid, context.chat_data[cid]["status_msg"])
            except:
                pass
        
        # Invalid input, ask again
        msg = await update.message.reply_text(
            "Fahrzeug nicht gefunden! Bitte gib eine gültige Fahrzeug-ID ein:",
            reply_markup=kb.ZURÜCK_BUTTON
        )
        context.chat_data[cid]["status_msg"] = msg.message_id
        return AWAITING_SCHADEN_FAHRZEUG
    
    # Save in context
    context.chat_data[cid]["schaden_fahrzeug_id"] = fahrzeug_id
    context.chat_data[cid]["schaden_fahrzeug_kennzeichen"] = fahrzeug[1]
    
    # Delete user's message
    await update.message.delete()
    
    # Delete previous prompt
    if "status_msg" in context.chat_data[cid]:
        try:
            await context.bot.delete_message(cid, context.chat_data[cid]["status_msg"])
        except:
            pass
    
    # Ask for damage description
    msg = await update.message.reply_text(
        f"Fahrzeug: {fahrzeug[1]} - {fahrzeug[2]} {fahrzeug[3]}\n"
        f"Bitte beschreibe den Schaden:",
        reply_markup=kb.ZURÜCK_BUTTON
    )
    context.chat_data[cid]["status_msg"] = msg.message_id
    context.chat_data[cid]["state"] = "awaiting_schaden_beschreibung"
    return AWAITING_SCHADEN_BESCHREIBUNG

async def handle_schaden_beschreibung(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle damage description input."""
    cid = update.effective_chat.id
    beschreibung = update.message.text
    
    # Save in context
    context.chat_data[cid]["schaden_beschreibung"] = beschreibung
    
    # Delete user's message
    await update.message.delete()
    
    # Delete previous prompt
    if "status_msg" in context.chat_data[cid]:
        try:
            await context.bot.delete_message(cid, context.chat_data[cid]["status_msg"])
        except:
            pass
    
    # Ask for date
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    msg = await update.message.reply_text(
        f"Fahrzeug: {context.chat_data[cid].get('schaden_fahrzeug_kennzeichen', '')}\n"
        f"Beschreibung: {beschreibung}\n"
        f"Bitte gib das Datum des Schadens ein (Format: YYYY-MM-DD, Standard: heute):",
        reply_markup=kb.ZURÜCK_BUTTON
    )
    context.chat_data[cid]["status_msg"] = msg.message_id
    context.chat_data[cid]["state"] = "awaiting_schaden_datum"
    return AWAITING_SCHADEN_DATUM

async def handle_schaden_datum(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle damage date input and complete the process."""
    cid = update.effective_chat.id
    datum = update.message.text
    
    # If empty, use today
    if not datum.strip():
        datum = datetime.datetime.now().strftime("%Y-%m-%d")
    else:
        # Validate date format
        try:
            datetime.datetime.strptime(datum, "%Y-%m-%d")
        except ValueError:
            # Delete user's message
            await update.message.delete()
            
            # Delete previous prompt
            if "status_msg" in context.chat_data[cid]:
                try:
                    await context.bot.delete_message(cid, context.chat_data[cid]["status_msg"])
                except:
                    pass
            
            # Invalid input, ask again
            msg = await update.message.reply_text(
                "Ungültiges Datumsformat! Bitte verwende das Format YYYY-MM-DD (z.B. 2023-12-31):",
                reply_markup=kb.ZURÜCK_BUTTON
            )
            context.chat_data[cid]["status_msg"] = msg.message_id
            return AWAITING_SCHADEN_DATUM
    
    fahrzeug_id = context.chat_data[cid].get("schaden_fahrzeug_id", "")
    beschreibung = context.chat_data[cid].get("schaden_beschreibung", "")
    
    # Delete user's message
    await update.message.delete()
    
    # Delete previous prompt
    if "status_msg" in context.chat_data[cid]:
        try:
            await context.bot.delete_message(cid, context.chat_data[cid]["status_msg"])
        except:
            pass
    
    # Save to database
    new_id = db.add_schaden(fahrzeug_id, beschreibung, datum)
    
    if new_id:
        success_message = f"✅ Schaden wurde erfolgreich gemeldet!"
    else:
        success_message = "❌ Es gab einen Fehler beim Melden des Schadens."
    
    msg = await update.message.reply_text(success_message, reply_markup=kb.SCHAEDEN_MENU)
    context.chat_data[cid]["status_msg"] = msg.message_id
    context.chat_data[cid]["state"] = "schaeden"
    
    return ConversationHandler.END

# Handlers for supervisor messages
async def handle_supervisor_nachricht(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle supervisor message input and send it."""
    cid = update.effective_chat.id
    nachricht = update.message.text
    
    # In a real system, we'd have fahrer_id associated with the user
    fahrer_id = 1  # Placeholder
    
    # Delete user's message
    await update.message.delete()
    
    # Delete previous prompt
    if "status_msg" in context.chat_data[cid]:
        try:
            await context.bot.delete_message(cid, context.chat_data[cid]["status_msg"])
        except:
            pass
    
    # Save to database
    success = db.add_nachricht(fahrer_id, nachricht)
    
    if success:
        success_message = "✅ Deine Nachricht wurde an den Supervisor gesendet!"
    else:
        success_message = "❌ Es gab einen Fehler beim Senden der Nachricht."
    
    msg = await update.message.reply_text(success_message, reply_markup=kb.SUPERVISOR_MENU)
    context.chat_data[cid]["status_msg"] = msg.message_id
    context.chat_data[cid]["state"] = "fahrer_supervisor"
    
    return ConversationHandler.END

# Handlers for tours
async def handle_tour_start_km(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle tour start km input."""
    cid = update.effective_chat.id
    try:
        start_km = int(update.message.text)
    except ValueError:
        # Delete user's message
        await update.message.delete()
        
        # Delete previous prompt
        if "status_msg" in context.chat_data[cid]:
            try:
                await context.bot.delete_message(cid, context.chat_data[cid]["status_msg"])
            except:
                pass
        
        # Invalid input, ask again
        msg = await update.message.reply_text(
            "Ungültige Eingabe! Bitte gib den Kilometerstand als Zahl ein:",
            reply_markup=kb.ZURÜCK_BUTTON
        )
        context.chat_data[cid]["status_msg"] = msg.message_id
        return AWAITING_TOUR_START_KM
    
    # Save in context
    context.chat_data[cid]["tour_start_km"] = start_km
    
    # Delete user's message
    await update.message.delete()
    
    # Delete previous prompt
    if "status_msg" in context.chat_data[cid]:
        try:
            await context.bot.delete_message(cid, context.chat_data[cid]["status_msg"])
        except:
            pass
    
    # Ask for destination
    msg = await update.message.reply_text(
        f"Kilometerstand: {start_km} km\nBitte gib das Ziel der Tour ein:",
        reply_markup=kb.ZURÜCK_BUTTON
    )
    context.chat_data[cid]["status_msg"] = msg.message_id
    context.chat_data[cid]["state"] = "awaiting_tour_ziel"
    return AWAITING_TOUR_ZIEL

async def handle_tour_ziel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle tour destination input and start the tour."""
    cid = update.effective_chat.id
    ziel = update.message.text
    start_km = context.chat_data[cid].get("tour_start_km", 0)
    
    # Save in context
    context.chat_data[cid]["tour_ziel"] = ziel
    
    # Delete user's message
    await update.message.delete()
    
    # Delete previous prompt
    if "status_msg" in context.chat_data[cid]:
        try:
            await context.bot.delete_message(cid, context.chat_data[cid]["status_msg"])
        except:
            pass
    
    # In a real system, we'd have fahrer_id associated with the user
    fahrer_id = 1  # Placeholder
    
    # Save to database
    success, result = db.start_tour(fahrer_id, start_km, ziel)
    
    if success:
        success_message = f"✅ Tour nach {ziel} wurde gestartet!"
        context.chat_data[cid]["active_tour_id"] = result
    else:
        success_message = f"❌ Fehler beim Starten der Tour: {result}"
    
    msg = await update.message.reply_text(success_message, reply_markup=kb.TOUR_MENU)
    context.chat_data[cid]["status_msg"] = msg.message_id
    context.chat_data[cid]["state"] = "fahrer_tour"
    
    return ConversationHandler.END

async def handle_tour_ende_km(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle tour end km input and complete the tour."""
    cid = update.effective_chat.id
    try:
        ende_km = int(update.message.text)
    except ValueError:
        # Delete user's message
        await update.message.delete()
        
        # Delete previous prompt
        if "status_msg" in context.chat_data[cid]:
            try:
                await context.bot.delete_message(cid, context.chat_data[cid]["status_msg"])
            except:
                pass
        
        # Invalid input, ask again
        msg = await update.message.reply_text(
            "Ungültige Eingabe! Bitte gib den Kilometerstand als Zahl ein:",
            reply_markup=kb.ZURÜCK_BUTTON
        )
        context.chat_data[cid]["status_msg"] = msg.message_id
        return AWAITING_TOUR_ENDE_KM
    
    # Delete user's message
    await update.message.delete()
    
    # Delete previous prompt
    if "status_msg" in context.chat_data[cid]:
        try:
            await context.bot.delete_message(cid, context.chat_data[cid]["status_msg"])
        except:
            pass
    
    # In a real system, we'd use the active tour ID
    tour_id = context.chat_data[cid].get("active_tour_id", 1)  # Placeholder
    
    # Save to database
    success, error = db.end_tour(tour_id, ende_km)
    
    if success:
        success_message = "✅ Tour wurde erfolgreich beendet!"
        context.chat_data[cid].pop("active_tour_id", None)
    else:
        success_message = f"❌ Fehler beim Beenden der Tour: {error}"
    
    msg = await update.message.reply_text(success_message, reply_markup=kb.TOUR_MENU)
    context.chat_data[cid]["status_msg"] = msg.message_id
    context.chat_data[cid]["state"] = "fahrer_tour"
    
    return ConversationHandler.END

async def handle_search_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle search term input for various searches."""
    cid = update.effective_chat.id
    search_term = update.message.text
    user_state = context.chat_data.get(cid, {}).get("state", "")
    
    # Delete user's message
    await update.message.delete()
    
    # Delete previous prompt
    if "status_msg" in context.chat_data[cid]:
        try:
            await context.bot.delete_message(cid, context.chat_data[cid]["status_msg"])
        except:
            pass
    
    if user_state == "awaiting_fahrer_search":
        # Search for drivers
        results = db.search_fahrer(search_term)
        
        if results:
            search_text = f"🔍 Suchergebnisse für '{search_term}':\n\n"
            for f in results:
                search_text += f"🚚 {f[1]} - Tel: {f[2]}"
                if f[3]:  # Email
                    search_text += f" - Email: {f[3]}"
                if f[4]:  # Fahrer ID
                    search_text += f" - ID: {f[4]}"
                if f[5]:  # Is ersatz
                    search_text += " (Ersatzfahrer)"
                search_text += "\n"
        else:
            search_text = f"🔍 Keine Ergebnisse für '{search_term}' gefunden."
        
        msg = await update.message.reply_text(search_text, reply_markup=kb.ÜBERSICHT_MENU)
        context.chat_data[cid]["status_msg"] = msg.message_id
        context.chat_data[cid]["state"] = "übersicht"
    
    elif user_state == "awaiting_lkw_search":
        # Search for LKWs
        results = db.search_fahrzeug(search_term, typ="LKW")
        
        if results:
            search_text = f"🔍 Suchergebnisse für '{search_term}':\n\n"
            for v in results:
                search_text += f"🚚 {v[1]} - {v[2]} {v[3]} ({v[4]})\n"
                if v[6]:  # TÜV Datum
                    search_text += f"TÜV: {v[6]}\n"
                search_text += "\n"
        else:
            search_text = f"🔍 Keine Ergebnisse für '{search_term}' gefunden."
        
        msg = await update.message.reply_text(search_text, reply_markup=kb.LKW_MENU)
        context.chat_data[cid]["status_msg"] = msg.message_id
        context.chat_data[cid]["state"] = "lkw"
    
    elif user_state == "awaiting_pkw_search":
        # Search for PKWs
        results = db.search_fahrzeug(search_term, typ="PKW")
        
        if results:
            search_text = f"🔍 Suchergebnisse für '{search_term}':\n\n"
            for v in results:
                search_text += f"🚗 {v[1]} - {v[2]} {v[3]} ({v[4]})\n"
                if v[6]:  # TÜV Datum
                    search_text += f"TÜV: {v[6]}\n"
                search_text += "\n"
        else:
            search_text = f"🔍 Keine Ergebnisse für '{search_term}' gefunden."
        
        msg = await update.message.reply_text(search_text, reply_markup=kb.KFZ_MENU)
        context.chat_data[cid]["status_msg"] = msg.message_id
        context.chat_data[cid]["state"] = "pkw"
    
    else:
        # Unknown state, return to main menu
        msg = await update.message.reply_text(
            "⚠️ Unbekannte Aktion. Zurück zum Hauptmenü.",
            reply_markup=kb.MAIN_MENU
        )
        context.chat_data[cid] = {"state": "start", "last_active": datetime.datetime.utcnow(), "menu_msg": msg.message_id}
