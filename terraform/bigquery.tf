resource "google_bigquery_dataset" "chesscom" {
  dataset_id    = "chesscom"
  friendly_name = "chesscom"
  description   = "Dataset per salvare le statistiche di Chess.com"
  location      = var.region

  lifecycle {
    prevent_destroy = false
  }
}

resource "google_bigquery_table" "players_history" {
  dataset_id = google_bigquery_dataset.chesscom.dataset_id
  table_id   = "players_history"
  time_partitioning {
    type = "DAY"
  }
  clustering = ["player_name"]  
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