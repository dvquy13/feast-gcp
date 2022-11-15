variable "project_name" {
  type        = string
  description = "The project identifier is used to uniquely namespace resources"
  default     = "feast-gcp-project-id"
}

variable "gcp_project" {
  type        = string
  description = "The GCP project id"
  default     = "feast-gcp-project-id"
}

variable "gcp_location" {
  type        = string
  description = "The GCP location"
  default     = "asia-southeast1"
}

variable "gcp_zone" {
  type        = string
  description = "The zone for Kubernetes since there's error when creating the node pool at asia-southeast1-a"
  default     = "asia-southeast1-b"
}

variable "service_account" {
  type        = string
  description = "The main Service Account"
  # This SA needs to be created manually before the project with the appropriate roles
  # For temporary it can be editor and roles/cloudfunctions.admin
  default = "feast-sa@feast-gcp-project-id.iam.gserviceaccount.com"
}

variable "main_image_version" {
  type        = string
  description = "The version of the main Docker image"
  default     = "0.3.0"
}

variable "cloud_run_env" {
  type        = string
  description = "Value of the environment variable `env` inside Cloud Run"
}
