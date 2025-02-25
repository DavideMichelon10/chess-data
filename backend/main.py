from fastapi import FastAPI, HTTPException
from bigquery_connection import BigQueryConnection
app = FastAPI()
from fastapi.middleware.cors import CORSMiddleware


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],  
)
@app.get("/search/")
def search_player(player_name: str):
    print(f"in search_player")
    query = f"""
        WITH ranked_data AS (
            SELECT 
                player_name,
                game_type,
                last_rating,
                best_rating,
                timestamp,
                ROW_NUMBER() OVER (PARTITION BY player_name, game_type ORDER BY timestamp DESC) AS rank
            FROM `chess-data-451709.chess_data.chess_stats`
            WHERE player_name = '{player_name}'
        )
        SELECT player_name, game_type, last_rating, best_rating
        FROM ranked_data
        WHERE rank = 1;
    """

    try:
        results = BigQueryConnection().execute_query(query)

        if not results:
            return {"message": "Nessun risultato trovato per questo giocatore"}

        return {"player_name": player_name, "stats": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))