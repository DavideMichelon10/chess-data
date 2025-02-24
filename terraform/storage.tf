
resource "google_storage_bucket" "function_bucket" {
  name          = "${var.project_id}-function-bucket"
  location      = "US"
  force_destroy = true
}

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
