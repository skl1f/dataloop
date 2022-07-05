resource "google_artifact_registry_repository" "registry" {
  provider = google-beta
  project = var.project_id
  location = var.region
  repository_id = "dataloop"
  description = "docker repository"
  format = "DOCKER"
}

resource "google_service_account" "artifacts_pull" {
  account_id = "service-artifacts-pull"
  display_name = "Service Account for Pulling images from GCR"
}

resource "google_artifact_registry_repository_iam_member" "repo-iam" {
  provider = google-beta

  location = google_artifact_registry_repository.registry.location
  repository = google_artifact_registry_repository.registry.name
  role   = "roles/artifactregistry.reader"
  member =  "serviceAccount:${google_service_account.artifacts_pull.email}"
}