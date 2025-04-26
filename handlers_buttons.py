    elif cmd == "buero":
        msg = await query.message.reply_text("💼 BÜRO Bereich", reply_markup=kb.BUERO_MENU)
        state.update({"state": "buero", "status_msg": msg.message_id})

    elif cmd == "firma":
        msg = await query.message.reply_text("🏢 FIRMA Bereich", reply_markup=kb.FIRMA_MENU)
        state.update({"state": "firma", "status_msg": msg.message_id})

    elif cmd == "kalender_ceo":
        msg = await query.message.reply_text("📅 KALENDER CEO Bereich", reply_markup=kb.KALENDER_CEO_MENU)
        state.update({"state": "kalender_ceo", "status_msg": msg.message_id})

    elif cmd == "news":
        msg = await query.message.reply_text("📰 NEWS Bereich", reply_markup=kb.NEWS_MENU)
        state.update({"state": "news", "status_msg": msg.message_id})

    elif cmd == "support":
        msg = await query.message.reply_text("⚙️ SUPPORT Bereich", reply_markup=kb.SUPPORT_MENU)
        state.update({"state": "support", "status_msg": msg.message_id})

    # ZURÜCK-Button Bereich angepasst:
    elif cmd == "zurück":
        prev = state.get("state")

        if prev in ["login_fahrer", "ceo", "buero", "firma", "kalender_ceo", "news", "support"]:
            msg = await query.message.reply_text("✅ Willkommen auf der CEO Plattform", reply_markup=kb.CEO_MENU)
            state.update({"state": "ceo", "menu_msg": msg.message_id})
        else:
            msg = await query.message.reply_text("Willkommen 👋\nBitte wähle deine Rolle:", reply_markup=kb.MAIN_MENU)
            state.update({"state": "start", "menu_msg": msg.message_id})
        
        return ConversationHandler.END