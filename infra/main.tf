provider "google" {
  project = var.gcp_project
  region  = var.gcp_location
}

terraform {
  backend "gcs" {
    # Ref: https://cloud.google.com/docs/terraform/resource-management/store-state
    # This bucket needs to be created manually first before init
    bucket = "feast-gcp-feast"
    prefix = "terraform/state"
  }
}

resource "google_storage_bucket" "feast_bucket" {
  name          = "${var.project_name}-feast"
  force_destroy = true
  location      = var.gcp_location

  uniform_bucket_level_access = true
}
