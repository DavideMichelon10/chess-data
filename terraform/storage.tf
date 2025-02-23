
resource "google_storage_bucket" "function_bucket" {
  name          = "${var.project_id}-function-bucket"
  location      = "US"
  force_destroy = true
}