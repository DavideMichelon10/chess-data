from google.cloud import bigquery, firestore, logging as cloud_logging

# Inizializzazione dei client
bq_client = bigquery.Client()
db = firestore.Client()
logging_client = cloud_logging.Client()
logger = logging_client.logger('chess_data_collector')

# Configurazione BigQuery
BQ_PROJECT = "chess-data-451709"
BQ_DATASET = "chesscom"
BQ_TABLE = "players_history"

def copy_firestore_to_bigquery():
    """Copia i dati da Firestore a BigQuery creando un record per ogni game_type."""
    try:
        logger.log_text("Avvio della copia Firestore → BigQuery", severity="INFO")

        collection_ref = db.collection("users")
        docs = collection_ref.stream()

        rows_to_insert = []
        for doc in docs:
            doc_data = doc.to_dict()
            player_name = doc.id
            
            timestamp = doc_data.get("timestamp", None)
            
            for game_type, stats in doc_data.items():
                if isinstance(stats, dict) and "last_rating" in stats:
                    row = {
                        "player_name": player_name,
                        "game_type": game_type,
                        "last_rating": stats["last_rating"],
                        "best_rating": stats.get("best_rating", None),
                        "best_game_url": stats.get("best_game_url", None),
                        "win": stats.get("win", 0),
                        "loss": stats.get("loss", 0),
                        "draw": stats.get("draw", 0),
                        "timestamp": timestamp
                    }
                    rows_to_insert.append(row)

        if rows_to_insert:
            # Inserisce i dati in BigQuery
            table_ref = bq_client.dataset(BQ_DATASET).table(BQ_TABLE)
            print(f"table_ref {table_ref}")
            errors = bq_client.insert_rows_json(table_ref, rows_to_insert)
            if errors:
                logger.log_text(f"Errore nell'inserimento in BigQuery: {errors}", severity="ERROR")
            else:
                logger.log_text(f"Dati copiati con successo in BigQuery: {len(rows_to_insert)} record", severity="INFO")
        else:
            logger.log_text("Nessun dato da copiare in BigQuery.", severity="WARNING")

    except Exception as e:
        logger.log_text(f"Errore nella copia Firestore → BigQuery: {str(e)}", severity="ERROR")
        raise

if __name__ == "__main__":
    copy_firestore_to_bigquery()
