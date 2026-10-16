# ClinicPulse: 15-Minute Capstone Walkthrough Script

A step-by-step presentation script designed for the final evaluation session. Follows the required presentation sequence.

---

## 1. Pre-Session Setup (30 Minutes Prior)

```bash
# 1. Update kubeconfig to point to EKS cluster
aws eks update-kubeconfig --region ap-south-1 --name clinicpulse-eks

# 2. Confirm all pods and services are healthy
kubectl get pods,svc -n clinicpulse

# 3. Establish port forwards for Grafana and Prometheus
kubectl port-forward -n monitoring svc/kube-prometheus-stack-grafana 3001:80 &
kubectl port-forward -n monitoring svc/kube-prometheus-stack-prometheus 9090:9090 &

# 4. Resolve the application Ingress URL
APP="http://$(kubectl get svc -n ingress-nginx ingress-nginx-controller -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')"

# 5. Populate realistic clinical records
python scripts/seed_demo_data.py "$APP"
```

Open browser tabs:
- Application UI (`$APP`)
- Swagger Docs (`$APP/docs`)
- GitHub Repository Actions Tab
- GitHub Packages (GHCR)
- Grafana Dashboard (`http://localhost:3001`)
- Prometheus Targets (`http://localhost:9090/targets`)

---

## 2. Live Demo Sequence

| Phase | What to Demonstrate | Narration & Key Technical Points |
|---|---|---|
| **1. Application** | Book an appointment on `$APP`; attempt to book an overlapping slot for same doctor; advance status `SCHEDULED -> CHECKED_IN -> COMPLETED`. | *"ClinicPulse is an outpatient triage and scheduling application. It strictly prevents double-booking (returns 409 Conflict) and enforces clinical lifecycle rules."* |
| **2. REST API** | Open `$APP/docs`, inspect schema definitions, execute `GET /api/appointments/stats`. | *"14 REST endpoints implemented in FastAPI, validated via Pydantic v2 schemas and self-documenting through OpenAPI."* |
| **3. Database** | Run `kubectl exec -it clinicpulse-postgres-0 -n clinicpulse -- psql -U clinicpulse -c "select id, patient_name, appointment_type, status from appointments limit 5;"` | *"Stateful PostgreSQL managed by bidirectional Alembic migrations with advisory locking for multi-replica concurrency."* |
| **4. Git & CI/CD** | Make a minor change (e.g. update subtitle), push to `main`, show GitHub Actions pipeline running. | *"Every commit triggers automated Pytest suites, PostgreSQL integration, and multi-stage container builds. Images are tagged with immutable Git SHAs."* |
| **5. Container Security** | Show the Trivy scan step in GitHub Actions. | *"Aqua Security Trivy blocks any fixable HIGH or CRITICAL CVEs. Both runtime images run as non-root (UID 10001 backend, UID 101 frontend) and pip was stripped from runtime."* |
| **6. Cloud Infra (IaC)** | Review `terraform/main.tf` and AWS console showing VPC `10.40.0.0/16` and EKS. | *"Infrastructure defined in Terraform: 2 public, 2 private subnets, NAT gateway, and managed node group spanning dual AZs."* |
| **7. Kubernetes & Helm** | Show `helm list -n clinicpulse` and `kubectl get pods -n clinicpulse`. | *"Packaged as a production Helm chart featuring rolling updates, zero-downtime, liveness/readiness separation, and PodDisruptionBudgets."* |
| **8. Autoscaling (HPA)** | Run `./scripts/load-test.sh "$APP"` in one terminal and watch `kubectl get hpa -n clinicpulse -w`. | *"Horizontal Pod Autoscaler monitors CPU utilization and dynamically scales backend pods from 2 up to 6 replicas."* |
| **9. Observability** | Open Grafana dashboard showing requests/sec, latency, CPU utilization, and appointments by department. | *"Prometheus scrapes custom application metrics directly from /metrics via ServiceMonitor."* |
| **10. Troubleshooting** | Apply `kubectl apply -f troubleshooting/broken-service.yaml`, inspect with `kubectl get endpointslices`, fix via label patch. | *"Demonstrating diagnostic triage from runbook for missing Service endpoints."* |

---

## 3. Post-Session Cleanup

```bash
# Execute safe AWS teardown to release NLBs, EBS volumes, and VPC
./scripts/teardown-aws.sh
```
