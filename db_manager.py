import sqlite3
import logging
from config import DATABASE_PATH
from datetime import datetime

class DatabaseManager:
    def __init__(self):
        """Initialize the database connection and create tables if they don't exist."""
        self.connection = None
        self.cursor = None
        self.setup_database()

    def setup_database(self):
        """Set up the database connection and create necessary tables."""
        try:
            self.connection = sqlite3.connect(DATABASE_PATH)
            self.cursor = self.connection.cursor()
            
            # Create fahrer table
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS fahrer (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                telefon TEXT NOT NULL,
                email TEXT,
                fahrer_id TEXT UNIQUE,
                is_ersatz BOOLEAN DEFAULT FALSE,
                active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            
            # Create fahrzeuge table
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS fahrzeuge (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                kennzeichen TEXT NOT NULL UNIQUE,
                marke TEXT NOT NULL,
                modell TEXT NOT NULL,
                baujahr INTEGER,
                typ TEXT CHECK(typ IN ('LKW', 'PKW')),
                tuev_datum DATE,
                active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            
            # Create schaeden table
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS schaeden (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fahrzeug_id INTEGER NOT NULL,
                beschreibung TEXT NOT NULL,
                datum DATE NOT NULL,
                status TEXT DEFAULT 'offen' CHECK(status IN ('offen', 'in_bearbeitung', 'erledigt')),
                bild_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (fahrzeug_id) REFERENCES fahrzeuge (id)
            )
            ''')
            
            # Create touren table
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS touren (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fahrer_id INTEGER NOT NULL,
                start_datum TIMESTAMP NOT NULL,
                ende_datum TIMESTAMP,
                start_km INTEGER NOT NULL,
                ende_km INTEGER,
                ziel TEXT NOT NULL,
                status TEXT DEFAULT 'aktiv' CHECK(status IN ('aktiv', 'beendet')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (fahrer_id) REFERENCES fahrer (id)
            )
            ''')
            
            # Create nachrichten table
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS nachrichten (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                absender_id INTEGER NOT NULL,
                nachricht TEXT NOT NULL,
                gelesen BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (absender_id) REFERENCES fahrer (id)
            )
            ''')
            
            # Create kalender table
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS kalender (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titel TEXT NOT NULL,
                beschreibung TEXT,
                datum DATE NOT NULL,
                fahrer_id INTEGER,
                ziel TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (fahrer_id) REFERENCES fahrer (id)
            )
            ''')
            
            self.connection.commit()
            logging.info("Database setup complete")
        except sqlite3.Error as e:
            logging.error(f"Database error: {e}")
            if self.connection:
                self.connection.close()
            raise

    def close(self):
        """Close the database connection."""
        if self.connection:
            self.connection.close()

    # Fahrer-related methods
    def add_fahrer(self, name, telefon, email="", fahrer_id="", is_ersatz=False):
        """Add a new fahrer to the database."""
        try:
            self.cursor.execute(
                "INSERT INTO fahrer (name, telefon, email, fahrer_id, is_ersatz) VALUES (?, ?, ?, ?, ?)",
                (name, telefon, email, fahrer_id, is_ersatz)
            )
            self.connection.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            logging.error(f"Error adding fahrer: {e}")
            return None

    def get_all_fahrer(self, only_active=True, only_ersatz=False):
        """Get all fahrer from the database."""
        try:
            query = "SELECT id, name, telefon, email, fahrer_id, is_ersatz FROM fahrer WHERE 1=1"
            if only_active:
                query += " AND active = 1"
            if only_ersatz:
                query += " AND is_ersatz = 1"
            
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            logging.error(f"Error getting fahrer: {e}")
            return []

    def get_fahrer_by_id(self, fahrer_id):
        """Get a fahrer by their ID."""
        try:
            self.cursor.execute(
                "SELECT id, name, telefon, email, fahrer_id, is_ersatz FROM fahrer WHERE id = ?",
                (fahrer_id,)
            )
            return self.cursor.fetchone()
        except sqlite3.Error as e:
            logging.error(f"Error getting fahrer by ID: {e}")
            return None

    def update_fahrer(self, fahrer_id, name=None, telefon=None, email=None, fahrer_id_new=None, is_ersatz=None, active=None):
        """Update a fahrer in the database."""
        try:
            update_parts = []
            values = []
            
            if name is not None:
                update_parts.append("name = ?")
                values.append(name)
            if telefon is not None:
                update_parts.append("telefon = ?")
                values.append(telefon)
            if email is not None:
                update_parts.append("email = ?")
                values.append(email)
            if fahrer_id_new is not None:
                update_parts.append("fahrer_id = ?")
                values.append(fahrer_id_new)
            if is_ersatz is not None:
                update_parts.append("is_ersatz = ?")
                values.append(is_ersatz)
            if active is not None:
                update_parts.append("active = ?")
                values.append(active)
                
            if not update_parts:
                return False
                
            values.append(fahrer_id)
            query = f"UPDATE fahrer SET {', '.join(update_parts)} WHERE id = ?"
            
            self.cursor.execute(query, values)
            self.connection.commit()
            return self.cursor.rowcount > 0
        except sqlite3.Error as e:
            logging.error(f"Error updating fahrer: {e}")
            return False

    def delete_fahrer(self, fahrer_id):
        """Delete a fahrer from the database (set active to false)."""
        try:
            self.cursor.execute(
                "UPDATE fahrer SET active = 0 WHERE id = ?",
                (fahrer_id,)
            )
            self.connection.commit()
            return self.cursor.rowcount > 0
        except sqlite3.Error as e:
            logging.error(f"Error deleting fahrer: {e}")
            return False

    def search_fahrer(self, search_term):
        """Search for fahrer by name, telefon, email, or fahrer_id."""
        try:
            search_term = f"%{search_term}%"
            self.cursor.execute(
                """SELECT id, name, telefon, email, fahrer_id, is_ersatz 
                FROM fahrer 
                WHERE (name LIKE ? OR telefon LIKE ? OR email LIKE ? OR fahrer_id LIKE ?) AND active = 1""",
                (search_term, search_term, search_term, search_term)
            )
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            logging.error(f"Error searching fahrer: {e}")
            return []

    # Fahrzeuge-related methods
    def add_fahrzeug(self, kennzeichen, marke, modell, baujahr, typ, tuev_datum=None):
        """Add a new fahrzeug to the database."""
        try:
            self.cursor.execute(
                "INSERT INTO fahrzeuge (kennzeichen, marke, modell, baujahr, typ, tuev_datum) VALUES (?, ?, ?, ?, ?, ?)",
                (kennzeichen, marke, modell, baujahr, typ, tuev_datum)
            )
            self.connection.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            logging.error(f"Error adding fahrzeug: {e}")
            return None

    def get_all_fahrzeuge(self, only_active=True, typ=None):
        """Get all fahrzeuge from the database."""
        try:
            query = "SELECT id, kennzeichen, marke, modell, baujahr, typ, tuev_datum FROM fahrzeuge WHERE 1=1"
            params = []
            
            if only_active:
                query += " AND active = 1"
            if typ:
                query += " AND typ = ?"
                params.append(typ)
            
            self.cursor.execute(query, params)
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            logging.error(f"Error getting fahrzeuge: {e}")
            return []

    def get_fahrzeug_by_id(self, fahrzeug_id):
        """Get a fahrzeug by ID."""
        try:
            self.cursor.execute(
                "SELECT id, kennzeichen, marke, modell, baujahr, typ, tuev_datum FROM fahrzeuge WHERE id = ?",
                (fahrzeug_id,)
            )
            return self.cursor.fetchone()
        except sqlite3.Error as e:
            logging.error(f"Error getting fahrzeug by ID: {e}")
            return None

    def get_fahrzeug_by_kennzeichen(self, kennzeichen):
        """Get a fahrzeug by kennzeichen."""
        try:
            self.cursor.execute(
                "SELECT id, kennzeichen, marke, modell, baujahr, typ, tuev_datum FROM fahrzeuge WHERE kennzeichen = ?",
                (kennzeichen,)
            )
            return self.cursor.fetchone()
        except sqlite3.Error as e:
            logging.error(f"Error getting fahrzeug by kennzeichen: {e}")
            return None

    def update_fahrzeug(self, fahrzeug_id, kennzeichen=None, marke=None, modell=None, baujahr=None, tuev_datum=None, active=None):
        """Update a fahrzeug in the database."""
        try:
            update_parts = []
            values = []
            
            if kennzeichen is not None:
                update_parts.append("kennzeichen = ?")
                values.append(kennzeichen)
            if marke is not None:
                update_parts.append("marke = ?")
                values.append(marke)
            if modell is not None:
                update_parts.append("modell = ?")
                values.append(modell)
            if baujahr is not None:
                update_parts.append("baujahr = ?")
                values.append(baujahr)
            if tuev_datum is not None:
                update_parts.append("tuev_datum = ?")
                values.append(tuev_datum)
            if active is not None:
                update_parts.append("active = ?")
                values.append(active)
                
            if not update_parts:
                return False
                
            values.append(fahrzeug_id)
            query = f"UPDATE fahrzeuge SET {', '.join(update_parts)} WHERE id = ?"
            
            self.cursor.execute(query, values)
            self.connection.commit()
            return self.cursor.rowcount > 0
        except sqlite3.Error as e:
            logging.error(f"Error updating fahrzeug: {e}")
            return False

    def delete_fahrzeug(self, fahrzeug_id):
        """Delete a fahrzeug from the database (set active to false)."""
        try:
            self.cursor.execute(
                "UPDATE fahrzeuge SET active = 0 WHERE id = ?",
                (fahrzeug_id,)
            )
            self.connection.commit()
            return self.cursor.rowcount > 0
        except sqlite3.Error as e:
            logging.error(f"Error deleting fahrzeug: {e}")
            return False

    def search_fahrzeug(self, search_term, typ=None):
        """Search for fahrzeug by kennzeichen, marke, or modell."""
        try:
            search_term = f"%{search_term}%"
            query = """SELECT id, kennzeichen, marke, modell, baujahr, typ, tuev_datum 
                    FROM fahrzeuge 
                    WHERE (kennzeichen LIKE ? OR marke LIKE ? OR modell LIKE ?) AND active = 1"""
            params = [search_term, search_term, search_term]
            
            if typ:
                query += " AND typ = ?"
                params.append(typ)
                
            self.cursor.execute(query, params)
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            logging.error(f"Error searching fahrzeug: {e}")
            return []

    def get_tuev_upcoming(self, days=30):
        """Get all vehicles with TÜV dates in the next X days."""
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            future_date = datetime.now().replace(day=datetime.now().day + days).strftime("%Y-%m-%d")
            
            self.cursor.execute(
                """SELECT id, kennzeichen, marke, modell, typ, tuev_datum 
                FROM fahrzeuge 
                WHERE tuev_datum BETWEEN ? AND ? AND active = 1
                ORDER BY tuev_datum""",
                (today, future_date)
            )
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            logging.error(f"Error getting upcoming TÜV: {e}")
            return []

    # Schäden-related methods
    def add_schaden(self, fahrzeug_id, beschreibung, datum, bild_path=None, status="offen"):
        """Add a new schaden to the database."""
        try:
            self.cursor.execute(
                "INSERT INTO schaeden (fahrzeug_id, beschreibung, datum, bild_path, status) VALUES (?, ?, ?, ?, ?)",
                (fahrzeug_id, beschreibung, datum, bild_path, status)
            )
            self.connection.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            logging.error(f"Error adding schaden: {e}")
            return None

    def get_all_schaeden(self, status=None):
        """Get all schaeden from the database."""
        try:
            query = """SELECT s.id, f.kennzeichen, s.beschreibung, s.datum, s.status
                    FROM schaeden s
                    JOIN fahrzeuge f ON s.fahrzeug_id = f.id
                    WHERE 1=1"""
            params = []
            
            if status:
                query += " AND s.status = ?"
                params.append(status)
                
            query += " ORDER BY s.datum DESC"
            
            self.cursor.execute(query, params)
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            logging.error(f"Error getting schaeden: {e}")
            return []

    def get_schaeden_by_fahrzeug(self, fahrzeug_id, status=None):
        """Get all schaeden for a specific fahrzeug."""
        try:
            query = """SELECT s.id, s.beschreibung, s.datum, s.status, s.bild_path
                    FROM schaeden s
                    WHERE s.fahrzeug_id = ?"""
            params = [fahrzeug_id]
            
            if status:
                query += " AND s.status = ?"
                params.append(status)
                
            query += " ORDER BY s.datum DESC"
            
            self.cursor.execute(query, params)
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            logging.error(f"Error getting schaeden by fahrzeug: {e}")
            return []

    def update_schaden_status(self, schaden_id, status):
        """Update the status of a schaden."""
        try:
            self.cursor.execute(
                "UPDATE schaeden SET status = ? WHERE id = ?",
                (status, schaden_id)
            )
            self.connection.commit()
            return self.cursor.rowcount > 0
        except sqlite3.Error as e:
            logging.error(f"Error updating schaden status: {e}")
            return False

    # Tour-related methods
    def start_tour(self, fahrer_id, start_km, ziel):
        """Start a new tour for a driver."""
        try:
            # Check if driver has an active tour
            self.cursor.execute(
                "SELECT id FROM touren WHERE fahrer_id = ? AND status = 'aktiv'",
                (fahrer_id,)
            )
            if self.cursor.fetchone():
                return False, "Es gibt bereits eine aktive Tour für diesen Fahrer."
            
            # Create new tour
            start_datum = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.cursor.execute(
                "INSERT INTO touren (fahrer_id, start_datum, start_km, ziel, status) VALUES (?, ?, ?, ?, 'aktiv')",
                (fahrer_id, start_datum, start_km, ziel)
            )
            self.connection.commit()
            return True, self.cursor.lastrowid
        except sqlite3.Error as e:
            logging.error(f"Error starting tour: {e}")
            return False, str(e)

    def end_tour(self, tour_id, ende_km):
        """End an active tour."""
        try:
            # Check if tour exists and is active
            self.cursor.execute(
                "SELECT id FROM touren WHERE id = ? AND status = 'aktiv'",
                (tour_id,)
            )
            if not self.cursor.fetchone():
                return False, "Tour nicht gefunden oder bereits beendet."
            
            # End tour
            ende_datum = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.cursor.execute(
                "UPDATE touren SET status = 'beendet', ende_datum = ?, ende_km = ? WHERE id = ?",
                (ende_datum, ende_km, tour_id)
            )
            self.connection.commit()
            return True, None
        except sqlite3.Error as e:
            logging.error(f"Error ending tour: {e}")
            return False, str(e)

    def get_active_tour_for_fahrer(self, fahrer_id):
        """Get active tour for a driver if exists."""
        try:
            self.cursor.execute(
                """SELECT t.id, t.start_datum, t.start_km, t.ziel
                FROM touren t
                WHERE t.fahrer_id = ? AND t.status = 'aktiv'""",
                (fahrer_id,)
            )
            return self.cursor.fetchone()
        except sqlite3.Error as e:
            logging.error(f"Error getting active tour: {e}")
            return None

    def get_tours_for_fahrer(self, fahrer_id, limit=10):
        """Get recent tours for a driver."""
        try:
            self.cursor.execute(
                """SELECT t.id, t.start_datum, t.ende_datum, t.start_km, t.ende_km, t.ziel, t.status
                FROM touren t
                WHERE t.fahrer_id = ?
                ORDER BY t.start_datum DESC
                LIMIT ?""",
                (fahrer_id, limit)
            )
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            logging.error(f"Error getting tours for fahrer: {e}")
            return []

    # Message-related methods
    def add_nachricht(self, absender_id, nachricht):
        """Add a new message."""
        try:
            self.cursor.execute(
                "INSERT INTO nachrichten (absender_id, nachricht) VALUES (?, ?)",
                (absender_id, nachricht)
            )
            self.connection.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            logging.error(f"Error adding nachricht: {e}")
            return None

    def get_unread_nachrichten_count(self):
        """Get count of unread messages."""
        try:
            self.cursor.execute(
                "SELECT COUNT(*) FROM nachrichten WHERE gelesen = 0"
            )
            return self.cursor.fetchone()[0]
        except sqlite3.Error as e:
            logging.error(f"Error getting unread nachrichten count: {e}")
            return 0

    def get_all_nachrichten(self, limit=50):
        """Get all messages with sender info."""
        try:
            self.cursor.execute(
                """SELECT n.id, f.name, n.nachricht, n.created_at, n.gelesen
                FROM nachrichten n
                JOIN fahrer f ON n.absender_id = f.id
                ORDER BY n.created_at DESC
                LIMIT ?""",
                (limit,)
            )
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            logging.error(f"Error getting all nachrichten: {e}")
            return []

    def mark_nachricht_as_read(self, nachricht_id):
        """Mark a message as read."""
        try:
            self.cursor.execute(
                "UPDATE nachrichten SET gelesen = 1 WHERE id = ?",
                (nachricht_id,)
            )
            self.connection.commit()
            return self.cursor.rowcount > 0
        except sqlite3.Error as e:
            logging.error(f"Error marking nachricht as read: {e}")
            return False

    # Kalender-related methods
    def add_kalender_eintrag(self, titel, datum, beschreibung=None, fahrer_id=None, ziel=None):
        """Add a new calendar entry."""
        try:
            self.cursor.execute(
                "INSERT INTO kalender (titel, beschreibung, datum, fahrer_id, ziel) VALUES (?, ?, ?, ?, ?)",
                (titel, beschreibung, datum, fahrer_id, ziel)
            )
            self.connection.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            logging.error(f"Error adding kalender eintrag: {e}")
            return None

    def get_kalender_eintraege(self, start_date, end_date, fahrer_id=None):
        """Get calendar entries in a date range."""
        try:
            query = """SELECT k.id, k.titel, k.beschreibung, k.datum, f.name, k.ziel
                    FROM kalender k
                    LEFT JOIN fahrer f ON k.fahrer_id = f.id
                    WHERE k.datum BETWEEN ? AND ?"""
            params = [start_date, end_date]
            
            if fahrer_id:
                query += " AND k.fahrer_id = ?"
                params.append(fahrer_id)
                
            query += " ORDER BY k.datum"
            
            self.cursor.execute(query, params)
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            logging.error(f"Error getting kalender eintraege: {e}")
            return []

    def delete_kalender_eintrag(self, eintrag_id):
        """Delete a calendar entry."""
        try:
            self.cursor.execute(
                "DELETE FROM kalender WHERE id = ?",
                (eintrag_id,)
            )
            self.connection.commit()
            return self.cursor.rowcount > 0
        except sqlite3.Error as e:
            logging.error(f"Error deleting kalender eintrag: {e}")
            return False

# Singleton pattern
db_manager = DatabaseManager()

def get_db_manager():
    """Get the database manager singleton."""
    return db_manager
