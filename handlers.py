Es fehlen die Handler-Funktionen in der `handlers.py` Datei. Der vorherige Code, den ich gesendet habe, wurde abgeschnitten und enthielt nur die `handle_buttons` Funktion, aber nicht die anderen Handler-Funktionen wie `handle_fahrer_name`, die in der `main.py` referenziert werden.

Hier sind die fehlenden Handler-Funktionen, die du am Ende der `handlers.py` Datei hinzufügen musst:

```python
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
    
    # Determine path based on whether it's a regular driver or ersatz driver
    if context.chat_data[cid].get("is_ersatz", False):
        path = "📂 CEO → FIRMA → FAHRER → ERSATZFAHRER → NEUER ERSATZFAHRER\n\n"
    else:
        path = "📂 CEO → FIRMA → FAHRER → ÜBERSICHT → NEUER FAHRER\n\n"
    
    # Ask for phone number
    msg = await update.message.reply_text(
        f"{path}Name: {name}\nBitte gib die Telefonnummer des Fahrers ein:",
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
    
    # Determine path based on whether it's a regular driver or ersatz driver
    if context.chat_data[cid].get("is_ersatz", False):
        path = "📂 CEO → FIRMA → FAHRER → ERSATZFAHRER → NEUER ERSATZFAHRER\n\n"
    else:
        path = "📂 CEO → FIRMA → FAHRER → ÜBERSICHT → NEUER FAHRER\n\n"
    
    # Ask for email
    msg = await update.message.reply_text(
        f"{path}Name: {name}\nTelefon: {telefon}\nBitte gib die E-Mail-Adresse des Fahrers ein (optional, 'keine' für keine E-Mail):",
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
    
    # Determine path based on whether it's a regular driver or ersatz driver
    if context.chat_data[cid].get("is_ersatz", False):
        path = "📂 CEO → FIRMA → FAHRER → ERSATZFAHRER → NEUER ERSATZFAHRER\n\n"
    else:
        path = "📂 CEO → FIRMA → FAHRER → ÜBERSICHT → NEUER FAHRER\n\n"
    
    # Ask for Fahrer-ID
    msg = await update.message.reply_text(
        f"{path}Name: {name}\nTelefon: {telefon}\nE-Mail: {email if email else 'keine'}\n"
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
    
    # Determine path based on whether it's a regular driver or ersatz driver
    if context.chat_data[cid].get("is_ersatz", False):
        path = "📂 CEO → FIRMA → FAHRER → ERSATZFAHRER → NEUER ERSATZFAHRER\n\n"
        state_val = "confirm_ersatz"
    else:
        path = "📂 CEO → FIRMA → FAHRER → ÜBERSICHT → NEUER FAHRER\n\n"
        state_val = "confirm_fahrer"
    
    # Ask for confirmation
    msg = await update.message.reply_text(
        f"{path}Name: {name}\nTelefon: {telefon}\nE-Mail: {email if email else 'keine'}\n"
        f"Fahrer-ID: {fahrer_id if fahrer_id else 'keine'}\n\n"
        f"Ist diese Information korrekt?",
        reply_markup=kb.CONFIRM_KEYBOARD
    )
    context.chat_data[cid]["status_msg"] = msg.message_id
    context.chat_data[cid]["state"] = state_val
    context.chat_data[cid]["fahrer_id_value"] = fahrer_id
    
    # We're done with the conversation handler
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
            search_text = f"📂 CEO → FIRMA → FAHRER → ÜBERSICHT → FAHRER SUCHEN\n\n🔍 Suchergebnisse für '{search_term}':\n\n"
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
            search_text = f"📂 CEO → FIRMA → FAHRER → ÜBERSICHT → FAHRER SUCHEN\n\n🔍 Keine Ergebnisse für '{search_term}' gefunden."
        
        msg = await update.message.reply_text(search_text, reply_markup=kb.ÜBERSICHT_MENU)
        context.chat_data[cid]["status_msg"] = msg.message_id
        context.chat_data[cid]["state"] = "übersicht"
    
    elif user_state == "awaiting_lkw_search":
        # Search for LKWs
        results = db.search_fahrzeug(search_term, typ="LKW")
        
        if results:
            search_text = f"📂 CEO → FIRMA → FAHRZEUGE → LKW → LKW SUCHEN\n\n🔍 Suchergebnisse für '{search_term}':\n\n"
            for v in results:
                search_text += f"🚚 {v[1]} - {v[2]} {v[3]} ({v[4]})\n"
                if v[6]:  # TÜV Datum
                    search_text += f"TÜV: {v[6]}\n"
                search_text += "\n"
        else:
            search_text = f"📂 CEO → FIRMA → FAHRZEUGE → LKW → LKW SUCHEN\n\n🔍 Keine Ergebnisse für '{search_term}' gefunden."
        
        msg = await update.message.reply_text(search_text, reply_markup=kb.LKW_MENU)
        context.chat_data[cid]["status_msg"] = msg.message_id
        context.chat_data[cid]["state"] = "lkw"
    
    elif user_state == "awaiting_pkw_search":
        # Search for PKWs
        results = db.search_fahrzeug(search_term, typ="PKW")
        
        if results:
            search_text = f"📂 CEO → FIRMA → FAHRZEUGE → KFZ → PKW SUCHEN\n\n🔍 Suchergebnisse für '{search_term}':\n\n"
            for v in results:
                search_text += f"🚗 {v[1]} - {v[2]} {v[3]} ({v[4]})\n"
                if v[6]:  # TÜV Datum
                    search_text += f"TÜV: {v[6]}\n"
                search_text += "\n"
        else:
            search_text = f"📂 CEO → FIRMA → FAHRZEUGE → KFZ → PKW SUCHEN\n\n🔍 Keine Ergebnisse für '{search_term}' gefunden."
        
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

# Diese Funktionen musst du noch implementieren
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
        f"📂 CEO → FIRMA → FAHRZEUGE → LKW → NEUER LKW\n\nKennzeichen: {kennzeichen}\nBitte gib die Marke des LKW ein:",
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
        f"📂 CEO → FIRMA → FAHRZEUGE → LKW → NEUER LKW\n\nKennzeichen: {kennzeichen}\nMarke: {marke}\nBitte gib das Modell des LKW ein:",
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
        f"📂 CEO → FIRMA → FAHRZEUGE → LKW → NEUER LKW\n\nKennzeichen: {kennzeichen}\nMarke: {marke}\nModell: {modell}\nBitte gib das Baujahr des LKW ein:",
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
            "📂 CEO → FIRMA → FAHRZEUGE → LKW → NEUER LKW\n\nUngültige Eingabe! Bitte gib das Baujahr als Zahl ein (z.B. 2018):",
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
        f"📂 CEO → FIRMA → FAHRZEUGE → LKW → NEUER LKW\n\nKennzeichen: {kennzeichen}\nMarke: {marke}\nModell: {modell}\nBaujahr: {baujahr}\n"
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
            "📂 CEO → FIRMA → FAHRZEUGE → LKW → NEUER LKW\n\nUngültiges Datumsformat! Bitte verwende das Format YYYY-MM-DD (z.B. 2023-12-31):",
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
        success_message = f"📂 CEO → FIRMA → FAHRZEUGE → LKW\n\n✅ LKW {kennzeichen} wurde erfolgreich hinzugefügt!"
    else:
        success_message = "📂 CEO → FIRMA → FAHRZEUGE → LKW\n\n❌ Es gab einen Fehler beim Hinzufügen des LKW."
    
    msg = await update.message.reply_text(success_message, reply_markup=kb.LKW_MENU)
    context.chat_data[cid]["status_msg"] = msg.message_id
    context.chat_data[cid]["state"] = "lkw"
    
    return ConversationHandler.END

# Ähnliche Funktionen für PKW implementieren
async def handle_pkw_kennzeichen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle input of new PKW license plate."""
    # Ähnlich wie handle_lkw_kennzeichen
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
        f"📂 CEO → FIRMA → FAHRZEUGE → KFZ → NEUER PKW\n\nKennzeichen: {kennzeichen}\nBitte gib die Marke des PKW ein:",
        reply_markup=kb.ZURÜCK_BUTTON
    )
    context.chat_data[cid]["status_msg"] = msg.message_id
    context.chat_data[cid]["state"] = "awaiting_pkw_marke"
    return AWAITING_PKW_MARKE

async def handle_pkw_marke(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle input of new PKW brand."""
    # Ähnlich wie handle_lkw_marke
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
        f"📂 CEO → FIRMA → FAHRZEUGE → KFZ → NEUER PKW\n\nKennzeichen: {kennzeichen}\nMarke: {marke}\nBitte gib das Modell des PKW ein:",
        reply_markup=kb.ZURÜCK_BUTTON
    )
    context.chat_data[cid]["status_msg"] = msg.message_id
    context.chat_data[cid]["state"] = "awaiting_pkw_modell"
    return AWAITING_PKW_MODELL

async def handle_pkw_modell(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle input of new PKW model."""
    # Ähnlich wie handle_lkw_modell
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
        f"📂 CEO → FIRMA → FAHRZEUGE → KFZ → NEUER PKW\n\nKennzeichen: {kennzeichen}\nMarke: {marke}\nModell: {modell}\nBitte gib das Baujahr des PKW ein:",
        reply_markup=kb.ZURÜCK_BUTTON
    )
    context.chat_data[cid]["status_msg"] = msg.message_id
    context.chat_data[cid]["state"] = "awaiting_pkw_baujahr"
    return AWAITING_PKW_BAUJAHR

async def handle_pkw_baujahr(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle input of new PKW year."""
    # Ähnlich wie handle_lkw_baujahr
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
            "📂 CEO → FIRMA → FAHRZEUGE → KFZ → NEUER PKW\n\nUngültige Eingabe! Bitte gib das Baujahr als Zahl ein (z.B. 2018):",
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
        f"📂 CEO → FIRMA → FAHRZEUGE → KFZ → NEUER PKW\n\nKennzeichen: {kennzeichen}\nMarke: {marke}\nModell: {modell}\nBaujahr: {baujahr}\n"
        f"Bitte gib das Datum der nächsten TÜV-Prüfung ein (Format: YYYY-MM-DD):",
        reply_markup=kb.ZURÜCK_BUTTON
    )
    context.chat_data[cid]["status_msg"] = msg.message_id
    context.chat_data[cid]["state"] = "awaiting_pkw_tuev"
    return AWAITING_PKW_TUEV

async def handle_pkw_tuev(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle input of new PKW TÜV date and complete the process."""
    # Ähnlich wie handle_lkw_tuev
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
            "📂 CEO → FIRMA → FAHRZEUGE → KFZ → NEUER PKW\n\nUngültiges Datumsformat! Bitte verwende das Format YYYY-MM-DD (z.B. 2023-12-31):",
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
    new​​​​​​​​​​​​​​​​