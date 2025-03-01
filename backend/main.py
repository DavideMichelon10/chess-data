from fastapi import FastAPI, HTTPException, Query
from bigquery_connection import BigQueryConnection
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],  
)

def fetch_query_results(query: str, params: dict = None):
    """
    Funzione generica per eseguire query su BigQuery
    """
    try:
        print(f"fetchimg...")
        results = BigQueryConnection().execute_query(query, params)
        print(f"get data: {results}")
        return results
    except Exception as e:
        print(f"excetion: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/search/")
def search_player(player_name: str = Query(..., title="Nome del giocatore")):
    query = """
        WITH ranked_data AS (
            SELECT 
                player_name,
                game_type,
                last_rating,
                best_rating,
                timestamp,
                ROW_NUMBER() OVER (PARTITION BY player_name, game_type ORDER BY timestamp DESC) AS rank
            FROM `chess-data-451709.chess_data.chess_stats`
            WHERE player_name = @player_name
        )
        SELECT player_name, game_type, last_rating, best_rating
        FROM ranked_data
        WHERE rank = 1;
    """
    params = {"player_name": player_name}
    results = fetch_query_results(query, params)

    if not results:
        return {"message": "Nessun risultato trovato per questo giocatore"}

    return {"player_name": player_name, "stats": results}

@app.get("/top-players/")
def get_top_players(game_type: str, limit: int = 10):
    print(f"DEBUG: game_type={game_type}")
    query = """
        SELECT player_name, game_type, MAX(best_rating) AS best_rating
        FROM `chess-data-451709.chess_data.chess_stats`
        WHERE game_type = @game_type
        GROUP BY player_name, game_type
        ORDER BY best_rating DESC
        LIMIT 100;
    """
    params = {"game_type": game_type, "limit": limit}
    results = fetch_query_results(query, params)

    if not results:
        return {"message": "Nessun risultato trovato per questo game_type"}
    print(f"res: {results}")
    return {"game_type": game_type, "top_players": results}