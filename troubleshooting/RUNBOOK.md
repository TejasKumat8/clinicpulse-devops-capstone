# ClinicPulse Incident Troubleshooting Runbook

This runbook documents diagnostic runbooks for simulating and resolving common cloud-native Kubernetes failure modes in the `clinicpulse` namespace.

```bash
# Trigger failure simulations
kubectl apply -f troubleshooting/

# Clean up simulation resources after diagnosis
kubectl delete -f troubleshooting/
```

### Standard Incident Triage Hierarchy:
`kubectl get pods` ──► `kubectl describe` ──► `kubectl logs` ──► `kubectl get endpointslices`

---

## Lab 1: `ImagePullBackOff` (Manifest: broken-image.yaml)

| Step | Command | Observation / Diagnostic Output |
|---|---|---|
| **Symptom** | `kubectl get pods -n clinicpulse -l lab=broken-image` | STATUS: `ImagePullBackOff`, READY: `0/1` |
| **Diagnose** | `kubectl describe pod -n clinicpulse -l lab=broken-image` | Event: `Failed to pull image "...:non-existent-tag-v9.9.9": manifest unknown` |
| **Root Cause** | — | Specified container tag does not exist on GHCR, or repository authentication missing. |
| **Remediation** | `kubectl set image deploy/lab-broken-image backend=ghcr.io/tejaskumat8/clinicpulse-backend:<valid-git-sha> -n clinicpulse` | Image pulls successfully; Pod transitions to `Running` (1/1). |

**Takeaway:** CI pipelines produce deterministic immutable tags matching `${GITHUB_SHA}`. Verify SHA tags on GitHub Packages.

---

## Lab 2: Service Missing Endpoints (Manifest: broken-service.yaml)

| Step | Command | Observation / Diagnostic Output |
|---|---|---|
| **Symptom** | `kubectl run test-curl --rm -it -n clinicpulse --image=curlimages/curl --restart=Never -- curl -m 3 http://lab-broken-service:8000/health` | `Connection timed out` or `refused`. |
| **Diagnose** | `kubectl get endpointslices -n clinicpulse -l kubernetes.io/service-name=lab-broken-service` | `ENDPOINTS: <unset>` — No matching Pod discovered. |
| **Label Audit** | `kubectl get svc lab-broken-service -n clinicpulse -o jsonpath='{.spec.selector}'`<br/>`kubectl get pods -n clinicpulse --show-labels` | Service requires `component=api`; Pods are labeled `component=backend`. |
| **Remediation** | `kubectl patch svc lab-broken-service -n clinicpulse -p '{"spec":{"selector":{"app.kubernetes.io/component":"backend"}}}'` | Endpoints immediately populate; traffic routes correctly. |

**Takeaway:** Kubernetes Services decouple routing via label selectors. A syntax mismatch between Service selector and Pod template labels results in silent routing failure.

---

## Lab 3: Container Running but Not Ready (Manifest: broken-readiness.yaml)

| Step | Command | Observation / Diagnostic Output |
|---|---|---|
| **Symptom** | `kubectl get pods -n clinicpulse -l lab=broken-readiness` | STATUS: `Running`, but READY: `0/1`. |
| **Diagnose** | `kubectl describe pod -n clinicpulse -l lab=broken-readiness` | Warning: `Readiness probe failed: ... :80/: connect: connection refused`. |
| **Root Cause** | — | Unprivileged container processes bind to port **8080**; the readiness probe checks default HTTP port **80**. |
| **Remediation** | `kubectl patch deploy lab-broken-readiness -n clinicpulse --type=json -p '[{"op":"replace","path":"/spec/template/spec/containers/0/readinessProbe/httpGet/port","value":8080}]'` | Probe succeeds; Pod reaches `Ready 1/1` within seconds. |

**Takeaway:** Understand probe semantics: Liveness verifies if the process is alive; Readiness determines if the process should receive traffic. Misconfigured readiness probes starve healthy containers from traffic.
