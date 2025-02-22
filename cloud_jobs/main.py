import requests
import datetime
import os
from google.cloud import bigquery

# Creazione del client BigQuery
client = bigquery.Client()

# Leggi i dataset e la tabella da variabili d'ambiente (configurate in Terraform)
DATASET_ID = os.getenv("DATASET_ID", "chess_data")
TABLE_ID = os.getenv("TABLE_ID", "chess_stats")

# Lista dei giocatori da monitorare
PLAYERS = ["magnuscarlsen", "davideblunder", "hikaru", "ImNoob66"]

# Headers per la richiesta API
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def fetch_chess_data():
    """Funzione principale per recuperare i dati dei giocatori e salvarli su BigQuery."""
    for player in PLAYERS:
        try:
            url = f"https://api.chess.com/pub/player/{player}/stats"
            response = requests.get(url, headers=HEADERS)

            if response.status_code == 200:
                data = response.json()
                print(f"Dati ricevuti per {player}: {data}")

                # Salva i dati su BigQuery
                save_to_bigquery(player, data)

            else:
                print(f"Errore API per {player} {response.status_code}: {response.text}")

        except Exception as e:
            print(f"Errore durante la richiesta API per {player}: {str(e)}")

    print("Dati salvati con successo per tutti i giocatori.")

def save_to_bigquery(player_name, data):
    """Salva i dati della partita su BigQuery"""
    rows_to_insert = []
    timestamp = datetime.datetime.utcnow().isoformat()

    # Estrarre statistiche da ogni modalità di gioco
    for game_type, stats in data.items():
        if isinstance(stats, dict) and "last" in stats and "record" in stats:
            row = {
                "player_name": player_name,
                "game_type": game_type,
                "last_rating": stats["last"]["rating"],
                "best_rating": stats["best"]["rating"] if "best" in stats else None,
                "best_game_url": stats["best"]["game"] if "best" in stats else None,
                "win": stats["record"]["win"],
                "loss": stats["record"]["loss"],
                "draw": stats["record"]["draw"],
                "timestamp": timestamp
            }
            rows_to_insert.append(row)

    if rows_to_insert:
        table_ref = client.dataset(DATASET_ID).table(TABLE_ID)
        errors = client.insert_rows_json(table_ref, rows_to_insert)

        if errors:
            print(f"Errore durante l'inserimento in BigQuery per {player_name}: {errors}")
        else:
            print(f"Dati inseriti con successo in BigQuery per {player_name}")

if __name__ == "__main__":
    fetch_chess_data()