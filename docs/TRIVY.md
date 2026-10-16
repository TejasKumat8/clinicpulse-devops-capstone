# Trivy Security Scan: Vulnerability Gate & Remediation Report

**Candidate:** Tejas Kumat  
**Project:** ClinicPulse  

---

## 1. Executive Summary

In our CI/CD pipeline, every container image is scanned by **Aqua Security Trivy** before publishing to GitHub Container Registry (GHCR). The scan inspects:
1. **Operating System Packages:** Debian Bookworm in `clinicpulse-backend`, Alpine Linux in `clinicpulse-frontend`.
2. **Language Dependencies:** Python packages in virtual environment (`site-packages`), JavaScript packages in Node runtime.

The CI gate enforces a strict security policy:
- **Severity Filter:** `HIGH,CRITICAL`
- **Unfixed Filter:** `ignore-unfixed: true` (avoids blocking pipelines on vulnerabilities where upstream patches do not yet exist)
- **Exit Code:** `1` (Any discovered fixable HIGH or CRITICAL vulnerability fails the job, halting deployment)

**Result:** Both `clinicpulse-backend` and `clinicpulse-frontend` images pass the scan with **0 HIGH and 0 CRITICAL** vulnerabilities.

---

## 2. Discovered Vulnerabilities & Engineering Remediation

During initial image creation, the backend image generated **4 HIGH** findings:

| Package | Vulnerability ID | Installed Version | Fixed In | Vulnerability Nature |
|---|---|---|---|---|
| `urllib3` | CVE-2026-97687 | 2.7.0 | 2.8.0 | Traffic interception via proxy TLS configuration override |
| `urllib3` | CVE-2026-97689 | 2.7.0 | 2.8.0 | Memory exhaustion / DoS in chunk parser |
| `msgpack` | GHSA-6v7p-g79w-8964 | 1.1.2 | 1.2.1 | Out-of-bounds memory read when Unpacker is reused |
| `setuptools` | CVE-2025-47273 | 70.3.0 | 78.1.1 | Path traversal vulnerability in PackageIndex |

### Root Cause Analysis
An inspection of the container layers revealed that none of these packages were direct dependencies of ClinicPulse. Instead, they were bundled internally inside **`pip`'s vendored dependencies** (`pip/_vendor/`) and the `ensurepip` module bundled with Python.

### Architectural Fix
Since ClinicPulse installs all packages during Stage 1 (`builder`) and strictly forbids runtime installation of packages, `pip` is entirely unnecessary in the runtime container:
1. In `backend/Dockerfile`, the runtime stage executes:
   ```dockerfile
   RUN python -m pip uninstall -y pip \
    && rm -rf /usr/local/lib/python3.12/ensurepip /usr/local/bin/pip*
   ```
2. In `frontend/Dockerfile`, we execute `apk upgrade --no-cache` to ensure all system libraries contain latest Alpine security patches.

**Outcome:** Attack surface is minimized (attackers gaining RCE cannot run `pip install`), image footprint is reduced, and Trivy reports **0 HIGH / 0 CRITICAL**.

---

## 3. GitHub Actions Pipeline Gate Configuration

```yaml
- name: Trivy vulnerability scan (fail on HIGH/CRITICAL)
  uses: aquasecurity/trivy-action@master
  with:
    image-ref: ${{ steps.meta.outputs.image }}:${{ github.sha }}
    format: table
    severity: HIGH,CRITICAL
    ignore-unfixed: true
    vuln-type: os,library
    exit-code: "1"
```

In addition to failing the build, a secondary pass generates a **SARIF** report uploaded to GitHub Code Scanning, populating the repository's **Security** tab for audit compliance.
