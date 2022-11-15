output "project_name" {
  value = var.project_name
}
output "project_bucket" {
  value = google_storage_bucket.feast_bucket.url
}

output "cloud_run_url" {
  value = google_cloud_run_service.feast_repo.status[*].url
}

output "redis_host" {
  description = "The IP address of the Memorystore Redis instance"
  value       = google_redis_instance.feast_memorystore_redis_instance.host
}

output "vpc_subnet_name" {
  value       = module.feast-vpc-module.subnets["${var.gcp_location}/serverless-subnet"].name
  description = "VPC Subnet name"
}

output "kubernetes_cluster_name" {
  value       = google_container_cluster.primary.name
  description = "GKE Cluster Name"
}

output "kubernetes_cluster_host" {
  value       = google_container_cluster.primary.endpoint
  description = "GKE Cluster Host"
}
