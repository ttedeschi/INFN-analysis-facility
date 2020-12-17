# INFN-analysis-facility
This repo contains all information and recipes to set up an Analysis Facility on INFN infrastructure. The scheme of the Analysis Facility is the following

![alt text](AnalysisFacility_OSG_2.png)

## Quick Start
Setup oidc-agent for DODAS-IAM: https://dodas-ts.github.io/dodas-apps/setup-oidc/

``` dodas create TOSCA_templates/jupyterhub.yaml ```

### Setup htcondor
```
helm repo add longhorn https://charts.longhorn.io
helm repo update
kubectl create namespace longhorn-system
helm install longhorn longhorn/longhorn --namespace longhorn-system --kubeconfig /etc/kubernetes/admin.conf
kubectl create namespace cert-manager
helm repo add jetstack https://charts.jetstack.io
helm repo update
helm install cert-manager jetstack/cert-manager --namespace cert-manager --version v1.1.0 --set installCRDs=true --kubeconfig /etc/kubernetes/admin.conf
```
After substituting <k8s master public ip> with the real value inside ```k8s_templates/htcondor.yaml```,
```
kubectl apply -f k8s_templates/htcondor.yaml
```


