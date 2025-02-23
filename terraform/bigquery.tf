resource "google_bigquery_dataset" "chess_data" {
  dataset_id    = "chess_data"
  friendly_name = "Chess Data"
  description   = "Dataset per salvare le statistiche di Chess.com"
  location      = "US"

  lifecycle {
    prevent_destroy = true
  }
}

resource "google_bigquery_table" "chess_stats" {
  dataset_id = google_bigquery_dataset.chess_data.dataset_id
  table_id   = "chess_stats"

  schema = <<EOF
    [
    {"name": "player_name", "type": "STRING", "mode": "NULLABLE"},
    {"name": "game_type", "type": "STRING", "mode": "NULLABLE"},
    {"name": "last_rating", "type": "INTEGER", "mode": "NULLABLE"},
    {"name": "best_rating", "type": "INTEGER", "mode": "NULLABLE"},
    {"name": "best_game_url", "type": "STRING", "mode": "NULLABLE"},
    {"name": "win", "type": "INTEGER", "mode": "NULLABLE"},
    {"name": "loss", "type": "INTEGER", "mode": "NULLABLE"},
    {"name": "draw", "type": "INTEGER", "mode": "NULLABLE"},
    {"name": "timestamp", "type": "TIMESTAMP", "mode": "NULLABLE"}
    ]
    EOF

  deletion_protection = false
}