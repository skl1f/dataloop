resource "google_artifact_registry_repository" "registry" {
  provider = google-beta
  project = var.project_id
  location = var.region
  repository_id = "dataloop"
  description = "docker repository"
  format = "DOCKER"
}