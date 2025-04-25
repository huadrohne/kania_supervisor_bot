
    # Save to database
    new_id = db.add_fahrzeug(kennzeichen, marke, modell, baujahr, "PKW", tuev_datum)
    
    if new_id:
        success_message = f"📂 CEO → FIRMA → FAHRZEUGE → KFZ\n\n✅ PKW {kennzeichen} wurde erfolgreich hinzugefügt!"
    else:
        success_message = "📂 CEO → FIRMA → FAHRZEUGE → KFZ\n\n❌ Es gab einen Fehler beim Hinzufügen des PKW."
    
    msg = await update.message.reply_text(success_message, reply_markup=kb.KFZ_MENU)
    context.chat_data[cid]["status_msg"] = msg.message_id
    context.chat_data[cid]["state"] = "pkw"
    
    return ConversationHandler.END

# Weitere notwendige Handlers für Schäden, Tour und Supervisor
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
            "📂 CEO → FIRMA → FAHRZEUGE → SCHÄDEN → SCHADEN MELDEN\n\nUngültige Eingabe! Bitte gib die ID des Fahrzeugs ein:",
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
            "📂 CEO → FIRMA → FAHRZEUGE → SCHÄDEN → SCHADEN MELDEN\n\nFahrzeug nicht gefunden! Bitte gib eine gültige Fahrzeug-ID ein:",
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
        f"📂 CEO → FIRMA → FAHRZEUGE → SCHÄDEN → SCHADEN MELDEN\n\nFahrzeug: {fahrzeug[1]} - {fahrzeug[2]} {fahrzeug[3]}\n"
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
        f"📂 CEO → FIRMA → FAHRZEUGE → SCHÄDEN → SCHADEN MELDEN\n\nFahrzeug: {context.chat_data[cid].get('schaden_fahrzeug_kennzeichen', '')}\n"
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
                "📂 CEO → FIRMA → FAHRZEUGE → SCHÄDEN → SCHADEN MELDEN\n\nUngültiges Datumsformat! Bitte verwende das Format YYYY-MM-DD (z.B. 2023-12-31):",
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
        success_message = "📂 CEO → FIRMA → FAHRZEUGE → SCHÄDEN\n\n✅ Schaden wurde erfolgreich gemeldet!"
    else:
        success_message = "📂 CEO → FIRMA → FAHRZEUGE → SCHÄDEN\n\n❌ Es gab einen Fehler beim Melden des Schadens."
    
    msg = await update.message.reply_text(success_message, reply_markup=kb.SCHAEDEN_MENU)
    context.chat_data[cid]["status_msg"] = msg.message_id
    context.chat_data[cid]["state"] = "schaeden"
    
    return ConversationHandler.END

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
            "📂 FAHRER → TOUR → TOUR STARTEN\n\nUngültige Eingabe! Bitte gib den Kilometerstand als Zahl ein:",
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
        f"📂 FAHRER → TOUR → TOUR STARTEN\n\nKilometerstand: {start_km} km\nBitte gib das Ziel der Tour ein:",
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
        success_message = f"📂 FAHRER → TOUR\n\n✅ Tour nach {ziel} wurde gestartet!"
        context.chat_data[cid]["active_tour_id"] = result
    else:
        success_message = f"📂 FAHRER → TOUR\n\n❌ Fehler beim Starten der Tour: {result}"
    
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
            "📂 FAHRER → TOUR → TOUR BEENDEN\n\nUngültige Eingabe! Bitte gib den Kilometerstand als Zahl ein:",
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
        success_message = "📂 FAHRER → TOUR\n\n✅ Tour wurde erfolgreich beendet!"
        context.chat_data[cid].pop("active_tour_id", None)
    else:
        success_message = f"📂 FAHRER → TOUR\n\n❌ Fehler beim Beenden der Tour: {error}"
    
    msg = await update.message.reply_text(success_message, reply_markup=kb.TOUR_MENU)
    context.chat_data[cid]["status_msg"] = msg.message_id
    context.chat_data[cid]["state"] = "fahrer_tour"
    
    return ConversationHandler.END

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
        success_message = "📂 FAHRER → SUPERVISOR\n\n✅ Deine Nachricht wurde an den Supervisor gesendet!"
    else:
        success_message = "📂 FAHRER → SUPERVISOR\n\n❌ Es gab einen Fehler beim Senden der Nachricht."
    
    msg = await update.message.reply_text(success_message, reply_markup=kb.SUPERVISOR_MENU)
    context.chat_data[cid]["status_msg"] = msg.message_id
    context.chat_data[cid]["state"] = "fahrer_supervisor"
    
    return ConversationHandler.END