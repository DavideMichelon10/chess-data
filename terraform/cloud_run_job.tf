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

resource "google_cloud_run_v2_job" "fetch_chess_users" {
  name     = "fetch-chess-users"
  location = var.region

  template {

    template {
      containers {
        image = "gcr.io/${var.project_id}/fetch-chess-users:latest"

        env {
          name  = "INSTANCE_CONNECTION_NAME"
          value = "chess-data-451709:us-central1:instance"
        }

        env {
          name  = "DB_USER"
          value = module.cloudsql.db_user
        }

        env {
          name  = "DB_PASSWORD"
          value = module.cloudsql.db_password
        }

        env {
          name  = "DB_NAME"
          value = module.cloudsql.db_name
        }
        volume_mounts {
          name       = "cloudsql"
          mount_path = "/cloudsql"
        }
      }
      volumes {
        name = "cloudsql"
        cloud_sql_instance {
          instances = ["chess-data-451709:us-central1:instance"]
        }
      }
    }
  }
}
