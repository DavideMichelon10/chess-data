
resource "google_service_account" "firestore_sa" {
  account_id   = "firestore-access"
  display_name = "Firestore Access Service Account"
}

# 2. Assegna il ruolo al Service Account (es. roles/datastore.user)
resource "google_project_iam_member" "firestore_sa_role" {
  project = var.project_id
  role    = "roles/datastore.user"
  member  = "serviceAccount:${google_service_account.firestore_sa.email}"
}