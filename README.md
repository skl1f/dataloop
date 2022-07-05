# dataloop

1. docker build --platform linux/amd64 -t europe-west1-docker.pkg.dev/ordinal-torch-327414/dataloop/server:latest .
2. terraform apply
3. docker push europe-west1-docker.pkg.dev/ordinal-torch-327414/dataloop/server:latest
4. kubectl apply -f ./kubernetes/namespaces.yaml
5. kubectl create secret docker-registry artifact-registry \
--docker-server=https://europe-west1-docker.pkg.dev \
--docker-email=service-artifacts-pull@ordinal-torch-327414.iam.gserviceaccount.com \
--docker-username=_json_key \
--docker-password="$(cat ordinal-torch-327414-f860f0dc2e2c.json)" \
--namespace services
6. kubectl apply -f ./kubernetes/artifact-registry-access.yaml 
7. kubectl apply -f ./kubernetes/services.yaml 
8. kubectl apply -f ./kubernetes/frontend.yaml 
9. kubectl apply -f ./kubernetes/grafana.yaml
10. kubectl apply -f ./kubernetes/prometheus.yaml