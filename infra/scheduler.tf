resource "google_cloud_scheduler_job" "feast_materializer_daily" {
  name        = "feast_materializer_daily"
  description = ""
  schedule    = "30 5 * * *"
  time_zone   = "Asia/Singapore"

  retry_config {
    retry_count = 1
  }

  http_target {
    http_method = "GET"
    uri         = "${one(google_cloud_run_service.feast_repo.status[*].url)}/feast/materialize?start_ts=2022-09-13T00:00:00&end_ts=2022-09-16T00:00:00"
  }
}
