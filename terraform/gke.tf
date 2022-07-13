variable "gke_username" {
  default     = ""
  description = "gke username"
}

variable "gke_password" {
  default     = ""
  description = "gke password"
}

variable "gke_num_nodes" {
  default     = 1
  description = "number of gke nodes"
}

variable "gke_machine_type" {
  default     = "n1-standard-4"
  description = "GKE nodes type"
}

variable "master_ipv4_cidr_block" {
  default     = ""
  description = "master network block"
}

variable "pods_ipv4_cidr_block" {
  default     = ""
  description = "pods network block"
}

variable "services_ipv4_cidr_block" {
  default     = ""
  description = "services network block"
}

# GKE cluster
resource "google_container_cluster" "primary" {
  name     = "${var.project_id}-gke"
  location = var.region

  remove_default_node_pool = true
  initial_node_count       = 1

  network    = google_compute_network.vpc.name
  subnetwork = google_compute_subnetwork.subnet.name

  maintenance_policy {
    daily_maintenance_window {
      start_time = "02:00"
    }
  }

  network_policy {
    provider = "CALICO"
    enabled  = true
  }

  addons_config {
    network_policy_config {
      disabled = false
    }
  }

  ip_allocation_policy {
    cluster_ipv4_cidr_block = var.pods_ipv4_cidr_block
    services_ipv4_cidr_block = var.services_ipv4_cidr_block
  }

    private_cluster_config {
    enable_private_endpoint = false
    enable_private_nodes    = true
    master_ipv4_cidr_block  = var.master_ipv4_cidr_block
  }

  dns_config {
      cluster_dns        = "CLOUD_DNS"
      cluster_dns_scope  = "VPC_SCOPE"
      cluster_dns_domain = "${var.project_id}-gke"
    }

}

# Separately Managed Node Pool
resource "google_container_node_pool" "primary_nodes" {
  name       = "${google_container_cluster.primary.name}-node-pool"
  location   = var.region
  cluster    = google_container_cluster.primary.name
  node_count = var.gke_num_nodes

  node_config {
    oauth_scopes = [
      "https://www.googleapis.com/auth/logging.write",
      "https://www.googleapis.com/auth/monitoring",
    ]

    preemptible  = true
    machine_type = var.gke_machine_type

    labels = {
      env = var.project_id
    }

    tags         = ["gke-node", "${var.project_id}-gke"]
  }
}
