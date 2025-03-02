import requests
import datetime
import time
from google.cloud import firestore
from google.cloud import logging as cloud_logging

# Inizializzazione dei client
db = firestore.Client()
logging_client = cloud_logging.Client()
logger = logging_client.logger('chess_data_collector')

CATEGORIES = ["GM", "IM", "FM", "MANUAL_PLAYERS"]
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
CHESS_API_BASE = "https://api.chess.com/pub"

# Giocatori manualmente inseriti
MANUAL_PLAYERS = ["davideblunder", "ImNoob66"]

def get_players(category):
    """Recupera la lista dei giocatori in base alla categoria."""
    logger.log_text(f"Getting data for category: {category}")
    if category == "manual":
        return MANUAL_PLAYERS
    else:
        url = f"{CHESS_API_BASE}/titled/{category.upper()}"
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            players = response.json().get("players", [])
            logger.log_text(f"Retrieved {len(players)} players for category {category}")
            return players
        else:
            logger.log_text(f"Errore nel recupero della lista per {category}: {response.status_code}", severity="ERROR")
            return []

def fetch_chess_data():
    """Recupera i dati dei giocatori per ciascuna categoria e li salva in Firestore."""
    for category in CATEGORIES:
        players = get_players(category)
        logger.log_text(f"Processing {len(players)} players from category {category}")
        
        for player in players:
            try:
                url = f"{CHESS_API_BASE}/player/{player}/stats"
                response = requests.get(url, headers=HEADERS)
                if response.status_code == 200:
                    data = response.json()
                    logger.log_text(f"Dati ricevuti per {player}", severity="INFO")
                    save_to_firestore(player, data, category)
                else:
                    logger.log_text(f"Errore API per {player} {response.status_code}: {response.text}", severity="ERROR")
            except Exception as e:
                logger.log_text(f"Errore durante la richiesta API per {player}: {str(e)}", severity="ERROR")
            time.sleep(0.5)
        logger.log_text(f"Dati salvati con successo per tutti i giocatori di {category}.", severity="INFO")

def save_to_firestore(player_name, data, category):
    """Salva i dati in Firestore, aggiungendo la categoria del giocatore."""
    doc_ref = db.collection("chesscom_users").document(player_name)
    timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
    stats_to_save = {"category": category, "timestamp": timestamp}
    
    for game_type, stats in data.items():
        if isinstance(stats, dict) and "last" in stats and "record" in stats:
            stats_to_save[game_type] = {
                "last_rating": stats["last"]["rating"],
                "best_rating": stats.get("best", {}).get("rating"),
                "best_game_url": stats.get("best", {}).get("game"),
                "win": stats["record"]["win"],
                "loss": stats["record"]["loss"],
                "draw": stats["record"]["draw"],
            }
    
    if stats_to_save:
        doc_ref.set(stats_to_save, merge=True)
        logger.log_text(f"Dati inseriti in Firestore per {player_name}", severity="INFO")
    else:
        logger.log_text(f"Nessun dato valido per {player_name}", severity="WARNING")

if __name__ == "__main__":
    logger.log_text("Script di raccolta dati Chess.com avviato", severity="INFO")
    try:
        fetch_chess_data()
        logger.log_text("Script completato con successo", severity="INFO")
    except Exception as e:
        logger.log_text(f"Errore fatale nell'esecuzione dello script: {str(e)}", severity="CRITICAL")
        raise


