terraform {
  backend "gcs" {
    bucket  = "chess-data-451709-terraform-state-bucket"
    prefix  = "terraform/state"
  }
}