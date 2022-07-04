variable "project_id" {
  description = "project id"
}

variable "region" {
  description = "region"
}

variable "compute_ip_cidr_range" {
  description = "compute subnet"
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# VPC
resource "google_compute_network" "vpc" {
  name                    = "${var.project_id}-vpc"
  auto_create_subnetworks = "false"
}

# Subnet
resource "google_compute_subnetwork" "subnet" {
  name                      = "${var.project_id}-subnet"
  region                    = var.region
  network                   = google_compute_network.vpc.name
  private_ip_google_access  = true
  ip_cidr_range             = var.compute_ip_cidr_range

  log_config {
    aggregation_interval = "INTERVAL_10_MIN"
    flow_sampling        = 0.5
    metadata             = "INCLUDE_ALL_METADATA"
  }
}

# Router
resource "google_compute_router" "router" {
  name    = "${var.project_id}-router"
  region  = google_compute_subnetwork.subnet.region
  network = google_compute_network.vpc.id
}

# Static IP
resource "google_compute_address" "address" {
  count  = 3
  name   = "${var.project_id}-nat-ip-${count.index}"
  region = google_compute_subnetwork.subnet.region
}

# Cloud NAT
resource "google_compute_router_nat" "nat_manual" {
  name   = "${var.project_id}-router-nat"
  router = google_compute_router.router.name
  region = google_compute_router.router.region

  nat_ip_allocate_option = "MANUAL_ONLY"
  nat_ips                = google_compute_address.address.*.self_link

  source_subnetwork_ip_ranges_to_nat = "LIST_OF_SUBNETWORKS"
  subnetwork {
    name                    = google_compute_subnetwork.subnet.id
    source_ip_ranges_to_nat = ["ALL_IP_RANGES"]
  }
}