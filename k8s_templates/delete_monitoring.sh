kubectl delete -f htcondor-exporter.yaml
kubectl delete configmap prometheus-example-cm -n monitoring
kubectl delete -f prometheus.yaml
kubectl delete configmap prometheus-adapter-example-cm 
kubectl delete -f prometheus_adapter.yaml 
