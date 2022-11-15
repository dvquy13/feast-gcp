resource "google_redis_instance" "feast_memorystore_redis_instance" {
  name               = "feast-memorystore"
  tier               = "BASIC"
  memory_size_gb     = 2
  region             = var.gcp_location
  redis_version      = "REDIS_6_X"
  display_name       = "Feast Online Store"
  authorized_network = module.feast-vpc-module.network_name

  depends_on = [
    module.feast-vpc-module
  ]
}
