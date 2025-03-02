
resource "google_storage_bucket" "terraform_state" {
  name     = "${var.project_id}-terraform-state-bucket"
  location = var.region

  versioning {
    enabled = true
  }

  lifecycle_rule {
    action {
      type = "Delete"
    }
    condition {
      age = 90
    }
  }

  storage_class = "STANDARD"
}

resource "google_storage_bucket" "chesscom-avatars" {
  name          = "${var.project_id}-chesscom-avatars"
  location      = var.region
  force_destroy = true # Imposta a true se vuoi consentire l'eliminazione del bucket anche se contiene oggetti

  storage_class = "STANDARD"

  versioning {
    enabled = false
  }

  uniform_bucket_level_access = true

  lifecycle_rule {
    condition {
      age = 365 
    }
    action {
      type = "Delete"
    }
  }

  retention_policy {
    is_locked        = false
    retention_period = 2592000  # 30 giorni in secondi
  }

  cors {
    origin          = ["*"]
    method          = ["GET", "HEAD", "OPTIONS"]
    response_header = ["Content-Type"]
    max_age_seconds = 3600
  }
}

resource "google_storage_bucket_iam_binding" "public_access" {
  bucket = google_storage_bucket.chesscom-avatars.name
  role   = "roles/storage.objectViewer"
  members = [
    "allUsers"
  ]
}

resource "google_project_iam_binding" "chess_vm_storage_admin" {
  project = var.project_id
  role    = "roles/storage.admin"

  members = [
    "serviceAccount:${google_service_account.chess_sa.email}"
  ]
}