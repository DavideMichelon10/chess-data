resource "google_bigquery_dataset" "chesscom" {
  dataset_id    = "chesscom"
  friendly_name = "chesscom"
  description   = "Dataset per salvare le statistiche di Chess.com"
  location      = var.region

  lifecycle {
    prevent_destroy = false
  }
}

# Tabella per salvare le partite di Chess.com
resource "google_bigquery_table" "chess_games" {
  dataset_id = google_bigquery_dataset.chesscom.dataset_id
  table_id   = "chess_games"
  time_partitioning {
    type = "DAY"
    field = "end_time"  # Partizionamento sulla data di fine partita
  }
  clustering = ["user_id"]  # Clustering su user_id per query più rapide
    schema = <<EOF
    [
      {"name": "game_id", "type": "STRING", "mode": "REQUIRED"},
      {"name": "user_id", "type": "STRING", "mode": "NULLABLE"},
      {"name": "white_player", "type": "STRING", "mode": "NULLABLE"},
      {"name": "black_player", "type": "STRING", "mode": "NULLABLE"},
      {"name": "rating_white", "type": "INTEGER", "mode": "NULLABLE"},
      {"name": "rating_black", "type": "INTEGER", "mode": "NULLABLE"},
      {"name": "result_white", "type": "STRING", "mode": "NULLABLE"},
      {"name": "result_black", "type": "STRING", "mode": "NULLABLE"},
      {"name": "accuracy_white", "type": "FLOAT", "mode": "NULLABLE"},
      {"name": "accuracy_black", "type": "FLOAT", "mode": "NULLABLE"},
      {"name": "time_control", "type": "STRING", "mode": "NULLABLE"},
      {"name": "time_class", "type": "STRING", "mode": "NULLABLE"},
      {"name": "end_time", "type": "TIMESTAMP", "mode": "REQUIRED"},
      {"name": "moves", "type": "STRING", "mode": "NULLABLE"},
      {"name": "eco", "type": "STRING", "mode": "NULLABLE"},
      {"name": "url", "type": "STRING", "mode": "NULLABLE"}
    ]
  EOF


  deletion_protection = false
}