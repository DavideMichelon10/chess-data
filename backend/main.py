from pathlib import Path
import sys

current_dir = Path(__file__).resolve().parent

# Risali alla directory root del progetto
project_root = current_dir.parent
print(f"project_root: {project_root}")

sys.path.append(str(project_root))

from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from backend.bigquery_connection import BigQueryConnection
from backend.firestore_connection import FirestoreConnection
from pipelines.fetch_chess_data.fetch_chess_data import ChessDataCollector

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
def get_top_players(game_type: str, category:str, limit: int = 10):
    """
    Esegue una query su Firestore e ritorna i giocatori con best_rating più alto
    in base al game_type indicato (es. 'chess_blitz', 'chess_bullet', 'chess_rapid').
    """
    results = firestore_conn.get_top_players(game_type, category, limit)

    if not results:
        return {"message": "Nessun risultato trovato per questo game_type"}
    
    return {
        "game_type": game_type,
        "top_players": results
    }
    
@app.get("/search")
def search_player(player_name: str, response: Response):
    """
    Cerca i dati di un giocatore in Firestore. Se non esiste, verifica se è presente su Chess.com.
    Se è su Chess.com, salva i dati in Firestore e restituiscili.
    Se non esiste né in Firestore né su Chess.com, restituisce un messaggio di errore.
    """
    collector = ChessDataCollector()

    # 1. Controlla in Firestore
    data = firestore_conn.get_user_data(player_name)
    if data:
        return {
            "username": player_name,
            "user_data": data
        }
    
    # 2. Se non esiste in Firestore, cerca su Chess.com
    status_code, profile = collector.get_player_profile(player_name)
    

    if status_code == 404:
        response.status_code = 404
        return {"message": f"Il giocatore '{player_name}' non è stato trovato su Chess.com"}

    if status_code != 200:
        response.status_code = status_code  # Altro errore HTTP ricevuto da Chess.com
        return {"message": f"Errore nel recupero del profilo per '{player_name}' (HTTP {status_code})"}

    # 3. L'utente esiste su Chess.com: recupera avatar e statistiche
    stats_data = collector.get_player_stats(player_name) or {}
    avatar_url = profile.get("avatar")
    stored_avatar_url = None

    if avatar_url:
        stored_avatar_url = collector.download_and_store_avatar(avatar_url, player_name)
    
    collector.save_to_firestore(
        player_name=player_name,
        stats_data=stats_data,
        profile_data=profile,
        stored_avatar_url=stored_avatar_url,
        category=profile.get("title", None)
    )
    
    # 5. Recupera i dati aggiornati da Firestore
    new_data = firestore_conn.get_user_data(player_name)
    
    response.status_code = 201
    return {
        "username": player_name,
        "user_data": new_data
    }

@app.get("/player-history/")
def get_player_history(
    player_name: str, 
    game_type: str, 
    start_date: str = "2025-03-01"
):
    """
    Recupera lo storico di un giocatore per un determinato game_type
    a partire da una data specificata (default: 1° marzo 2025).
    """
    bq_conn = BigQueryConnection()
    sql = """
        SELECT player_name, game_type, last_rating, best_rating, 
               best_game_url, win, loss, draw, timestamp
        FROM `chess-data-451709.chesscom.players_history`
        WHERE player_name = @player_name
        AND game_type = @game_type
        AND timestamp >= TIMESTAMP(@start_date)
        ORDER BY timestamp ASC
    """
    
    params = {
        "player_name": player_name,
        "game_type": game_type,
        "start_date": start_date
    }
    
    print(f"query_ {sql}")
    print(f"params: {params}")
    results = bq_conn.execute_query(sql, params)
    
    if not results:
        return {"message": "Nessun risultato trovato per questo giocatore"}
    
    return {
        "player_name": player_name,
        "game_type": game_type,
        "history": results
    }