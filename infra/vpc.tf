resource "google_project_service" "feast-vpcaccess-api" {
  project = var.gcp_project
  service = "vpcaccess.googleapis.com"
}

module "feast-vpc-module" {
  # Somehow terraform can not delete this because of Cloud Run and/or Cloud Functions, if need to please go to the Cloud Run and
  # delete that first.
  # Ref: https://serverfault.com/a/1035138
  # Then run terraform state list to find the cloud run states and terraform state rm those states.
  # Ref: https://discuss.hashicorp.com/t/resource-manually-deleted-now-cant-destroy-plan-or-apply-due-to-it-missing-what-do/12215/3
  # Then if run into error like network resource is being used by routes then manually find the routes under VPC network console and
  # delete it.
  source       = "terraform-google-modules/network/google"
  version      = "~> 3.3.0"
  project_id   = var.gcp_project
  network_name = "feast-network"
  mtu          = 1460

  subnets = [
    {
      subnet_name   = "serverless-subnet"
      subnet_ip     = "10.10.10.0/28"
      subnet_region = var.gcp_location
    },
    {
      subnet_name   = "gke-subnet"
      subnet_ip     = "10.2.0.0/16"
      subnet_region = var.gcp_location
    }
  ]
}

module "feast-serverless-connector" {
  source     = "terraform-google-modules/network/google//modules/vpc-serverless-connector-beta"
  project_id = var.gcp_project
  vpc_connectors = [{
    name        = "central-serverless"
    region      = var.gcp_location
    subnet_name = module.feast-vpc-module.subnets["${var.gcp_location}/serverless-subnet"].name
    # host_project_id = var.host_project_id # Specify a host_project_id for shared VPC
    machine_type  = "e2-micro"
    min_instances = 2
    max_instances = 4
    }
    # Uncomment to specify an ip_cidr_range
    #   , {
    #     name          = "central-serverless2"
    #     region        = "us-central1"
    #     network       = module.feast-vpc-module.network_name
    #     ip_cidr_range = "10.10.11.0/28"
    #     subnet_name   = null
    #     machine_type  = "e2-standard-4"
    #     min_instances = 2
    #   max_instances = 7 }
  ]
  depends_on = [
    google_project_service.feast-vpcaccess-api
  ]
}
