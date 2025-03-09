
from google.cloud import logging as cloud_logging

class Config:
    PROJECT = "chess-data-451709"
    BUCKET_NAME_AVATARS = f"{PROJECT}-chesscom-avatars"
    BUCKET_UPLOAD_DATA = "chesscom-games-data"
    CHESSCOM_API_BASE = "https://api.chess.com/pub"
    FIRESTORE_CHESSCOM_USERS_COLLECTION =  "chesscom_users"
    BQ_DATASET_CHESSCOM = "chesscom"
    REQUEST_DELAY = 0.5
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    @classmethod
    def get(cls, key):
        return getattr(cls, key, None)
    
    @staticmethod
    def init_logging():
        logging_client = cloud_logging.Client()
        return logging_client.logger('chess_data_collector')