# ClinicPulse: DevOps Capstone Submission & Rubric Evidence

Every grading criterion from the evaluation rubric, its exact location in the codebase, and the command to produce screenshot evidence.

**Candidate:** Tejas Kumat (`TejasKumat8`)  
**Project:** ClinicPulse — Healthcare Appointment & Patient Flow Orchestration Platform  

---

## M1: Application (10 Points)

| Evaluation Criterion | Implementation Location | Verification Status |
|---|---|---|
| FastAPI starts cleanly, `/health` responds | `backend/app/routers/system.py` | ✅ Verified (`{"status":"UP"}`) |
| ≥ 4 REST Endpoints (GET, POST, PUT, DELETE) | `backend/app/routers/appointments.py`, `doctors.py` (14 endpoints total) | ✅ Verified |
| PostgreSQL database schema managed by Alembic | `backend/alembic/versions/0001_*.py`, `0002_*.py` | ✅ Verified (`doctors`, `appointments` tables) |
| React frontend renders and interacts with REST API | `frontend/src/api.js`, `frontend/src/App.jsx` | ✅ Verified |
| Responsive, accessible user interface | `frontend/src/styles.css` (Breakpoints 1280px, 1100px, 860px, 480px) | ✅ Verified |

- 📸 `m1-app-desktop.png`: http://localhost:3000 after running `python scripts/seed_demo_data.py`
- 📸 `m1-app-mobile.png`: Viewport simulated as iPhone / Pixel in Chrome DevTools
- 📸 `m1-booking-conflict.png`: Double booking attempt showing `409 Conflict: Doctor already has appointment #X`

---

## M2: Testing (10 Points)

| Evaluation Criterion | Implementation Location | Verification Status |
|---|---|---|
| `pytest` runs and passes with zero errors | `backend/tests/` | ✅ 41 passed |
| ≥ 5 tests covering ≥ 3 endpoints | 41 unit & integration tests across 14 endpoints | ✅ |
| Database test isolation | `backend/tests/conftest.py` (In-memory SQLite StaticPool via dependency overrides) | ✅ Verified |
| `pytest.ini` and `conftest.py` present | `backend/pytest.ini`, `backend/tests/conftest.py` | ✅ Present & configured |

- 📸 `m2-pytest.png`: `cd backend && pytest -v`

---

## M3: Git & GitHub (5 Points)

| Evaluation Criterion | Verification Status |
|---|---|
| Public GitHub repository | ✅ `https://github.com/TejasKumat8/clinicpulse-devops-capstone` |
| Conventional commit history | ✅ `feat(...)`, `test(...)`, `ci(...)`, `fix(...)`, `infra(...)` |
| `.gitignore` security exclusions | ✅ Excludes `.env`, `__pycache__`, `node_modules`, `.venv`, `*.tfstate`, `*.tfvars` |

- 📸 `m3-commits.png`: `git log --oneline -n 12`
- 📸 `m3-repo.png`: GitHub repository overview page

---

## M4: Docker (10 Points)

| Evaluation Criterion | Implementation Location | Verification Status |
|---|---|---|
| Multi-stage `backend/Dockerfile` | `backend/Dockerfile` (builder -> minimal runtime) | ✅ Built |
| Multi-stage `frontend/Dockerfile` | `frontend/Dockerfile` (node:22-alpine -> nginx-unprivileged) | ✅ Built |
| Non-root user execution | Backend UID 10001, Frontend UID 101 | ✅ Verified |
| `docker compose up --build` brings up stack | `docker-compose.yml` (Healthcheck-gated dependency ordering) | ✅ Verified |

- 📸 `m4-compose-up.png`: `docker compose up -d && docker compose ps`
- 📸 `m4-nonroot.png`: `docker compose exec backend id && docker compose exec frontend id`
- 📸 `m4-browser.png`: Browser view on `http://localhost:3000`

---

## M5: CI/CD Pipeline (15 Points)

