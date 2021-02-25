export KUBECONFIG=/etc/kubernetes/admin.conf
helm repo add infnAF https://ttedeschi.github.io/INFN-analysis-facility/helm-charts
helm repo update
helm install hub infnAF/jupyterhub --set hub.host=$1 --set hub.image=ttedesch/jupyterhub:1.0.0 --kubeconfig /etc/kubernetes/admin.conf
