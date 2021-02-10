export KUBECONFIG=/etc/kubernetes/admin.conf
helm repo add infnAF https://ttedeschi.github.io/INFN-analysis-facility/helm-charts
helm repo update
helm install hub infnAF/jupyterhub --set hub.host=$1 --create-namespace --namespace jupyterhub --kubeconfig /etc/kubernetes/admin.conf
