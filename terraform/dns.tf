resource "google_dns_managed_zone" "gcp-europe-west1" {
  name        = "gcp-europe-west1"
  dns_name    = "gcp-europe-west1.ukrgadget.com."
  description = "Regional DNS zone"
}