import requests
import datetime
import time
import os
import json
import hashlib
import urllib.parse
from google.cloud import firestore, storage
from typing import Optional, Dict, Any, Tuple, List
import re
from google.cloud import bigquery
from commons.firestore_connection import FirestoreConnection
from commons.bigquery_connection import BigQueryConnection
from commons.bucket_manager import BucketManager
from commons.Config import Config
import pandas as pd

PROJECT = Config.get("PROJECT")
CHESSCOM_API_BASE = Config.get("CHESSCOM_API_BASE")
REQUEST_DELAY = Config.get("REQUEST_DELAY")
HEADERS = Config.get("HEADERS")
FIRESTORE_CHESSCOM_USERS_COLLECTION = Config.get("FIRESTORE_CHESSCOM_USERS_COLLECTION")
LEADERBOARD_TYPES = ["live_bullet", "live_rapid", "daily", "live_blitz"]

logger = Config.init_logging()

class ChesscomDataCollector:
    """Gestisce la raccolta dati da Chess.com e il salvataggio su Firestore."""
    
    def __init__(self, firestore_conn: Optional[FirestoreConnection] = None) -> None:
        self.firestore_conn = firestore_conn or FirestoreConnection()
        self.db = self.firestore_conn.db
        self.bucket_avatar =  BucketManager(Config.get("BUCKET_NAME_AVATARS"))
        self.bucket_upload_data = BucketManager(Config.get("BUCKET_UPLOAD_DATA"))


    def get_existing_players(self) -> List[str]:
        """Ottiene gli username dei giocatori già presenti in Firestore."""
        users_ref = self.db.collection(FIRESTORE_CHESSCOM_USERS_COLLECTION)
        docs = users_ref.stream()
        return [doc.id for doc in docs]

    def get_top_players_from_leaderboards(self) -> List[str]:
        """Recupera i top 50 giocatori da più leaderboard di Chess.com."""
        url = f"{CHESSCOM_API_BASE}/leaderboards"
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
        url = f"{CHESSCOM_API_BASE}/player/{username}"
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
        url = f"{CHESSCOM_API_BASE}/player/{username}/stats"
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
            
            blob = self.bucket_avatar.get_blob(blob_name)
            
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
            
            return f"gs://{self.bucket_avatar.bucket_name}/{blob_name}"
        
        except Exception as e:
            logger.log_text(f"Errore durante il salvataggio dell'avatar di {username}: {str(e)}", severity="ERROR")
            return None

    def save_to_firestore(self, player_name: str, stats_data: Dict[str, Any], profile_data: Dict[str, Any], stored_avatar_url: Optional[str]) -> None:
        """Salva i dati del giocatore in Firestore."""
        player_name = player_name.lower()
        doc_ref = self.db.collection(FIRESTORE_CHESSCOM_USERS_COLLECTION).document(player_name)
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
        
    def get_collected_days(self, player: str) -> List[str]:
        """Ottiene i giorni già raccolti per un giocatore."""
        doc_ref = self.db.collection(FIRESTORE_CHESSCOM_USERS_COLLECTION).document(player)
        doc = doc_ref.get()
        return doc.to_dict().get("collected_days", []) if doc.exists else []

    def save_collected_days(self, player: str, days: List[str]) -> None:
        if isinstance(days, set):
            days = list(days)
        doc_ref = self.db.collection(FIRESTORE_CHESSCOM_USERS_COLLECTION).document(player)
        doc_ref.set({"collected_days": firestore.ArrayUnion(days)}, merge=True)


    def extract_moves_from_pgn(self, pgn: str) -> List[str]:

        move_lines = []
        
        for line in pgn.strip().split('\n'):
            if re.match(r'^\d+\.', line):
                move_lines.append(line)
        
        all_moves_text = ' '.join(move_lines)
        
        all_moves_text = re.sub(r'\{[^}]*\}', '', all_moves_text)
        
        all_moves_text = re.sub(r'\s(0-1|1-0|1\/2-1\/2)$', '', all_moves_text)
        all_moves_text = re.sub(r'\s+', ' ', all_moves_text).strip()
        
        return all_moves_text


    def _save_game_to_csv(self, player: str, game_day: str, game_data: dict) -> None:
        """Salva i dati di un giocatore in un CSV nel bucket senza sovrascrivere."""
        game_id = game_data["game_id"]
        local_csv_path = f"/tmp/{player}_{game_day}_{game_id}.csv"
        gcs_csv_path = f"{player}/{game_day}/{game_id}.csv"
        df = pd.DataFrame([game_data])

        # Se il file esiste già, scriviamo in modalità "append" (a)
        write_mode = "a" if os.path.exists(local_csv_path) else "w"
        header = not os.path.exists(local_csv_path)  # Scrive l'header solo se il file non esiste

        df.to_csv(local_csv_path, index=False, encoding="utf-8", mode=write_mode, header=header)

        self.bucket_upload_data.upload_file(local_csv_path, gcs_csv_path)
        os.remove(local_csv_path)
        
    def fetch_and_store_games(self, players: List[str]) -> None:
        """Recupera le partite giorno per giorno e carica i dati in BigQuery giocatore per giocatore."""
        
        yesterday = datetime.date.today() - datetime.timedelta(days=1)
        yesterday_year = yesterday.year
        yesterday_month = yesterday.month
        yesterday_str = yesterday.strftime("%Y-%m-%d")

        for player in players:
            print(f"🔄 Analizzando {player}...")

            self.bucket_upload_data.delete_files_under_path(player)
            collected_days = self.get_collected_days(player)
            processed_days = set()

            for year in range(2025, yesterday_year + 1):  # 🔹 Non superiamo l'anno di ieri
                for month in range(1, 13):
                    # 🔹 Se il mese è successivo a ieri nell'anno corrente, interrompiamo il ciclo
                    if year == yesterday_year and month > yesterday_month:
                        break

                    url = f"https://api.chess.com/pub/player/{player}/games/{year}/{month:02d}"
                    response = requests.get(url, headers=HEADERS, timeout=10)

                    if response.status_code != 200:
                        print(f"❌ Errore nel recupero dati per {player} - {year}/{month:02d}")
                        continue

                    games = response.json().get("games", [])

                    for game in games:
                        end_time = datetime.datetime.utcfromtimestamp(game["end_time"])
                        game_day = end_time.strftime("%Y-%m-%d")

                        if game_day >= yesterday_str:
                            continue

                        if game_day in collected_days:
                            continue

                        game_data = {
                            "game_id": game["url"].split("/")[-1],
                            "user_id": player,
                            "white_player": game.get("white", {}).get("username"),
                            "black_player": game.get("black", {}).get("username"),
                            "rating_white": game.get("white", {}).get("rating"),
                            "rating_black": game.get("black", {}).get("rating"),
                            "result_white": game.get("white", {}).get("result"),  
                            "result_black": game.get("black", {}).get("result"),
                            "accuracy_white": game.get("accuracies", {}).get("white", 0.0),
                            "accuracy_black": game.get("accuracies", {}).get("black", 0.0),
                            "time_control": game["time_control"],
                            "time_class": game.get("time_class"),
                            "end_time": end_time.timestamp(),
                            "moves": self.extract_moves_from_pgn(game["pgn"]),
                            "eco": game.get("eco"),
                            "url": game["url"]
                        }

                        self._save_game_to_csv(player, game_day, game_data)
                        processed_days.add(game_day)

                    time.sleep(REQUEST_DELAY)

            success = self._upload_to_gcs_and_bigquery(player)

            if success:
                self.save_collected_days(player, processed_days)
                print(f"✅ Giorni caricati su Firestore per {player}: {processed_days}")
            else:
                print(f"❌ Errore nell'upload su BigQuery per {player}. Giorni non salvati in Firestore.")
    
    def _upload_to_gcs_and_bigquery(self, player: str) -> None:

        BQ_DATASET= Config.get("BQ_DATASET_CHESSCOM")
        BQ_TABLE = "chess_games"
        
        blobs = self.bucket_upload_data.list_files(prefix=f"{player}/")
        
        gcs_uris = [self.bucket_upload_data.get_blob_uri(blob) for blob in blobs]

        # Creazione connessione a BigQuery
        bq_conn = BigQueryConnection()

        job_config = bigquery.LoadJobConfig(
            source_format=bigquery.SourceFormat.CSV,
            skip_leading_rows=1
        )

        try:
            load_job = bq_conn.connection.load_table_from_uri(
                gcs_uris,
                f"{PROJECT}.{BQ_DATASET}.{BQ_TABLE}",
                job_config=job_config
            )
            load_job.result()  # Attende il completamento del job
            print(f"✅ Dati caricati in BigQuery per {player}")
            return True

        except Exception as e:
            print(f"❌ Errore durante il caricamento su BigQuery: {str(e)}")
            raise e