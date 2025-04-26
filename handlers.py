# Import handlers from separate files
from handlers_base import start, reset_user_menu, send_branding
from handlers_buttons import handle_buttons
from handlers_conversations import (
    handle_fahrer_name, handle_fahrer_telefon, handle_fahrer_email, handle_fahrer_id,
    handle_lkw_kennzeichen, handle_lkw_marke, handle_lkw_modell, handle_lkw_baujahr, handle_lkw_tuev,
    handle_pkw_kennzeichen, handle_pkw_marke, handle_pkw_modell, handle_pkw_baujahr, handle_pkw_tuev,
    handle_schaden_fahrzeug, handle_schaden_beschreibung, handle_schaden_datum,
    handle_tour_start_km, handle_tour_ziel, handle_tour_ende_km,
    handle_supervisor_nachricht,
    handle_search_input
)

# Re-export everything for easier imports elsewhere
__all__ = [
    'start', 'reset_user_menu', 'send_branding',
    'handle_buttons',
    'handle_fahrer_name', 'handle_fahrer_telefon', 'handle_fahrer_email', 'handle_fahrer_id',
    'handle_lkw_kennzeichen', 'handle_lkw_marke', 'handle_lkw_modell', 'handle_lkw_baujahr', 'handle_lkw_tuev',
    'handle_pkw_kennzeichen', 'handle_pkw_marke', 'handle_pkw_modell', 'handle_pkw_baujahr', 'handle_pkw_tuev',
    'handle_schaden_fahrzeug', 'handle_schaden_beschreibung', 'handle_schaden_datum',
    'handle_tour_start_km', 'handle_tour_ziel', 'handle_tour_ende_km',
    'handle_supervisor_nachricht',
    'handle_search_input'
]