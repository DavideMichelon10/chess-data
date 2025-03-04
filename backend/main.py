from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from bigquery_connection import BigQueryConnection
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
def search_player(player_name: str):
    """
    Recupera i dati (tutti i campi) di un singolo giocatore da Firestore.
    Lo username coincide con l'ID del documento.
    """
    print("IN SEARCH")
    data = firestore_conn.get_user_data(player_name)
    if not data:
        return {"message": "Nessun risultato trovato per questo giocatore"}

    # Ritorniamo direttamente il doc, includendo anche lo username
    return {
        "username": player_name,
        "user_data": data
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