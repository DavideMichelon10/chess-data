resource "google_cloud_run_v2_job" "fetch_chess_data" {
  name     = "fetch-chess-data"
  location = var.region

  template {
    template {
      containers {
        image = "gcr.io/${var.project_id}/fetch-chess-data:latest"

        env {
          name  = "DATASET_ID"
          value = google_bigquery_dataset.chess_data.dataset_id
        }
        env {
          name  = "TABLE_ID"
          value = google_bigquery_table.chess_stats.table_id
        }
      }
    }
  }
}