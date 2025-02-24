resource "google_cloud_scheduler_job" "chess_job" {
  name        = "chess-fetch-job"
  description = "Esegue il job Cloud Run ogni 6 ore"
  schedule = "0 */6 * * *"
  time_zone   = "UTC"
  region      = var.region

  http_target {
    uri         = "https://${var.region}-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/${var.project_id}/jobs/fetch-chess-data:run"
    http_method = "POST"

    oauth_token {
      service_account_email = "scheduler-sa@chess-data-451709.iam.gserviceaccount.com"
    }
  }
}

resource "google_cloud_scheduler_job" "fetch_users" {
  name        = "fetch-users-job"
  description = ""
  schedule = "30 */6 * * *"
  time_zone   = "UTC"
  region      = var.region

  http_target {
    uri         = "https://${var.region}-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/${var.project_id}/jobs/fetch-chess-users:run"
    http_method = "POST"

    oauth_token {
      service_account_email = "scheduler-sa@chess-data-451709.iam.gserviceaccount.com"
    }
  }
}