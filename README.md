# INFN Analysis Facility
Often, in order to perform their analysis, particle physicists have to use resources shared between the whole research community, which in meny cases results in inefficiency and bad user experience, along with limited access to specialized hardware and software. Here we present a prototype of Analysis Facility whose aim is to provide analysts a straightforward access to a Python-based scalable computational environment (focusing on columnar analysis) that can be deployed on-demand, allowing also access to specialized hardware. Kubernetes clusters are used to host necessary services, which include Jupyterhub and a batch system (HTCondor). Security is ensured by OAuth 2.0 and Scitokens authentication, while the on-demand deployment is allowed by DODAS service. Althought presented as a CMS experiment use case, this tool is as most general-porpouse as it can get, allowing researchers from different experiments to share the same local resources.

This repo contains all information and recipes to set up an Analysis Facility on INFN infrastructure. 
In particular, in this example, we show how to set up an Analysis Facility built on top of two Kubernetes clusters deployed via DODAS, one for Jupyterhub deployment and the second one for HTCondor batch system, which read data from an XRootD cache server.

![alt text](AnalysisFacility_OSG_2.png)

As shown in the figure above, users get access to a Jupyer Notebook instance authenticating at Jupyterhub endpoint via DODAS-Iam. Here, they can perform analysis locally (also  spawning and exploiting Spark workers) or submitting jobs via Dask to the HTCondor batch system. 

In the remainder of the documentation, we will provide two different user guides: one for admins, and another one for users. The former will explain how to set up an Analysis Facility built on top of two Kubernetes clusters deployed via DODAS, one for Jupyterhub deployment and the second one for HTCondor batch system, which read data from an XRootD cache server. The latter will explain how to access JupyterHub endpoint or set up an autonomous HTCondor client, while providing some analysis example scripts.

## User Guide
As a user of the analysis facility, you would like to both get access directly to the HTCondor cluster and to a Jupyter Notebook (which in turn can be used to submit jobs to HTCondor via Dask).

### Requirements
This guide only requires a web access via browser (for Jupyter Notebook) and a Docker Desktop installation (for HTCondor standalone client). In order to get access directly to the HTCondor cluster, you should first apply for an account at CMS-IAM https://cms-auth.web.cern.ch/ and setup oidc-agent for cms (https://github.com/ttedeschi/INFN-analysis-facility/blob/main/oidc-token-cms.md)

### Access to Jupyter Notebook
In order to get a Jupyter Notebook, you first have to apply for a Dodas-IAM account at https://dodas-iam.cloud.cnaf.infn.it/. Once you receive notification of account creation, you are good to go.

Go to http://90.147.75.37:30888/ and authenticate via Dodas-IAM, choosing the resources that will be assigned to your notebook. Once you have done this, you will be able to run multiple Jupyter notebooks, where you can perform your analysis or that you can use to submit jobs to HTCondor.

### Direct access to HTCondor via client
Create an HTCondor user using ```htcondor/submit:8.9.9-el7``` image. 

TEMPORARY SOLUTION: ask your cluster admin for a CA certificate and write it into ```/ca.cert``` file. Besides, ```oidc-token cms``` to get a valid token and put it into ```/tmp/token``` file. 

Once you have done these two steps, set these environment variables:
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
Following this guide you will deploy Jupyterhub and HTCondor batch system on top of two different Kubernetes clusters.

### Requirements
You need a working DODAS Iam-demo account: follow https://dodas-ts.github.io/dodas-apps/setup-oidc/ to get one.

### Setup Jupyterhub
Create the Kubernetes cluster
``` 
dodas create TOSCA_templates/jupyterhub.yaml 
```
Get infrastructure ID via:
``` 
dodas list InfIDs
```
Log into the cluster:
``` 
dodas login <InfID> 0
```
Then, add this TEMPORARY FIX: ```kubectl -n kube-system edit daemonset kube-flannel-ds-amd64``` putting ``` --iface-regex=172\.30\.X\.*``` into container args where x is the third component of k8s master internal IP.

Add Dodas Helm charts to Helm repos
```
helm repo add dodas https://dodas-ts.github.io/helm_charts
helm repo update
```
then subsitute in ```values/jupyterhub.yaml``` k8s master public IP and deploy Jupyterhub:
```
helm install  dodas/jupyterhub --values jupyterhub-value.yaml --generate-name --kubeconfig /etc/kubernetes/admin.conf
```
Then, set up DODAS-Iam authentication
```
kubectl edit deployment hub
```
and substitute infn-cloud website with ```https://dodas-iam.cloud.cnaf.infn.it```

This way the Jupyterhub uses DODAS-Iam authentication to give access to a newly created jupyter notebook instance.

### Setup htcondor
Create the Kubernetes cluster
``` 
dodas create TOSCA_templates/htcondor.yaml
```
Get infrastructure ID via:
``` 
dodas list InfIDs
```
Log into the cluster:
``` 
dodas login <InfID> 1
```
After login, install a storage system and a cert-manager:
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
After substituting <k8s master public ip> with the real value inside ```k8s_templates/htcondor.yaml```, create the htcondor deployment
```
kubectl apply -f k8s_templates/htcondor.yaml
```
HTCondor components use PASSWORD authentication method using a shared secret across the cluster.

### Get CA certs for clients

HTCondor clients outside the cluster use a SCITOKENS authentication method, using CMS-IAM token. CA certs can be retrieved with
```
kubectl exec schedd-pod-<pod name here> cat /etc/certs/ca.crt
```



