helm repo add longhorn https://charts.longhorn.io
helm repo update
kubectl create namespace longhorn-system
helm install longhorn longhorn/longhorn --namespace longhorn-system --kubeconfig /etc/kubernetes/admin.conf
kubectl create namespace cert-manager
helm repo add jetstack https://charts.jetstack.io
helm repo update
helm install cert-manager jetstack/cert-manager --namespace cert-manager --version v1.1.0 --set installCRDs=true --kubeconfig /etc/kubernetes/admin.conf
helm repo add infnAF https://ttedeschi.github.io/INFN-analysis-facility/helm-charts
helm repo update
helm install condor infnAF/htcondor --set masterPublicIp=$1 --set namespace=default --kubeconfig /etc/kubernetes/admin.conf
