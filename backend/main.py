from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

# Importa la nuova classe di connessione
from firestore_connection import FirestoreConnection

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],  
)

# Inizializza una sola volta la connessione Firestore (opzionale ma consigliato)
firestore_conn = FirestoreConnection()

@app.get("/top-players/")
def get_top_players(game_type: str, limit: int = 10):
    """
    Esegue una query su Firestore e ritorna i giocatori con best_rating più alto
    in base al game_type indicato (es. 'chess_blitz', 'chess_bullet', 'chess_rapid').
    """
    results = firestore_conn.get_top_players(game_type, limit)

    if not results:
        return {"message": "Nessun risultato trovato per questo game_type"}
    
    return {
        "game_type": game_type,
        "top_players": results
    }
    
@app.get("/search/")
def search_player(player_name: str = Query(..., title="Nome del giocatore")):
    """
    Recupera i dati di un singolo giocatore da Firestore.
    Lo username del giocatore coincide con l'ID del documento nella collection chesscom_users.
    """
    data = firestore_conn.get_user_data(player_name)
    if not data:
        return {"message": "Nessun risultato trovato per questo giocatore"}

    # Ricostruiamo un formato di risposta simile a quello di BigQuery,
    # ossia un array di "righe" per ogni game_type (chess_blitz, chess_bullet, chess_rapid).
    results = []
    for game_type in ["chess_blitz", "chess_bullet", "chess_rapid"]:
        if game_type in data:
            results.append({
                "player_name": player_name,
                "game_type": game_type,
                "last_rating": data[game_type].get("last_rating", None),
                "best_rating": data[game_type].get("best_rating", None),
            })
    
    return {
        "player_name": player_name,
        "stats": results
    }