#!/usr/bin/env bash
# Bootstraps prerequisites on an EKS or Minikube cluster:
#  1. Ingress NGINX controller
#  2. Prometheus Operator & Grafana stack
#  3. gp3 StorageClass
set -euo pipefail

echo "==> Applying StorageClass..."
kubectl apply -f k8s/storageclass-gp3.yaml || true

echo "==> Installing ingress-nginx..."
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx || true
helm repo update
helm upgrade --install ingress-nginx ingress-nginx/ingress-nginx \
  --version 4.11.3 \
  -n ingress-nginx --create-namespace \
  -f monitoring/ingress-nginx-values.yaml

echo "==> Installing kube-prometheus-stack..."
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts || true
helm repo update
helm upgrade --install kube-prometheus-stack prometheus-community/kube-prometheus-stack \
  --version 65.5.0 \
  -n monitoring --create-namespace \
  -f monitoring/kube-prometheus-stack-values.yaml

echo "==> Cluster bootstrap complete. Pods status:"
kubectl get pods -A
