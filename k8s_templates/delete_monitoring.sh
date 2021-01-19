kubectl delete -f manifests_no_configs/exporter.yaml
kubectl delete configmap prometheus-example-cm -n monitoring
kubectl delete -f manifests_no_configs/prometheus.yaml
kubectl delete configmap prometheus-adapter-example-cm 
kubectl delete -f manifests_no_configs/prometheus_adapter.yaml 
