# dataloop

1. docker build --platform linux/amd64 -t europe-west1-docker.pkg.dev/ordinal-torch-327414/dataloop/server:latest .
2. terraform apply
3. docker push europe-west1-docker.pkg.dev/ordinal-torch-327414/dataloop/server:latest
4. kubectl create secret docker-registry artifact-registry \
--docker-server=https://europe-west1-docker.pkg.dev \
--docker-email=SERVICE-ACCOUNT-EMAIL \
--docker-username=_json_key \
--docker-password="$(cat service_account_key.json)" \
--namespace services
5. kubectl apply -f ./kubernetes/namespaces.yaml
6. kubectl apply -f ./kubernetes/artifact-registry-access.yaml 
7. kubectl apply -f ./kubernetes/services.yaml 