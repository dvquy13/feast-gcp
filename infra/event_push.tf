locals {
  function_name = "feast-gcp-event-push"
}

data "archive_file" "cloud_fn_code_archive" {
  type        = "zip"
  source_dir  = "../cloud_fn"
  output_path = "../dist/${local.function_name}.zip"
}

resource "google_storage_bucket_object" "cloud_fn_code_archive" {
  name   = "${local.function_name}.zip"
  bucket = google_storage_bucket.feast_bucket.name
  source = data.archive_file.cloud_fn_code_archive.output_path
}

resource "google_cloudfunctions_function" "cloud_fn_event_push" {
  name        = local.function_name
  description = "Cloud Functions to update Feature Store via PUSH service"
  runtime     = "python39"

  available_memory_mb           = 512
  timeout                       = 540
  source_archive_bucket         = google_storage_bucket.feast_bucket.name
  source_archive_object         = google_storage_bucket_object.cloud_fn_code_archive.name
  trigger_http                  = true
  entry_point                   = "feast_process_event"
  vpc_connector                 = tolist(module.feast-serverless-connector.connector_ids)[0]
  vpc_connector_egress_settings = "PRIVATE_RANGES_ONLY"
  environment_variables = {
    REDIS_HOST = google_redis_instance.feast_memorystore_redis_instance.host
  }

  lifecycle {
    replace_triggered_by = [
      # Redeploy cloud functions on changes in cloud_fn_code_archive
      google_storage_bucket_object.cloud_fn_code_archive
    ]
  }
}

# IAM entry for all users to invoke the function
resource "google_cloudfunctions_function_iam_member" "invoker" {
  project        = google_cloudfunctions_function.cloud_fn_event_push.project
  region         = google_cloudfunctions_function.cloud_fn_event_push.region
  cloud_function = google_cloudfunctions_function.cloud_fn_event_push.name

  role   = "roles/cloudfunctions.invoker"
  member = "allUsers"
}
