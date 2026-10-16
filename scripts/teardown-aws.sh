#!/usr/bin/env bash
# Safely tears down AWS resources to prevent unexpected billing.
# Deletes Ingress NLB and EBS PVCs before destroying VPC and EKS.
set -euo pipefail

echo "==> 1. Uninstalling Helm releases..."
helm uninstall clinicpulse -n clinicpulse 2>/dev/null || true
helm uninstall kube-prometheus-stack -n monitoring 2>/dev/null || true
helm uninstall ingress-nginx -n ingress-nginx 2>/dev/null || true

echo "==> 2. Deleting PersistentVolumeClaims and namespaces..."
kubectl delete pvc --all -n clinicpulse 2>/dev/null || true
kubectl delete ns clinicpulse 2>/dev/null || true
kubectl delete ns ingress-nginx 2>/dev/null || true
kubectl delete ns monitoring 2>/dev/null || true

echo "==> Waiting 30s for AWS Load Balancers and ENIs to release..."
sleep 30

echo "==> 3. Running Terraform destroy..."
cd "$(dirname "$0")/../terraform"
terraform destroy -auto-approve

echo "==> All AWS resources destroyed cleanly."
