# Abilita le API necessarie per il progetto

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

resource "google_project_service" "pubsub" {
  service = "pubsub.googleapis.com"
}

resource "google_project_service" "bigquery" {
  service = "bigquery.googleapis.com"
}