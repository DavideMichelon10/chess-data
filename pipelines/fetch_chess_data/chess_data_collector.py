import requests
import datetime
import time
import os
import hashlib
import urllib.parse
from google.cloud import firestore, storage
from google.cloud import logging as cloud_logging
from typing import Optional, Dict, Any, Tuple, List
from backend.firestore_connection import FirestoreConnection  # Import della connessione esistente

# Configurazione
PROJECT = "chess-data-451709"
BUCKET_NAME = f"{PROJECT}-chesscom-avatars"
CHESS_API_BASE = "https://api.chess.com/pub"
REQUEST_DELAY = 0.5  # Secondi tra le richieste API
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
LEADERBOARD_TYPES = ["live_bullet", "live_rapid", "daily", "live_blitz"]

# Logging
logging_client = cloud_logging.Client()
logger = logging_client.logger('chess_data_collector')

class ChessDataCollector:
    """Gestisce la raccolta dati da Chess.com e il salvataggio su Firestore."""
    
    def __init__(self, firestore_conn: Optional[FirestoreConnection] = None) -> None:
        """
        Inizializza ChessDataCollector.
        
        Se viene passata una connessione Firestore, la usa.
        Altrimenti crea una nuova connessione Firestore.
        """
        self.firestore_conn = firestore_conn or FirestoreConnection()
        self.db = self.firestore_conn.db  # Usa Firestore
        self.storage_client = storage.Client()
        self.bucket = self.storage_client.bucket(BUCKET_NAME)
        self._validate_bucket()

    def _validate_bucket(self) -> None:
        """Verifica che il bucket esista."""
        if not self.bucket.exists():
            error_msg = f"Bucket {BUCKET_NAME} non esiste!"
            logger.log_text(error_msg, severity="CRITICAL")
            raise ValueError(error_msg)

    def get_existing_players(self) -> List[str]:
        """Ottiene gli username dei giocatori già presenti in Firestore."""
        users_ref = self.db.collection("chesscom_users")
        docs = users_ref.stream()
        return [doc.id for doc in docs]

    def get_top_players_from_leaderboards(self) -> List[str]:
        """Recupera i top 50 giocatori da più leaderboard di Chess.com."""
        url = f"{CHESS_API_BASE}/leaderboards"
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            response.raise_for_status()
            leaderboards = response.json()

            top_players = set()
            for category in LEADERBOARD_TYPES:
                for player in leaderboards.get(category, []):
                    top_players.add(player["username"])

            logger.log_text(f"Recuperati {len(top_players)} giocatori dalle leaderboard.", severity="INFO")
            return list(top_players)
        except requests.exceptions.RequestException as e:
            logger.log_text(f"Errore nel recupero delle leaderboard: {str(e)}", severity="ERROR")
            return []

    def get_player_profile(self, username: str) -> Tuple[int, Optional[Dict[str, Any]]]:
        """Recupera il profilo del giocatore da Chess.com."""
        url = f"{CHESS_API_BASE}/player/{username}"
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            status_code = response.status_code

            if status_code == 200:
                return status_code, response.json()
            logger.log_text(f"Errore {status_code} per {username}: {response.text}", severity="WARNING")
            return status_code, None
        except requests.exceptions.RequestException as e:
            logger.log_text(f"Errore nel recupero del profilo di {username}: {str(e)}", severity="ERROR")
            return 500, None

    def get_player_stats(self, username: str) -> Optional[Dict[str, Any]]:
        """Recupera le statistiche del giocatore da Chess.com."""
        url = f"{CHESS_API_BASE}/player/{username}/stats"
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.log_text(f"Errore nel recupero delle statistiche per {username}: {str(e)}", severity="ERROR")
            return None

    def download_and_store_avatar(self, avatar_url: str, username: str) -> Optional[str]:
        """
        Scarica l'immagine del profilo e la salva nel bucket GCP.
        """
        if not avatar_url:
            return None

        try:
            url_hash = hashlib.md5(avatar_url.encode()).hexdigest()
            file_extension = os.path.splitext(urllib.parse.urlparse(avatar_url).path)[1] or ".jpg"
            blob_name = f"avatars/{username}/{url_hash}{file_extension}"
            
            blob = self.bucket.blob(blob_name)
            if not blob.exists():
                try:
                    response = requests.get(avatar_url, headers=HEADERS, timeout=10)
                    response.raise_for_status()
                    
                    blob.upload_from_string(
                        response.content, 
                        content_type=response.headers.get('content-type', 'image/jpeg')
                    )
                    logger.log_text(f"Avatar salvato per {username}", severity="INFO")
                    
                except requests.exceptions.RequestException as e:
                    logger.log_text(f"Errore nel download dell'avatar per {username}: {str(e)}", severity="ERROR")
                    return None
            
            return f"gs://{BUCKET_NAME}/{blob_name}"
        
        except Exception as e:
            logger.log_text(f"Errore durante il salvataggio dell'avatar di {username}: {str(e)}", severity="ERROR")
            return None

    def save_to_firestore(self, player_name: str, stats_data: Dict[str, Any], profile_data: Dict[str, Any], stored_avatar_url: Optional[str]) -> None:
        """Salva i dati del giocatore in Firestore."""
        player_name = player_name.lower()
        doc_ref = self.db.collection("chesscom_users").document(player_name)
        timestamp = datetime.datetime.utcnow().isoformat()

        data_to_save = {
            "timestamp": timestamp,
            "last_updated": firestore.SERVER_TIMESTAMP
        }

        if profile_data:
            profile_fields = {
                "name": profile_data.get("name"),
                "country": profile_data.get("country"),
                "location": profile_data.get("location"),
                "followers": profile_data.get("followers"),
                "joined": profile_data.get("joined"),
                "last_online": profile_data.get("last_online"),
                "status": profile_data.get("status"),
                "username": profile_data.get("username"),
                "player_id": profile_data.get("player_id"),
            }
            if "title" in profile_data:
                profile_fields["title"] = profile_data["title"]
            
            data_to_save.update({k: v for k, v in profile_fields.items() if v is not None})

        if stored_avatar_url:
            data_to_save["avatar_storage_url"] = stored_avatar_url
            data_to_save["original_avatar_url"] = profile_data.get("avatar")

        for game_type, stats in stats_data.items():
            if isinstance(stats, dict) and "last" in stats and "record" in stats:
                stats_fields = {
                    "last_rating": stats["last"].get("rating"),
                    "best_rating": stats.get("best", {}).get("rating"),
                    "best_game_url": stats.get("best", {}).get("game"),
                    "win": stats["record"].get("win"),
                    "loss": stats["record"].get("loss"),
                    "draw": stats["record"].get("draw"),
                }
                data_to_save[game_type] = {k: v for k, v in stats_fields.items() if v is not None}

        doc_ref.set(data_to_save, merge=True)
        logger.log_text(f"Dati salvati per {player_name}", severity="INFO")

    def fetch_chess_data(self) -> None:
        """Aggiorna i dati dei giocatori."""
        existing_players = self.get_existing_players()
        leaderboard_players = self.get_top_players_from_leaderboards()
        all_players = list(set(existing_players + leaderboard_players))

        for player in all_players:
            status, profile = self.get_player_profile(player)
            if status != 200 or not profile:
                continue

            stats_data = self.get_player_stats(player) or {}
            avatar_url = profile.get("avatar")
            stored_avatar_url = self.download_and_store_avatar(avatar_url, player) if avatar_url else None
            self.save_to_firestore(player, stats_data, profile, stored_avatar_url)
            time.sleep(REQUEST_DELAY)