resource "google_service_account" "chess_sa" {
  account_id   = "backend"
  display_name = "Service Account for Chess VM"
}


resource "google_project_iam_binding" "chess_vm_logging" {
  project = var.project_id
  role    = "roles/logging.logWriter"

  members = [
    "serviceAccount:${google_service_account.chess_sa.email}"
  ]
}


resource "google_project_iam_binding" "chess_vm_firestore" {
  project = var.project_id
  role    = "roles/datastore.user"

  members = [
    "serviceAccount:${google_service_account.chess_sa.email}"
  ]
}

resource "google_project_iam_binding" "chess_vm_storage_viewer" {
  project = var.project_id
  role    = "roles/storage.objectViewer"

  members = [
    "serviceAccount:${google_service_account.chess_sa.email}"
  ]
}

resource "google_project_iam_binding" "chess_vm_bigquery" {
  project = var.project_id
  role    = "roles/bigquery.admin"

  members = [
    "serviceAccount:${google_service_account.chess_sa.email}"
  ]
}