| Evaluation Criterion | Implementation Location | Verification Status |
|---|---|---|
| Automated GitHub Actions workflow | `.github/workflows/ci-cd.yml` | ✅ Implemented |
| Trigger on push and pull request | `on.push.branches: [main]` | ✅ Implemented |
| Pytest job fails build on failure | `backend-tests` step | ✅ Quality gate |
| Frontend compiled in pipeline | `frontend-build` step (node --test && vite build) | ✅ Quality gate |
| Multi-stage container images built | `build-scan-push` matrix job | ✅ Implemented |
| Published to GitHub Container Registry (GHCR) | `ghcr.io/tejaskumat8/clinicpulse-*` | ✅ Verified |
| Immutable Git commit SHA tagging | `:${{ github.sha }}` used strictly, never `latest` | ✅ Verified |

- 📸 `m5-pipeline-green.png`: GitHub Actions run summary showing all green jobs
- 📸 `m5-ghcr.png`: GitHub Packages page showing published containers with SHA tags

---

## M6: Security & Vulnerability Scanning (5 Points)

| Evaluation Criterion | Implementation Location | Verification Status |
|---|---|---|
| Trivy container scanning in CI | Matrix job across both backend and frontend images | ✅ Implemented |
| Hard security gate on HIGH/CRITICAL | `severity: HIGH,CRITICAL`, `exit-code: "1"` | ✅ Implemented |
| Documented CVE investigation & remediation | [docs/TRIVY.md](TRIVY.md) | ✅ 0 High/Critical |

- 📸 `m6-trivy.png`: Trivy step output showing zero HIGH/CRITICAL CVEs

---

## M7: Terraform Infrastructure as Code (15 Points)

| Evaluation Criterion | Implementation Location | Verification Status |
|---|---|---|
| Syntactically valid HCL code | `terraform/` (`terraform validate` passes in CI) | ✅ Verified |
| VPC with dual AZs and subnet separation | `10.40.0.0/16` with 2 public & 2 private subnets + NAT | ✅ Code complete |
| Managed Amazon EKS cluster | EKS 1.31 + AL2023 managed node group + EBS CSI addon | ✅ Code complete |
| Clean resource destruction script | `scripts/teardown-aws.sh` | ✅ Automated |
| `terraform.tfvars.example` without secrets | `terraform/terraform.tfvars.example` | ✅ Zero credentials |

- 📸 `m7-validate.png`: `terraform fmt -check && terraform validate`
- 📸 `m7-plan.png`: `terraform plan` output showing resources to add

---

## M8: Kubernetes & Helm (15 Points)

| Evaluation Criterion | Implementation Location | Verification Status |
|---|---|---|
| `k8s/namespace.yaml` with restricted security | `k8s/namespace.yaml` | ✅ Implemented |
| Production Helm Chart | `helm/clinicpulse/` (Chart.yaml, values.yaml, templates) | ✅ Implemented |
| High availability pod replicas | Backend & Frontend ≥ 2 replicas | ✅ Implemented |
| ClusterIP Services & Ingress routing | Ingress routes `/` -> frontend, `/api` -> backend | ✅ Implemented |
| Horizontal Pod Autoscaling (HPA) | HPA scaling backend from 2 to 6 pods at 60% CPU | ✅ Implemented |

- 📸 `m8-pods.png`: `kubectl get pods -n clinicpulse`
- 📸 `m8-svc.png`: `kubectl get svc,ingress,hpa -n clinicpulse`
- 📸 `m8-helm.png`: `helm list -n clinicpulse` and `helm test clinicpulse -n clinicpulse`

---

## M9: Observability & Monitoring (10 Points)

| Evaluation Criterion | Implementation Location | Verification Status |
|---|---|---|
| Custom business & HTTP `/metrics` | `backend/app/metrics.py`, `clinicpulse_*` metrics | ✅ Verified |
| Prometheus scraping configured | ServiceMonitor with `release: kube-prometheus-stack` | ✅ Implemented |
| Auto-provisioned Grafana Dashboard | `helm/clinicpulse/dashboards/clinicpulse.json` ConfigMap | ✅ 14-panel dashboard |

- 📸 `m9-metrics.png`: `curl http://localhost:8000/metrics | grep clinicpulse`
- 📸 `m9-grafana.png`: Grafana dashboard screenshot displaying traffic & latency

---

## M10: Presentation & Live Demo (5 Points)

| Evaluation Criterion | Verification Status |
|---|---|
| Complete root README.md | ✅ Comprehensive architecture, quickstart, and design decisions |
| Live walkthrough script | [docs/DEMO.md](DEMO.md) |
