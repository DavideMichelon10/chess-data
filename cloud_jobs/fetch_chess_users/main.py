import os
import mysql.connector
import requests
import time
from datetime import datetime
import logging

# Configurazione del logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('titled_players_fetcher')

# Chess.com API
TITLED_PLAYERS_URL = "https://api.chess.com/pub/titled/{}"

# Variabili d'ambiente
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
INSTANCE_CONNECTION_NAME = os.getenv("INSTANCE_CONNECTION_NAME")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

TITLES = ["GM", "IM", "FM", "CM"]

def get_db_connection():
    """Crea una connessione a MySQL."""
    try:
        conn = mysql.connector.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            unix_socket=f"/cloudsql/{INSTANCE_CONNECTION_NAME}"
        )
        logger.info("✅ Connessione a MySQL riuscita!")
        return conn
    except mysql.connector.Error as e:
        logger.error(f"❌ Errore di connessione a MySQL: {e}")
        return None

def get_titled_players(title):
    """Scarica la lista di giocatori titolati per un dato titolo."""
    url = TITLED_PLAYERS_URL.format(title)
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            return response.json().get("players", [])
        else:
            logger.warning(f"Risposta non valida per {title}: {response.status_code}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Errore durante il recupero dei giocatori {title}: {e}")
    return []

def insert_titled_players(conn, players, title):
    """Inserisce i giocatori titolati nel database."""
    if not players:
        return
    
    try:
        cursor = conn.cursor()
        
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        values = [(username, title, current_time) for username in players]
        
        query = """
        INSERT INTO titled_players (username, title, last_updated)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE 
            title = VALUES(title),
            last_updated = VALUES(last_updated);
        """
        
        cursor.executemany(query, values)
        conn.commit()
        logger.info(f"✅ Inseriti/aggiornati {len(players)} giocatori con titolo {title}")
        
    except Exception as e:
        logger.error(f"❌ Errore nell'inserimento in MySQL: {e}")
    finally:
        cursor.close()

def main():
    logger.info("🚀 Avvio del job: Fetch Titled Players")
    
    # Connessione al DB
    conn = get_db_connection()
    if not conn:
        logger.error("❌ Impossibile connettersi al database. Terminazione.")
        return
    
    try:
        # Per ogni titolo, recupera e inserisci i giocatori
        for title in TITLES:
            logger.info(f"📥 Scaricando giocatori con titolo: {title}")
            players = get_titled_players(title)
            logger.info(f"Trovati {len(players)} giocatori con titolo {title}")
            
            # Inserisci tutti i giocatori nel database
            insert_titled_players(conn, players, title)
            
            # Piccola pausa tra le richieste per diversi titoli
            if title != TITLES[-1]:  # Non aspettare dopo l'ultimo titolo
                time.sleep(1)
    
    finally:
        conn.close()
        logger.info("✅ Job completato con successo!")

if __name__ == "__main__":
    main()