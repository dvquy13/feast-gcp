resource "google_cloud_run_service" "feast_repo" {
  name     = "feast-gcp-cloud-run"
  location = var.gcp_location

  template {
    spec {
      containers {
        image = "asia.gcr.io/${var.gcp_project}/feast-gcp:${var.main_image_version}"
        env {
          name  = "ENV"
          value = var.cloud_run_env
        }
        resources {
          requests = {
            "cpu"    = "2"
            "memory" = "2G"
          }
          limits = {
            "cpu"    = "4"
            "memory" = "4G"
          }
        }
      }
      timeout_seconds      = 3600
      service_account_name = var.service_account
    }

    metadata {
      # Original reference: https://cloud.google.com/vpc/docs/configure-serverless-vpc-access#terraform_1
      # Below has modified some config so it looks different from original
      annotations = {
        # Limit scale up to prevent any cost blow outs!
        "autoscaling.knative.dev/maxScale" = "3"
        # Use the VPC Connector
        # The below original config does not work
        # "run.googleapis.com/vpc-access-connector" = google_vpc_access_connector.connector_beta.name
        # We need to get the connector_id by using the tolist() function
        # Ref: https://github.com/hashicorp/terraform-provider-azurerm/issues/16142
        "run.googleapis.com/vpc-access-connector" = tolist(module.feast-serverless-connector.connector_ids)[0]
        # Need to comment out the egress setting because if enabled it routes all traffic from cloud run to VPC
        # This makes the cloud run unable to access to GCS which is required to get the registry.pb file
        # all egress from the service should go through the VPC Connector
        # "run.googleapis.com/vpc-access-egress" = "all-traffic"
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }
}

data "google_iam_policy" "noauth" {
  binding {
    role = "roles/run.invoker"
    members = [
      "allUsers",
    ]
  }
}

resource "google_cloud_run_service_iam_policy" "noauth" {
  location = google_cloud_run_service.feast_repo.location
  project  = google_cloud_run_service.feast_repo.project
  service  = google_cloud_run_service.feast_repo.name

  policy_data = data.google_iam_policy.noauth.policy_data
}
