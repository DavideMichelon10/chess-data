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

    def get_top_players(self, game_type: str, limit: int = 10):
        """
        Esegue una query su Firestore e ritorna i top player 
        (ordinati per best_rating decrescente) per un certo game_type.
        """
        docs = (
            self.db.collection("chesscom_users")
            .order_by(f"{game_type}.best_rating", direction=firestore.Query.DESCENDING)
            .limit(limit)
            .stream()
        )
        
        results = []
        for doc in docs:
            data = doc.to_dict()
            if game_type in data:
                # Se esiste un campo "avatar_storage_url", convertiamolo da gs:// a https://
                avatar_gs_url = data.get("avatar_storage_url")
                avatar_url = None
                if avatar_gs_url:
                    avatar_url = avatar_gs_url.replace("gs://", "https://storage.googleapis.com/")
                
                results.append({
                    "player_name": doc.id,
                    "game_type": game_type,
                    "best_rating": data[game_type].get("best_rating", None),
                    "avatar_url": avatar_url
                })
        return results