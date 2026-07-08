# Security Notes — Container Image Scanning (Trivy)

**Image:** `apigw:latest` (single shared image for all 5 services)
**Scanner:** Trivy (`trivy image --severity HIGH,CRITICAL apigw:latest`)
**Base image:** `python:3.10-slim` (Debian 13.5)
**Last scanned:** 2026-07-08

## Summary

| Milestone | HIGH/CRITICAL findings |
|---|---|
| First scan | **52** (20 OS + 2 Python + 30 from a stray Terraform binary) |
| After `.dockerignore` fix | **22** (20 OS + 2 Python) |

**Biggest fix:** the first scan flagged 30 HIGH/CRITICAL CVEs inside
`terraform/.terraform/.../terraform-provider-aws_...x5.exe` — a ~500 MB **Windows**
binary that `COPY . .` had accidentally baked into the Linux image. It can't even
run in the container; it was pure bloat and attack surface. Adding `terraform/` to
`.dockerignore` removed it entirely, eliminating all 30 findings and shrinking the
image. **Lesson: keep the build context clean.**

## Remaining findings & decisions

### 1. Debian OS packages — 18 HIGH + 2 CRITICAL — ACCEPTED (no fix available)

Packages: `perl-base`, `util-linux`/`libblkid1`/`libmount1`/`libuuid1`/`bsdutils`,
`ncurses` (`libncursesw6`/`libtinfo6`/`ncurses-base`), `gzip`, `libacl1`, `login`, `mount`.

- **Why not fixed:** every one shows an **empty `Fixed Version`** and status
  `affected` / `fix_deferred` — Debian has not released patched packages yet. There
  is nothing to upgrade to.
- **Reachability:** these are base-OS libraries (partition parsing, terminal handling,
  perl, gzip). The FastAPI app never invokes them, so real exploitability is low.
- **Action:** accept for now; **re-scan on every rebuild** and they will clear as
  Debian ships fixes. Future hardening option: move to a smaller base
  (`distroless` or `alpine`) to shed most of these OS packages entirely.

### 2. Python build tooling — 2 HIGH — ACCEPTED (not runtime deps)

| Package | CVE | Installed | Fixed in | Notes |
|---|---|---|---|---|
| `jaraco.context` | CVE-2026-23949 | 5.3.0 | 6.1.0 | vendored inside `setuptools` |
| `wheel` | CVE-2026-24049 | 0.45.1 | 0.46.2 | vendored inside `setuptools` |

- **Why low risk:** both are **build/packaging tools** bundled with `setuptools`, used
  only when *installing* packages — not by the running gateway. Their vulnerable code
  paths (malicious tar/wheel extraction) are never exercised at runtime.
- **Action:** can be removed by not shipping `pip`/`setuptools` in the final image, or
  upgraded on the next dependency refresh. Accepted for now as non-reachable.

## Next steps

- Add a **Trivy scan job to the CI pipeline** (Phase 4) so future images are scanned
  automatically and HIGH/CRITICAL regressions can fail the build.
- Re-run the scan after any base-image bump; update the table above.
