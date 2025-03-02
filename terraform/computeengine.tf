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
resource "google_storage_bucket_object" "script" {
  name   = "fetch_chess_data.py"
  bucket = google_storage_bucket.script_bucket.name
  source = "../pipelines/fetch_chess_data/fetch_chess_data.py"
}

# Service account per la VM
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
    google_storage_bucket_object.script
  ]
  
  metadata_startup_script = <<EOT
  #!/bin/bash
  set -e

  # Registrazione dell'inizio
  echo "Script di avvio iniziato: $(date)" | tee /tmp/chess_startup.log

  # Installa dipendenze
  sudo apt update && sudo apt install -y python3 python3-pip
  pip3 install google-cloud-firestore requests google-cloud-logging


  # Crea directory per i log
  mkdir -p /tmp/chess_logs

  # Usa il nome hardcoded del bucket
  BUCKET_NAME="${var.project_id}-chess-scripts"
  echo "Accesso al bucket: $BUCKET_NAME" | tee -a /tmp/chess_startup.log

  # Elenca i contenuti del bucket per debugging
  gsutil ls gs://$BUCKET_NAME/ | tee -a /tmp/chess_startup.log

  # Scarica lo script dal bucket
  gsutil cp gs://$BUCKET_NAME/fetch_chess_data.py /tmp/fetch_chess_data.py
  python3 /tmp/fetch_chess_data.py
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
  schedule    = "0 3 * * *"  # Ogni giorno alle 3:00 UTC
  time_zone   = "UTC"

  http_target {
    uri         = "https://www.googleapis.com/compute/v1/projects/${var.project_id}/zones/${var.region}-a/instances/chess-fetch-vm/start"
    http_method = "POST"
    oauth_token {
      service_account_email = google_service_account.chess_sa.email
    }
  }
}

# Output utili
output "script_bucket_name" {
  description = "Nome del bucket che contiene lo script e i log"
  value       = google_storage_bucket.script_bucket.name
}

output "vm_name" {
  description = "Nome della VM principale"
  value       = google_compute_instance.chess_vm.name
}

output "vm_zone" {
  description = "Zona della VM principale"
  value       = google_compute_instance.chess_vm.zone
}