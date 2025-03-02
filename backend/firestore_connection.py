# firestore_connection.py

import firebase_admin
from firebase_admin import credentials, firestore

class FirestoreConnection:
    def __init__(self):
        # Inizializza l'app Firebase se non è già stata inizializzata
        if not firebase_admin._apps:
            cred = credentials.Certificate('/Users/davide.michelon/personal_projects/chess-data/backend/firestore_credentials.json')
            firebase_admin.initialize_app(cred)
        self.db = firestore.client()

    def get_user_data(self, username: str):
        """
        Ritorna il dizionario contenente i dati di un giocatore
        (il document ID è lo username).
        Se non esiste, ritorna None.
        """
        doc_ref = self.db.collection("chesscom_users").document(username)
        doc = doc_ref.get()
        if doc.exists:
            return doc.to_dict()
        return None

    def get_top_players(self, game_type: str, category: str = None, limit: int = 100):
        """
        Esegue una query su Firestore e ritorna i top player (ordinati per actual_rating 
        decrescente) per un certo game_type, filtrando eventualmente anche su category.
        """
        # Costruisci la query di base
        query = self.db.collection("chesscom_users")

        if category:
            query = query.where("category", "==", category)

        query = query.order_by(f"{game_type}.last_rating", direction=firestore.Query.DESCENDING)

        docs = query.limit(limit).stream()
        
        results = []
        for doc in docs:
            data = doc.to_dict()

            if game_type in data:
                avatar_gs_url = data.get("avatar_storage_url")
                avatar_url = None
                if avatar_gs_url:
                    avatar_url = avatar_gs_url.replace("gs://", "https://storage.googleapis.com/")
                results.append({
                    "username": doc.id,
                    "last_rating": data[game_type].get("last_rating", None),
                    "name": data.get("name", None),
                    "win": data[game_type].get("win", None),
                    "loss": data[game_type].get("loss", None),
                    "draw": data[game_type].get("draw", None),
                    "avatar_url": avatar_url
                })
        return results