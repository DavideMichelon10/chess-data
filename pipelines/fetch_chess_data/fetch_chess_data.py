import requests
import datetime
import time
import os
import hashlib
import urllib.parse
from functools import lru_cache
from google.cloud import firestore
from google.cloud import storage
from google.cloud import logging as cloud_logging
from typing import Optional, Dict, Any, Tuple, List
# Configurazione
PROJECT = "chess-data-451709"
BUCKET_NAME = f"{PROJECT}-chesscom-avatars"
CHESS_API_BASE = "https://api.chess.com/pub"
CATEGORIES = ["GM", "IM", "FM", "MANUAL_PLAYERS"]
MANUAL_PLAYERS = ["davideblunder", "ImNoob66"]
REQUEST_DELAY = 0.5  # Secondi tra le richieste API
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# Inizializzazione del logging
logging_client = cloud_logging.Client()
logger = logging_client.logger('chess_data_collector')

class ChessDataCollector:
    """Classe per gestire la raccolta dei dati da Chess.com e il salvataggio su GCP."""
    
    def __init__(self) -> None:
        """Inizializza i client GCP e le risorse necessarie."""
        self.db = firestore.Client()
        self.storage_client = storage.Client()
        self.bucket = self.storage_client.bucket(BUCKET_NAME)
        self._validate_bucket()
    
    def _validate_bucket(self) -> None:
        """Verifica che il bucket esista."""
        if not self.bucket.exists():
            error_msg = f"Bucket {BUCKET_NAME} non esiste! Crearlo prima di eseguire lo script."
            logger.log_text(error_msg, severity="CRITICAL")
            raise ValueError(error_msg)
    
    @lru_cache(maxsize=32)
    def get_players(self, category: str) -> List[str]:
        """
        Recupera la lista dei giocatori in base alla categoria con caching.
        
        Args:
            category: Categoria di giocatori (es. "GM", "IM", "FM", "MANUAL_PLAYERS")
            
        Returns:
            Lista di username dei giocatori
        """
        logger.log_text(f"Getting data for category: {category}")
        
        if category == "MANUAL_PLAYERS":
            return MANUAL_PLAYERS
        
        url = f"{CHESS_API_BASE}/titled/{category.upper()}"
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            response.raise_for_status()  # Solleva un'eccezione per errori HTTP
            
            players = response.json().get("players", [])
            logger.log_text(f"Retrieved {len(players)} players for category {category}")
            return players
            
        except requests.exceptions.RequestException as e:
            logger.log_text(f"Errore nel recupero della lista per {category}: {str(e)}", severity="ERROR")
            return []
    
    def get_player_profile(self, username: str) -> Tuple[int, Optional[Dict[str, Any]]]:
        """
        Recupera il profilo del giocatore da Chess.com.
        Restituisce una tupla (status_code, dati).
        Se il giocatore non esiste (404), restituisce (404, None).
        """
        url = f"{CHESS_API_BASE}/player/{username}"
        
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            status_code = response.status_code  # Salviamo lo status code

            if status_code == 200:
                return status_code, response.json()  # Restituisce (200, profilo JSON)

            # Log per gli altri status code
            if status_code == 404:
                logger.log_text(f"Utente '{username}' non trovato su Chess.com (404)", severity="WARNING")
            else:
                logger.log_text(f"Errore HTTP {status_code} per {username}: {response.text}", severity="ERROR")
            
            return status_code, None  # Restituisce (status_code, None) in caso di errore

        except requests.exceptions.RequestException as e:
            logger.log_text(f"Errore nel recupero del profilo per {username}: {str(e)}", severity="ERROR")
            return 500, None
    
    def get_player_stats(self, username: str) -> Optional[Dict[str, Any]]:

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
        Scarica l'immagine del profilo e la salva nel bucket.
        
        Args:
            avatar_url: URL dell'avatar del giocatore
            username: Username del giocatore
            
        Returns:
            URL dell'immagine salvata nel bucket o None in caso di errore
        """
        if not avatar_url:
            return None
        
        try:
            # Crea un nome univoco per l'immagine
            url_hash = hashlib.md5(avatar_url.encode()).hexdigest()
            file_extension = os.path.splitext(urllib.parse.urlparse(avatar_url).path)[1] or ".jpg"
            blob_name = f"avatars/{username}/{url_hash}{file_extension}"
            
            # Controlla se l'immagine esiste già nel bucket
            blob = self.bucket.blob(blob_name)
            if not blob.exists():
                try:
                    response = requests.get(avatar_url, headers=HEADERS, timeout=10)
                    response.raise_for_status()
                    
                    # Carica l'immagine nel bucket
                    blob.upload_from_string(
                        response.content, 
                        content_type=response.headers.get('content-type', 'image/jpeg')
                    )
                    logger.log_text(f"Avatar salvato per {username}", severity="INFO")
                    
                except requests.exceptions.RequestException as e:
                    logger.log_text(f"Errore nel download dell'avatar per {username}: {str(e)}", severity="ERROR")
                    return None
            
            # Restituisci l'URL pubblico dell'immagine
            return f"gs://{BUCKET_NAME}/{blob_name}"
        
        except Exception as e:
            logger.log_text(f"Errore durante il salvataggio dell'avatar di {username}: {str(e)}", severity="ERROR")
            return None
    
    def save_to_firestore(
        self, 
        player_name: str, 
        stats_data: Dict[str, Any], 
        profile_data: Dict[str, Any], 
        stored_avatar_url: Optional[str], 
        category: str
    ) -> None:
        """
        Salva i dati in Firestore.
        
        Args:
            player_name: Username del giocatore
            stats_data: Statistiche del giocatore
            profile_data: Dati del profilo del giocatore
            stored_avatar_url: URL dell'avatar nel bucket
            category: Categoria del giocatore
        """
        doc_ref = self.db.collection("chesscom_users").document(player_name)
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        
        # Prepara i dati base da salvare
        data_to_save = {
            "category": category,
            "timestamp": timestamp,
            "last_updated": firestore.SERVER_TIMESTAMP
        }
        
        # Aggiungi i campi del profilo richiesti
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
            
            # Pulizia dei valori None
            profile_fields = {k: v for k, v in profile_fields.items() if v is not None}
            
            # Aggiungi l'URL dell'avatar salvato
            if stored_avatar_url:
                profile_fields["avatar_storage_url"] = stored_avatar_url
                profile_fields["original_avatar_url"] = profile_data.get("avatar")
            
            # Aggiungi i campi del profilo ai dati da salvare
            data_to_save.update(profile_fields)
        
        # Elabora le statistiche di gioco
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
                
                # Pulizia dei valori None
                stats_fields = {k: v for k, v in stats_fields.items() if v is not None}
                
                if stats_fields:
                    data_to_save[game_type] = stats_fields
        
        # Salva i dati in Firestore con merge per non sovrascrivere dati esistenti
        doc_ref.set(data_to_save, merge=True)
        logger.log_text(f"Dati inseriti in Firestore per {player_name}", severity="INFO")
    
    def process_player(self, player: str, category: str) -> None:
        """
        Elabora un singolo giocatore: recupera profilo, statistiche e avatar.
        
        Args:
            player: Username del giocatore
            category: Categoria del giocatore
        """
        try:
            # Ottieni il profilo del giocatore
            profile = self.get_player_profile(player)
            if not profile:
                logger.log_text(f"Profilo non disponibile per {player}", severity="WARNING")
                return
            
            # Ottieni e salva l'avatar
            avatar_url = profile.get("avatar")
            stored_avatar_url = None
            if avatar_url:
                stored_avatar_url = self.download_and_store_avatar(avatar_url, player)
            
            # Ottieni le statistiche del giocatore
            stats_data = self.get_player_stats(player) or {}
            
            # Salva entrambi i set di dati
            self.save_to_firestore(player, stats_data, profile, stored_avatar_url, category)
            
        except Exception as e:
            logger.log_text(f"Errore durante l'elaborazione del giocatore {player}: {str(e)}", severity="ERROR")
    
    def fetch_chess_data(self) -> None:
        """Recupera i dati dei giocatori per ciascuna categoria e li salva in Firestore."""
        start_time = time.time()
        total_players_processed = 0
        
        try:
            for category in CATEGORIES:
                players = self.get_players(category)
                num_players = len(players)
                total_players_processed += num_players
                
                logger.log_text(f"Processing {num_players} players from category {category}")
                
                for i, player in enumerate(players, 1):
                    self.process_player(player, category)
                    
                    # Log di progresso ogni 10 giocatori o all'ultimo giocatore
                    if i % 10 == 0 or i == num_players:
                        logger.log_text(f"Progresso categoria {category}: {i}/{num_players} giocatori elaborati")
                    
                    # Rispetta i limiti di rate dell'API
                    time.sleep(REQUEST_DELAY)
                
                logger.log_text(f"Dati salvati con successo per tutti i giocatori di {category}.", severity="INFO")
            
            execution_time = time.time() - start_time
            logger.log_text(
                f"Script completato: {total_players_processed} giocatori elaborati in {execution_time:.2f} secondi", 
                severity="INFO"
            )
            
        except Exception as e:
            logger.log_text(f"Errore durante l'esecuzione: {str(e)}", severity="ERROR")
            raise


def main() -> None:
    logger.log_text("Script di raccolta dati Chess.com avviato", severity="INFO")
    try:
        collector = ChessDataCollector()
        collector.fetch_chess_data()
        logger.log_text("Script completato con successo", severity="INFO")
    except Exception as e:
        logger.log_text(f"Errore fatale nell'esecuzione dello script: {str(e)}", severity="CRITICAL")
        raise


if __name__ == "__main__":
    main()