# INFN-analysis-facility
This repo contains all information and recipes to set up an Analysis Facility on INFN infrastructure. The scheme of the Analysis Facility is the following

![alt text](AnalysisFacility_OSG_2.png)

## Quick Start
Setup oidc-agent for DODAS-IAM: https://dodas-ts.github.io/dodas-apps/setup-oidc/

### Setup Jupyterhub
``` 
dodas create TOSCA_templates/jupyterhub.yaml 
```
After login:
``` kubectl -n kube-system edit daemonset kube-flannel-ds-amd64``` putting ``` --iface-regex=172\.30\.X\.*``` into container args where x is the third component of k8s master internal IP
```
helm repo add dodas https://dodas-ts.github.io/helm_charts
helm repo update
```
then subsitute in ```values/jupyterhub.yaml``` k8s master public IP and 
```
helm install  dodas/jupyterhub --values jupyterhub-value.yaml --generate-name --kubeconfig /etc/kubernetes/admin.conf
```
Then 
```
kubectl edit deployment hub
```
and substitute infn-cloud website with ```https://dodas-iam.cloud.cnaf.infn.it```

### Setup htcondor
``` 
dodas create TOSCA_templates/htcondor.yaml
```

After login:
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

### Setup htcondor client
```
kubectl exec schedd-pod-<pod name here> cat /etc/certs/ca.crt
```
Try remote submission:
```
echo "YOUR CA CERT" > /ca.crt
export _condor_AUTH_SSL_CLIENT_CAFILE=/ca.crt
export _condor_SEC_DEFAULT_AUTHENTICATION_METHODS=SCITOKENS
export _condor_SCITOKENS_FILE=/tmp/token                          # token from CMS-IAM
export _condor_COLLECTOR_HOST=<public IP>:30618
export _condor_SCHEDD_HOST=schedd.condor.svc.cluster.local
export _condor_TOOL_DEBUG=D_FULLDEBUG,D_SECURITY
```

### Machine Learning
From Root to Pandas/Numpy
```
import uproot
file = uproot.open("example.root")
tree = file["events"]
df = tree.arrays(["var1","var2"], library="pd")               # Pandas DataFrame
np_dict = tree.arrays(["var1","var2"], library="np")          # Dictionary of Numpy arrays 
```

