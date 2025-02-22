provider "google" {
  project = "chess-data-451709"
  region  = "us-central1"
}

variable "project_id" {
  description = "Project ID di Google Cloud"
  type        = string
  default     = "chess-data-451709"
}

resource "google_project_service" "cloud_functions" {
  service = "cloudfunctions.googleapis.com"
}

resource "google_project_service" "cloud_run" {
  service = "run.googleapis.com"
}

resource "google_project_service" "cloud_storage" {
  service = "storage.googleapis.com"
}

resource "google_project_service" "scheduler" {
  service = "cloudscheduler.googleapis.com"
}

# 🔹 Bucket per caricare il codice della funzione
resource "google_storage_bucket" "function_bucket" {
  name          = "${var.project_id}-function-bucket"
  location      = "US"
  force_destroy = true
}


# 🔹 Pub/Sub topic per attivare la funzione
resource "google_pubsub_topic" "chess_data_topic" {
  name = "chess-data-topic"
}

# 🔹 Creazione del dataset BigQuery
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

# 🔹 Cloud Run Job per eseguire il fetch dei dati
resource "google_cloud_run_v2_job" "fetch_chess_data" {
  name     = "fetch-chess-data"
  location = "us-central1"

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

# 🔹 Cloud Scheduler per avviare il job ogni 6 ore
resource "google_cloud_scheduler_job" "chess_job" {
  name        = "chess-fetch-job"
  description = "Esegue il job Cloud Run ogni 6 ore"
  schedule = "0 */6 * * *"
  time_zone   = "UTC"
  region      = "us-central1"

  http_target {
    uri         = "https://us-central1-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/${var.project_id}/jobs/fetch-chess-data:run"
    http_method = "POST"

    oauth_token {
      service_account_email = "scheduler-sa@chess-data-451709.iam.gserviceaccount.com"
    }
  }
}