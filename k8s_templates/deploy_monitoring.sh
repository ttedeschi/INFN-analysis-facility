kubectl apply -f htcondor-exporter.yaml
kubectl create namespace monitoring
kubectl create configmap prometheus-example-cm --from-file configs/prometheus.yml -n monitoring
kubectl apply -f prometheus.yaml
kubectl create configmap prometheus-adapter-example-cm --from-file configs/prometheus_adapter.yml
kubectl apply -f prometheus-adapter.yaml
