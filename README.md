# INFN-analysis-facility
This repo contains all information and recipes to set up an Analysis Facility on INFN infrastructure. The scheme of the Analysis Facility is the following: two Kubernetes clusters deployed via DODAS, one for Jupyterhub deployment and the second one for HTCondor batch system. 

![alt text](AnalysisFacility_OSG_2.png)

## User Guide
As a user of the analysis facility, you would like to both get access directly to the HTCondor cluster and to a Jupyter Notebook (which in turn can be used to submit jobs to HTCondor via Dask).

### Access to Jupyter Notebook
In order to get a Jupyter Notebook, you first have to apply for a Dodas-IAM account at https://dodas-iam.cloud.cnaf.infn.it/. Once you receive notification of account creation, you are good to go.

Go to http://90.147.75.37:30888/ and authenticate via Dodas-IAM, choosing the resources that will be assigned to your notebook. Once you have done this, you will be able to run multiple Jupyter notebooks, where you can perform your analysis or that you can use to submit jobs to HTCondor.

### Direct access to HTCondor via client
In order to get access directly to the HTCondor cluster, you should first apply for an account at CMS-IAM https://cms-auth.web.cern.ch/ and setup oidc-agent for cms (following these steps https://dodas-ts.github.io/dodas-apps/setup-oidc/ subsituting dodas with cms links and names). Once done this, create an HTCondor user using ```htcondor/submit:8.9.9-el7``` image. Ask your cluster admin for a CA certificate and write it into ```/ca.cert``` file. Besides, ```oidc-token cms``` to get a valid token and put it into ```/tmp/token``` file. Once you have done these two steps, set these environment variables:
```
export _condor_AUTH_SSL_CLIENT_CAFILE=/ca.crt
export _condor_SEC_DEFAULT_AUTHENTICATION_METHODS=SCITOKENS
export _condor_SCITOKENS_FILE=/tmp/token                          # token from CMS-IAM
export _condor_COLLECTOR_HOST=212.189.205.205.xip.io:30618
export _condor_SCHEDD_HOST=schedd.condor.svc.cluster.local
export _condor_TOOL_DEBUG=D_FULLDEBUG,D_SECURITY
```
Now you are good to go!

## Admin guide 

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

This way the Jupyterhub uses DODAS-iam authentication to give access to a newly created jupyter notebook instance.

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
HTCondor components use PASSWORD authentication method using a shared secret across the cluster.

### Get CA certs for clients

HTCondor clients outside the cluster use a SCITOKENS authentication method, using CMS-IAM token. CA certs can be retrieved with
```
kubectl exec schedd-pod-<pod name here> cat /etc/certs/ca.crt
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

