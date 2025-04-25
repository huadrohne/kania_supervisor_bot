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
        msg = await query.message.reply_text("📂 FAHRER → KALENDER\n\n📅 Dein Kalender", reply_markup=kb.KALENDER_MENU)
        state.update({"state": "fahrer_kalender", "status_msg": msg.message_id})

    elif cmd == "fahrer_tour":
        # Check if driver has active tour
        active_tour = None  # db.get_active_tour_for_fahrer(fahrer_id)
        
        if active_tour:
            tour_info = f"📂 FAHRER → TOUR\n\n🚚 Aktive Tour:\nStart: {active_tour[1]}\nKilometerstand: {active_tour[2]} km\nZiel: {active_tour[3]}"
            msg = await query.message.reply_text(tour_info, reply_markup=kb.TOUR_MENU)
        else:
            msg = await query.message.reply_text("📂 FAHRER → TOUR\n\n🛣️ Tour-Verwaltung", reply_markup=kb.TOUR_MENU)
        
        state.update({"state": "fahrer_tour", "status_msg": msg.message_id})

    elif cmd == "fahrer_supervisor":
        msg = await query.message.reply_text("📂 FAHRER → SUPERVISOR\n\n🪄 Supervisor-Kontakt", reply_markup=kb.SUPERVISOR_MENU)
        state.update({"state": "fahrer_supervisor", "status_msg": msg.message_id})

    # ====== CEO MENU OPTIONS ======
    elif cmd == "büro":
        msg = await query.message.reply_text("📂 CEO → BÜRO\n\n🗂️ Büro-Bereich", reply_markup=kb.BÜRO_MENU)
        state.update({"state": "büro", "status_msg": msg.message_id})

    elif cmd == "firma":
        msg = await query.message.reply_text("📂 CEO → FIRMA\n\n🏢 Firma-Verwaltung", reply_markup=kb.FIRMA_MENU)
        state.update({"state": "firma", "status_msg": msg.message_id})

    elif cmd == "news":
        msg = await query.message.reply_text("📂 CEO → NEWS\n\n📰 Neuigkeiten", reply_markup=kb.NEWS_MENU)
        state.update({"state": "news", "status_msg": msg.message_id})

    elif cmd == "kalender_ceo":
        msg = await query.message.reply_text("📂 CEO → KALENDER\n\n📅 CEO Kalender", reply_markup=kb.KALENDER_CEO_MENU)
        state.update({"state": "kalender_ceo", "status_msg": msg.message_id})

    # ====== FIRMA MENU OPTIONS ======
    elif cmd == "fahrer":
        msg = await query.message.reply_text("📂 CEO → FIRMA → FAHRER\n\n👷 Fahrer-Verwaltung", reply_markup=kb.FAHRER_MENU)
        state.update({"state": "fahrer", "status_msg": msg.message_id})

    elif cmd == "fahrzeuge":
        msg = await query.message.reply_text("📂 CEO → FIRMA → FAHRZEUGE\n\n🛻 Fahrzeug-Verwaltung", reply_markup=kb.FAHRZEUGE_MENU)
        state.update({"state": "fahrzeuge", "status_msg": msg.message_id})

    # ====== FAHRER MENU OPTIONS ======
    elif cmd == "übersicht":
        # Get all drivers from database
        fahrer_list = db.get_all_fahrer(only_ersatz=False)
        
        if fahrer_list:
            fahrer_text = "📂 CEO → FIRMA → FAHRER → ÜBERSICHT\n\n📋 Fahrerübersicht:\n\n"
            for f in fahrer_list:
                fahrer_text += f"🚚 {f[1]} - Tel: {f[2]}"
                if f[5]:  # is_ersatz
                    fahrer_text += " (Ersatzfahrer)"
                fahrer_text += "\n"
        else:
            fahrer_text = "📂 CEO → FIRMA → FAHRER → ÜBERSICHT\n\n📋 Fahrerübersicht: Keine Fahrer vorhanden."
            
        msg = await query.message.reply_text(fahrer_text, reply_markup=kb.ÜBERSICHT_MENU)
        state.update({"state": "übersicht", "status_msg": msg.message_id})

    elif cmd == "ersatz":
        # Get ersatz drivers from database
        ersatz_list = db.get_all_fahrer(only_ersatz=True)
        
        if ersatz_list:
            ersatz_text = "📂 CEO → FIRMA → FAHRER → ERSATZFAHRER\n\n🔄 Ersatzfahrer-Übersicht:\n\n"
            for f in ersatz_list:
                ersatz_text += f"🚚 {f[1]} - Tel: {f[2]}\n"
        else:
            ersatz_text = "📂 CEO → FIRMA → FAHRER → ERSATZFAHRER\n\n🔄 Ersatzfahrer-Übersicht: Keine Ersatzfahrer vorhanden."
            
        msg = await query.message.reply_text(ersatz_text, reply_markup=kb.ERSATZ_MENU)
        state.update({"state": "ersatz", "status_msg": msg.message_id})

    # ====== FAHRZEUGE MENU OPTIONS ======
    elif cmd == "lkw":
        # Get all LKWs from database
        lkw_list = db.get_all_fahrzeuge(typ="LKW")
        
        if lkw_list:
            lkw_text = "📂 CEO → FIRMA → FAHRZEUGE → LKW\n\n🚚 LKW-Übersicht:\n\n"
            for l in lkw_list:
                lkw_text += f"🚚 {l[1]} - {l[2]} {l[3]} ({l[4]})\n"
        else:
            lkw_text = "📂 CEO → FIRMA → FAHRZEUGE → LKW\n\n🚚 LKW-Übersicht: Keine LKWs vorhanden."
            
        msg = await query.message.reply_text(lkw_text, reply_markup=kb.LKW_MENU)
        state.update({"state": "lkw", "status_msg": msg.message_id})

    elif cmd == "kfz":
        # Get all PKWs from database
        pkw_list = db.get_all_fahrzeuge(typ="PKW")
        
        if pkw_list:
            pkw_text = "📂 CEO → FIRMA → FAHRZEUGE → KFZ\n\n🚗 PKW-Übersicht:\n\n"
            for p in pkw_list:
                pkw_text += f"🚗 {p[1]} - {p[2]} {p[3]} ({p[4]})\n"
        else:
            pkw_text = "📂 CEO → FIRMA → FAHRZEUGE → KFZ\n\n🚗 PKW-Übersicht: Keine PKWs vorhanden."
            
        msg = await query.message.reply_text(pkw_text, reply_markup=kb.KFZ_MENU)
        state.update({"state": "pkw", "status_msg": msg.message_id})

    elif cmd == "tuev":
        # Get upcoming TÜV dates
        tuev_list = db.get_tuev_upcoming(days=60)
        
        if tuev_list:
            tuev_text = "📂 CEO → FIRMA → FAHRZEUGE → TÜV\n\n🗓 Anstehende TÜV-Termine (60 Tage):\n\n"
            for t in tuev_list:
                fahrzeug_typ = "🚚" if t[4] == "LKW" else "🚗"
                tuev_text += f"{fahrzeug_typ} {t[1]} - {t[2]} {t[3]} - TÜV: {t[5]}\n"
        else:
            tuev_text = "📂 CEO → FIRMA → FAHRZEUGE → TÜV\n\n🗓 TÜV-Übersicht: Keine TÜV-Termine in den nächsten 60 Tagen."
            
        msg = await query.message.reply_text(tuev_text, reply_markup=kb.TUEV_MENU)
        state.update({"state": "tuev", "status_msg": msg.message_id})

    elif cmd == "schaeden":
        # Get all damages
        schaeden_list = db.get_all_schaeden()
        
        if schaeden_list:
            schaeden_text = "📂 CEO → FIRMA → FAHRZEUGE → SCHÄDEN\n\n🔧 Schadensübersicht:\n\n"
            for s in schaeden_list:
                status_emoji = "🔴" if s[4] == "offen" else "🟡" if s[4] == "in_bearbeitung" else "🟢"
                schaeden_text += f"{status_emoji} {s[1]} - {s[2][:30]}... - {s[3]}\n"
        else:
            schaeden_text = "📂 CEO → FIRMA → FAHRZEUGE → SCHÄDEN\n\n🔧 Schadensübersicht: Keine Schäden gemeldet."
            
        msg = await query.message.reply_text(schaeden_text, reply_markup=kb.SCHAEDEN_MENU)
        state.update({"state": "schaeden", "status_msg": msg.message_id})

    # ====== ACTION BUTTONS ======
    elif cmd == "neuer_fahrer":
        msg = await query.message.reply_text(
            "📂 CEO → FIRMA → FAHRER → ÜBERSICHT → NEUER FAHRER\n\nBitte gib den Namen des neuen Fahrers ein:",
            reply_markup=kb.ZURÜCK_BUTTON
        )
        state.update({"state": "awaiting_fahrer_name", "status_msg": msg.message_id})
        return AWAITING_FAHRER_NAME

    elif cmd == "neuer_ersatzfahrer":
        msg = await query.message.reply_text(
            "📂 CEO → FIRMA → FAHRER → ERSATZFAHRER → NEUER ERSATZFAHRER\n\nBitte gib den Namen des neuen Ersatzfahrers ein:",
            reply_markup=kb.ZURÜCK_BUTTON
        )
        state.update({"state": "awaiting_ersatzfahrer_name", "status_msg": msg.message_id, "is_ersatz": True})
        return AWAITING_FAHRER_NAME

    elif cmd == "fahrer_suchen":
        msg = await query.message.reply_text(
            "📂 CEO → FIRMA → FAHRER → ÜBERSICHT → FAHRER SUCHEN\n\n🔍 Bitte gib einen Suchbegriff ein (Name, Telefon, Email oder ID):",
            reply_markup=kb.ZURÜCK_BUTTON
        )
        state.update({"state": "awaiting_fahrer_search", "status_msg": msg.message_id})

    elif cmd == "neuer_lkw":
        msg = await query.message.reply_text(
            "📂 CEO → FIRMA → FAHRZEUGE → LKW → NEUER LKW\n\nBitte gib das Kennzeichen des neuen LKW ein:",
            reply_markup=kb.ZURÜCK_BUTTON
        )
        state.update({"state": "awaiting_lkw_kennzeichen", "status_msg": msg.message_id})
        return AWAITING_LKW_KENNZEICHEN

    elif cmd == "neuer_pkw":
        msg = await query.message.reply_text(
            "📂 CEO → FIRMA → FAHRZEUGE → KFZ → NEUER PKW\n\nBitte gib das Kennzeichen des neuen PKW ein:",
            reply_markup=kb.ZURÜCK_BUTTON
        )
        state.update({"state": "awaiting_pkw_kennzeichen", "status_msg": msg.message_id})
        return AWAITING_PKW_KENNZEICHEN

    elif cmd == "schaden_melden":
        # Get all vehicles for selection
        fahrzeuge = db.get_all_fahrzeuge()
        
        if not fahrzeuge:
            msg = await query.message.reply_text(
                "📂 CEO → FIRMA → FAHRZEUGE → SCHÄDEN → SCHADEN MELDEN\n\n❌ Keine Fahrzeuge vorhanden. Bitte zuerst Fahrzeuge anlegen.",
                reply_markup=kb.ZURÜCK_BUTTON
            )
            state.update({"state": "schaeden", "status_msg": msg.message_id})
        else:
            fahrzeug_list = "\n".join([f"{f[0]}: {f[1]} - {f[2]} {f[3]}" for f in fahrzeuge])
            msg = await query.message.reply_text(
                f"📂 CEO → FIRMA → FAHRZEUGE → SCHÄDEN → SCHADEN MELDEN\n\nBitte gib die ID des beschädigten Fahrzeugs ein:\n\n{fahrzeug_list}",
                reply_markup=kb.ZURÜCK_BUTTON
            )
            state.update({"state": "awaiting_schaden_fahrzeug", "status_msg": msg.message_id})
            return AWAITING_SCHADEN_FAHRZEUG

    elif cmd == "schadensliste":
        # Get all damages
        schaeden_list = db.get_all_schaeden()
        
        if schaeden_list:
            schaeden_text = "📂 CEO → FIRMA → FAHRZEUGE → SCHÄDEN → SCHADENSLISTE\n\n📋 Detaillierte Schadensliste:\n\n"
            for s in schaeden_list:
                status_emoji = "🔴" if s[4] == "offen" else "🟡" if s[4] == "in_bearbeitung" else "🟢"
                schaeden_text += f"{status_emoji} ID: {s[0]} - {s[1]}\n"
                schaeden_text += f"Beschreibung: {s[2]}\n"
                schaeden_text += f"Datum: {s[3]} - Status: {s[4]}\n\n"
        else:
            schaeden_text = "📂 CEO → FIRMA → FAHRZEUGE → SCHÄDEN → SCHADENSLISTE\n\n📋 Schadensliste: Keine Schäden gemeldet."
            
        msg = await query.message.reply_text(schaeden_text, reply_markup=kb.SCHAEDEN_MENU)
        state.update({"state": "schaeden", "status_msg": msg.message_id})

    elif cmd == "tour_starten":
        # This is a placeholder - in a real system, we'd identify the driver
        active_tour = None  # db.get_active_tour_for_fahrer(fahrer_id)
        
        if active_tour:
            msg = await query.message.reply_text(
                "📂 FAHRER → TOUR → TOUR STARTEN\n\n❌ Du hast bereits eine aktive Tour!",
                reply_markup=kb.TOUR_MENU
            )
            state.update({"state": "fahrer_tour", "status_msg": msg.message_id})
        else:
            msg = await query.message.reply_text(
                "📂 FAHRER → TOUR → TOUR STARTEN\n\nBitte gib den aktuellen Kilometerstand ein:",
                reply_markup=kb.ZURÜCK_BUTTON
            )
            state.update({"state": "awaiting_tour_start_km", "status_msg": msg.message_id})
            return AWAITING_TOUR_START_KM

    elif cmd == "tour_beenden":
        # This is a placeholder - in a real system, we'd identify the driver
        active_tour = None  # db.get_active_tour_for_fahrer(fahrer_id)
        
        if not active_tour:
            msg = await query.message.reply_text(
                "📂 FAHRER → TOUR → TOUR BEENDEN\n\n❌ Du hast keine aktive Tour!",
                reply_markup=kb.TOUR_MENU
            )
            state.update({"state": "fahrer_tour", "status_msg": msg.message_id})
        else:
            # Store tour ID in context
            #context.chat_data[cid]["tour_id"] = active_tour[0]
            
            msg = await query.message.reply_text(
                "📂 FAHRER → TOUR → TOUR BEENDEN\n\nBitte gib den aktuellen Kilometerstand ein:",
                reply_markup=kb.ZURÜCK_BUTTON
            )
            state.update({"state": "awaiting_tour_ende_km", "status_msg": msg.message_id})
            return AWAITING_TOUR_ENDE_KM

    elif cmd == "supervisor_nachricht":
        msg = await query.message.reply_text(
            "📂 FAHRER → SUPERVISOR → NACHRICHT\n\nBitte gib deine Nachricht an den Supervisor ein:",
            reply_markup=kb.ZURÜCK_BUTTON
        )
        state.update({"state": "awaiting_supervisor_nachricht", "status_msg": msg.message_id})
        return AWAITING_SUPERVISOR_NACHRICHT

    elif cmd == "supervisor_kontakt":
        msg = await query.message.reply_text(
            "📂 FAHRER → SUPERVISOR → KONTAKT\n\n📞 Supervisor Kontaktdaten:\n\nTelefon: +49 123 456789\nE-Mail: supervisor@kania-transport.de",
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
            "📂 FAHRER → KALENDER → ÜBERSICHT\n\n📅 Kalenderübersicht (30 Tage):\n\nKeine Einträge vorhanden.",
            reply_markup=kb.KALENDER_MENU
        )
        state.update({"state": "fahrer_kalender", "status_msg": msg.message_id})

    elif cmd == "kalender_touren":
        # This is a placeholder - in a real system, we'd show tours
        # tours = db.get_tours_for_fahrer(fahrer_id)
        
        msg = await query.message.reply_text(
            "📂 FAHRER → KALENDER → MEINE TOUREN\n\n📝 Deine Touren:\n\nKeine Touren vorhanden.",
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
                success_message = f"📂 CEO → FIRMA → FAHRER → ERSATZFAHRER\n\n✅ Ersatzfahrer {name} wurde erfolgreich hinzugefügt!"
            else:
                success_message = "📂 CEO → FIRMA → FAHRER → ERSATZFAHRER\n\n❌ Es gab einen Fehler beim Hinzufügen des Ersatzfahrers."
                
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
                success_message = f"📂 CEO → FIRMA → FAHRER → ÜBERSICHT\n\n✅ Fahrer {name} wurde erfolgreich hinzugefügt!"
            else:
                success_message = "📂 CEO → FIRMA → FAHRER → ÜBERSICHT\n\n❌ Es gab einen Fehler beim Hinzufügen des Fahrers."
                
            msg = await query.message.reply_text(success_message, reply_markup=kb.ÜBERSICHT_MENU)
            state.update({"state": "übersicht", "status_msg": msg.message_id})
        
        # Add more confirmation handlers as needed

    elif cmd == "confirm_no":
        prev_state = state.get("state")
        
        if prev_state == "confirm_ersatz" or prev_state == "confirm_fahrer":
            # Return to appropriate menu
            if prev_state == "confirm_ersatz":
                msg = await query.message.reply_text("📂 CEO → FIRMA → FAHRER → ERSATZFAHRER\n\n❌ Vorgang abgebrochen", reply_markup=kb.ERSATZ_MENU)
                state.update({"state": "ersatz", "status_msg": msg.message_id})
            else:
                msg = await query.message.reply_text("📂 CEO → FIRMA → FAHRER → ÜBERSICHT\n\n❌ Vorgang abgebrochen", reply_markup=kb.ÜBERSICHT_MENU)
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
            msg = await query.message.reply_text("📂 CEO → FIRMA\n\n🏢 Firma-Verwaltung", reply_markup=kb.FIRMA_MENU)
            state.update({"state": "firma", "status_msg": msg.message_id})
        
        # Fahrer Verwaltung
        elif prev == "übersicht" or prev == "ersatz":
            msg = await query.message.reply_text("📂 CEO → FIRMA → FAHRER\n\n👷 Fahrer-Verwaltung", reply_markup=kb.FAHRER_MENU)
            state.update({"state": "fahrer", "status_msg": msg.message_id})
        
        # Fahrzeuge Verwaltung
        elif prev == "lkw" or prev == "pkw" or prev == "tuev" or prev == "schaeden":
            msg = await query.message.reply_text("📂 CEO → FIRMA → FAHRZEUGE\n\n🛻 Fahrzeug-Verwaltung", reply_markup=kb.FAHRZEUGE_MENU)
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
                    msg = await query.message.reply_text("📂 CEO → FIRMA → FAHRER → ERSATZFAHRER\n\n🔄 Ersatzfahrer-Verwaltung", reply_markup=kb.ERSATZ_MENU)
                    state.update({"state": "ersatz", "status_msg": msg.message_id})
                else:
                    msg = await query.message.reply_text("📂 CEO → FIRMA → FAHRER → ÜBERSICHT\n\n📋 Fahrerübersicht", reply_markup=kb.ÜBERSICHT_MENU)
                    state.update({"state": "übersicht", "status_msg": msg.message_id})
            
            elif prev in ["awaiting_lkw_kennzeichen", "awaiting_lkw_marke", "awaiting_lkw_modell", "awaiting_lkw_baujahr", "awaiting_lkw_tuev"]:
                msg = await query.message.reply_text("📂 CEO → FIRMA → FAHRZEUGE → LKW\n\n🚚 LKW-Verwaltung", reply_markup=kb.LKW_MENU)
                state.update({"state": "lkw", "status_msg": msg.message_id})
            
            elif prev in ["awaiting_pkw_kennzeichen", "awaiting_pkw_marke", "awaiting_pkw_modell", "awaiting_pkw_baujahr", "awaiting_pkw_tuev"]:
                msg = await query.message.reply_text("📂 CEO → FIRMA → FAHRZEUGE → KFZ\n\n🚗 PKW-Verwaltung", reply_markup=kb.KFZ_MENU)
                state.update({"state": "pkw", "status_msg": msg.message_id})
            
            elif prev in ["awaiting_schaden_fahrzeug", "awaiting_schaden_beschreibung", "awaiting_schaden_datum"]:
                msg = await query.message.reply_text("📂 CEO → FIRMA → FAHRZEUGE → SCHÄDEN\n\n🔧 Schäden-Verwaltung", reply_markup=kb.SCHAEDEN_MENU)
                state.update({"state": "schaeden", "status_msg": msg.message_id})
            
            elif prev in ["awaiting_supervisor_nachricht"]:
                msg = await query.message.reply_text("📂 FAHRER → SUPERVISOR\n\n🪄 Supervisor-Kontakt", reply_markup=kb.SUPERVISOR_MENU)
                state.update({"state": "fahrer_supervisor", "status_msg": msg.message_id})
            
            elif prev in ["awaiting_tour_start_km", "awaiting_tour_ziel", "awaiting_tour_ende_km"]:
                msg = await query.message.reply_text("📂 FAHRER → TOUR\n\n🛣️ Tour-Verwaltung", reply_markup=kb.TOUR_MENU)
                state.update({"state": "fahrer

              elif prev in ["awaiting_tour_start_km", "awaiting_tour_ziel", "awaiting_tour_ende_km"]:
                msg = await query.message.reply_text("📂 FAHRER → TOUR\n\n🛣️ Tour-Verwaltung", reply_markup=kb.TOUR_MENU)
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
