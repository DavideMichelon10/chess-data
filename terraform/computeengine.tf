resource "google_storage_bucket" "script_bucket" {
  name          = "${var.project_id}-chess-scripts"
  location      = var.region
  force_destroy = true
  
  uniform_bucket_level_access = true
  
  lifecycle_rule {
    condition {
      age = 30
    }
    action {
      type = "Delete"
    }
  }
}

# Carica lo script nel bucket
resource "google_storage_bucket_object" "fetch_chess_data" {
  name   = "fetch_chess_data.py"
  bucket = google_storage_bucket.script_bucket.name
  source = "../pipelines/fetch_chess_data/fetch_chess_data.py"
}

resource "google_storage_bucket_object" "copy_firestore_to_bigquery" {
  name   = "copy_firestore_to_bigquery.py"
  bucket = google_storage_bucket.script_bucket.name
  source = "../pipelines/fetch_chess_data/copy_firestore_to_bigquery.py"
}

resource "google_service_account" "chess_sa" {
  account_id   = "chess-fetch-sa"
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

resource "google_project_iam_binding" "chess_vm_compute" {
  project = var.project_id
  role    = "roles/compute.instanceAdmin.v1"

  members = [
    "serviceAccount:${google_service_account.chess_sa.email}"
  ]
}


# Permessi per accesso al bucket
resource "google_storage_bucket_iam_binding" "script_bucket_access" {
  bucket = google_storage_bucket.script_bucket.name
  role   = "roles/storage.objectUser"
  
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
  role    = "roles/bigquery.dataEditor"  # Permette di scrivere dati nelle tabelle di BigQuery

  members = [
    "serviceAccount:${google_service_account.chess_sa.email}"
  ]
}

resource "google_project_iam_binding" "chess_vm_bigquery_metadata" {
  project = var.project_id
  role    = "roles/bigquery.metadataViewer"  # Permette di leggere la struttura del dataset

  members = [
    "serviceAccount:${google_service_account.chess_sa.email}"
  ]
}

# VM per eseguire lo script
resource "google_compute_instance" "chess_vm" {
  name         = "chess-fetch-vm"
  machine_type = "e2-micro"
  zone         = "${var.region}-a"

  # Disabilitare la VM all'inizio, sarà avviata dallo scheduler
  desired_status = "TERMINATED"

  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-11"
      size  = 10  # GB
      type  = "pd-standard"
    }
  }

  network_interface {
    network = "default"
    access_config {
      # Ephemeral IP
    }
  }

  service_account {
    email  = google_service_account.chess_sa.email
    scopes = ["cloud-platform"]
  }

  depends_on = [
    google_storage_bucket_object.fetch_chess_data, google_storage_bucket_object.copy_firestore_to_bigquery
  ]
  
  metadata_startup_script = <<EOT
  #!/bin/bash
  set -e

  # Registrazione dell'inizio
  echo "Script di avvio iniziato: $(date)" | tee /tmp/chess_startup.log
  sudo dpkg --configure -a || echo "Nessun problema con dpkg"
  # Installa dipendenze
  sudo apt update && sudo apt install -y python3 python3-pip
  pip3 install --upgrade google-cloud-bigquery google-cloud-firestore google-cloud-logging google-cloud-storage requests

  # Crea directory per i log
  mkdir -p /tmp/chess_logs

  # Usa il nome hardcoded del bucket
  BUCKET_NAME="${var.project_id}-chess-scripts"
  echo "Accesso al bucket: $BUCKET_NAME" | tee -a /tmp/chess_startup.log


  gsutil cp gs://$BUCKET_NAME/fetch_chess_data.py /tmp/fetch_chess_data.py
  python3 /tmp/fetch_chess_data.py
  gsutil cp gs://$BUCKET_NAME/copy_firestore_to_bigquery.py /tmp/copy_firestore_to_bigquery.py
  python3 /tmp/copy_firestore_to_bigquery.py

  # Notifica completamento
  echo "Esecuzione completata, spegnimento VM: $(date)" | tee -a /tmp/chess_startup.log
  sync

  # Spegni la VM dopo l'esecuzione
  shutdown -h now
  EOT

  lifecycle {
    ignore_changes = [metadata_startup_script]
  }

  # Tags per firewall e networking
  tags = ["chess-data-vm"]
}

# Scheduler per avviare la VM ogni giorno
resource "google_cloud_scheduler_job" "start_vm" {
  name        = "start-chess-fetch-vm"
  description = "Start the VM to fetch chess data daily"
  schedule    = "26 12 * * *"  # Ogni giorno alle 3:00 UTC
  time_zone   = "UTC"

  http_target {
    uri         = "https://www.googleapis.com/compute/v1/projects/${var.project_id}/zones/${var.region}-a/instances/chess-fetch-vm/start"
    http_method = "POST"
    oauth_token {
      service_account_email = google_service_account.chess_sa.email
    }
  }
}
