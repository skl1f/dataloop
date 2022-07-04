variable "bastion_zone" {
  default     = ""
  description = "zone where to place bastion host"
}

variable "bastion_allowed_sources" {
  default     = ""
  description = "CIDR range to allow ssh connection to bastion"
}

// Dedicated service account for the Bastion instance.
resource "google_service_account" "bastion" {
  account_id   = "${var.project_id}-bastion"
  display_name = "GKE Bastion Service Account"
}

// Allow access to the Bastion Host via SSH.
resource "google_compute_firewall" "bastion-ssh" {
  name          = "${var.project_id}-bastion-ssh"
  network       = google_compute_network.vpc.name
  direction     = "INGRESS"
  project       = var.project_id
  source_ranges = ["0.0.0.0/0"]

  allow {
    protocol = "tcp"
    ports    = ["22"]
  }

  target_tags = ["bastion"]
}

// The Bastion host.
resource "google_compute_instance" "bastion" {
  name         = "${var.project_id}-bastion"
  machine_type = "e2-micro"
  zone         = var.bastion_zone
  project      = var.project_id
  tags         = ["bastion"]

  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-10"
    }
  }

  shielded_instance_config {
    enable_secure_boot          = true
    enable_vtpm                 = true
    enable_integrity_monitoring = true
  }

  network_interface {
    subnetwork = google_compute_subnetwork.subnet.name


    access_config {
      // Not setting "nat_ip", use an ephemeral external IP.
      network_tier = "STANDARD"
    }
  }

  // Allow the instance to be stopped by Terraform when updating configuration.
  allow_stopping_for_update = true

  service_account {
    email  = google_service_account.bastion.email
    scopes = ["cloud-platform"]
  }

  scheduling {
    preemptible       = true
    automatic_restart = false
  }
}