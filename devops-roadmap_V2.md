# DevOps Roadmap — DevSecOps Edition (v2)

**Owner:** Aditya Anil Rawat (Adi)
**Last updated:** 2026-07-01
**Replaces:** Original 6-phase DevOps tracker
**Strategy:** DevOps core as the spine, security layered into every phase. Advanced DevSecOps (threat modeling, Burp Suite, SOAR, compliance frameworks) explicitly deferred to post-hire. Positioning: "DevSecOps-flavored DevOps fresher from a cybersecurity firm."

**Rules of engagement:**
- Exit criteria gate phase transitions, not time. A phase is done when the criteria are done.
- Security add-ons are ~15–20% of each phase, never the majority. If a security topic starts eating the core topic's time, stop and finish the core first.
- DSA prep (EY OA) and SAA-C03 run in parallel tracks and are NOT part of this tracker.
- Update the status table below as milestones land.

---

## Status Tracker

| Phase | Topic | Security Layer | Status |
|-------|-------|----------------|--------|
| 1 | Docker | Container security (Trivy, non-root, secrets hygiene) | ✅ Done (2026-07-08: multi-stage build, non-root user, Trivy scan + NOTES.md, secret hygiene) |
| 2 | Kubernetes Core | SecurityContexts, resource limits | ⬜ Not started (minikube ready) |
| 3 | Kubernetes Intermediate | RBAC, Secrets, Sealed Secrets intro | ⬜ Not started |
| 4 | GitLab CI/CD | Pipeline hardening, scanner deep-dive | ⬜ Not started (work assignment overlaps heavily) |
| 5 | Terraform + AWS | IAM least privilege, KMS, SG/NACL | ⬜ Not started (aligns with SAA-C03) |
| 6 | Observability | Security event logging, SIEM concepts | ⬜ Not started |

Legend: ⬜ Not started · 🟡 In progress · ✅ Done

---

## Phase 1 — Docker + Container Security ✅

**Core scope:**
- Dockerfile fundamentals: layers, caching, build context
- Multi-stage builds for the 5 FastAPI services (monorepo strategy)
- Docker Compose: networks, depends_on, healthchecks, env files
- Fix known blockers: create `requirements.txt` per service, replace hardcoded `localhost` URLs in gateway with `os.getenv()`
- Volumes, port mapping, container networking basics

**Security add-on:**
- Run Trivy against every built image; understand CVE severity levels
- Run all containers as non-root user (`USER` directive)
- No secrets in images or Dockerfiles — env vars / env files only; understand why secrets in layers are recoverable
- Pin base image versions; prefer slim/alpine variants and understand the tradeoff
- `.dockerignore` to keep junk (and secrets) out of build context

**Exit criteria — ALL must be true:**
- [x] All 5 services build with multi-stage Dockerfiles *(done 2026-07-08: builder + runtime stages in the shared Dockerfile)*
- [x] `docker compose up` brings up the full stack; gateway routes to all services successfully *(verified working end-to-end)*
- [x] Every service runs as non-root *(done 2026-07-08: appuser + USER directive; `docker compose exec gateway whoami` → appuser)*
- [x] Trivy scan run; HIGH/CRITICAL fixed or explained in NOTES.md *(done 2026-07-08: 52→22 HIGH/CRITICAL after removing a stray Terraform binary via `.dockerignore`; remaining OS/tooling CVEs documented + accepted in NOTES.md; one image shared by all 5 services)*
- [x] No hardcoded URLs or secrets *(done 2026-07-08: SECRET_KEY now REQUIRED from env — no fallback in gateway/main.py, auth_service.py, or docker-compose.yml; real value only in gitignored `.env`. NOTE: k8s/secret.yaml still holds a plaintext value → deferred to Phase 3 Sealed Secrets)*
- [x] Can explain: layers vs images, multi-stage benefits, bridge network DNS, why non-root matters *(taught 2026-07-08 with the kitchen/clean-plate analogy for multi-stage and the master-key analogy for non-root; Adi explained both back correctly)*

**Resume material to extract:** "Containerized a 5-service FastAPI microservices platform with multi-stage builds and Trivy image scanning; all services run as non-root."

---

## Phase 2 — Kubernetes Core + K8s Security Basics ⬜

**Prereq:** Phase 1 exit criteria complete. Minikube + kubectl already confirmed working.

**Core scope:**
- Pods, ReplicaSets, Deployments — the ownership chain
- Services: ClusterIP, NodePort; how kube-dns service discovery works
- Labels and selectors (how everything actually connects)
- kubectl fluency: apply, get, describe, logs, exec, port-forward, rollout
- Namespaces
- Deploy the API Gateway project to minikube

**Security add-on:**
- SecurityContext: `runAsNonRoot`, `readOnlyRootFilesystem`, `allowPrivilegeEscalation: false`
- Resource requests and limits on every container (and why missing limits is a security issue, not just a stability one)
- Why you never mount the Docker socket into a pod
- Awareness-level only: what RBAC is (deep dive is Phase 3)

**Exit criteria — ALL must be true:**
- [ ] All 5 services deployed to minikube via YAML manifests (no `kubectl run` shortcuts)
- [ ] Services communicate via ClusterIP DNS names, not IPs
- [ ] Gateway reachable from host via NodePort or port-forward; full request flow works (auth → JWT → downstream service)
- [ ] Every deployment has SecurityContext (non-root, no privilege escalation) and resource limits
- [ ] Can kill a pod and watch the Deployment self-heal; can explain the ReplicaSet's role
- [ ] Can explain: pod vs container, Deployment vs ReplicaSet, ClusterIP vs NodePort, what a label selector does

**Resume material:** "Deployed a 5-service microservices platform to Kubernetes with hardened SecurityContexts and resource governance."

---

## Phase 3 — Kubernetes Intermediate + RBAC/Secrets ⬜

**Prereq:** Phase 2 complete.

**Core scope:**
- ConfigMaps: env injection and file mounts
- Ingress + ingress controller on minikube (nginx ingress addon); path-based routing
- Liveness, readiness, and startup probes on all services
- HorizontalPodAutoscaler (metrics-server addon) — trigger a scale event under load
- Rolling updates and rollbacks (`kubectl rollout undo`)

**Security add-on:**
- RBAC properly: Roles, ClusterRoles, RoleBindings, ServiceAccounts; create a read-only ServiceAccount and prove it can't delete pods
- Kubernetes Secrets: create, mount, consume — and articulate why base64 ≠ encryption
- Intro to Sealed Secrets: the problem it solves (secrets in Git), conceptual understanding + one working demo
- Least privilege as a principle: each service gets its own ServiceAccount

**Exit criteria — ALL must be true:**
- [ ] Ingress routes `/auth`, `/users`, `/orders`, `/payments` paths to correct services
- [ ] All services have liveness + readiness probes; can demonstrate a failing readiness probe pulling a pod out of rotation
- [ ] HPA scales a service up under synthetic load and back down after
- [ ] JWT secret moved to a Kubernetes Secret, consumed as env var
- [ ] Custom Role + RoleBinding created; demonstrated that the restricted ServiceAccount gets `Forbidden` on disallowed verbs
- [ ] One Sealed Secret created and unsealed in-cluster
- [ ] Can explain: liveness vs readiness, how HPA decides to scale, RBAC's four objects and how they connect, why Secrets need encryption at rest or sealing

**Resume material:** "Implemented Kubernetes RBAC with per-service least-privilege ServiceAccounts, health probes, autoscaling, and sealed secret management."

---

## Phase 4 — GitLab CI/CD + Pipeline Hardening ⬜

**Prereq:** Phase 3 complete. NOTE: the work assignment (`wlsf82/frontend-and-backend`, GitLab Ultimate, 2× EC2, deadline ~July 2) already covers much of this — after the demo, this phase is consolidation, not first contact.

**Core scope:**
- `.gitlab-ci.yml` deep fluency: stages, jobs, artifacts, cache, rules, needs
- Runners: shell vs Docker executor, registration, tags
- Environment variables and protected variables
- Build → test → scan → deploy pipeline for the API Gateway project (mirror the work assignment on your own repo — gitlab.com free tier is fine for most of it)
- Container registry usage; tagging strategy

**Security add-on (the differentiator phase):**
- Be able to whiteboard the scanner taxonomy: SAST vs DAST vs dependency scanning vs container scanning vs secret detection — what each catches, at which pipeline stage, with a concrete example vulnerability for each
- Protected branches + protected variables: why deploy credentials never appear in MR pipelines from forks
- Pipeline hardening: pinned runner images, least-privilege deploy tokens vs personal tokens, artifact expiry
- Secret detection: plant a fake secret, watch it get caught, understand the remediation flow

**Exit criteria — ALL must be true:**
- [ ] Work assignment shipped and demoed (tracked separately in `gitlab-cicd-progress-log.md`)
- [ ] Personal project has a working pipeline: build images → run tests → at least 2 security scan jobs → deploy (minikube or EC2)
- [ ] Can explain every scanner type with one example vuln each, without notes — this is the interview centerpiece
- [ ] Protected branch + protected variable configured and behavior verified
- [ ] Deploy uses a scoped token, not a personal access token
- [ ] Postmortem written: 5 things that broke during the work assignment and how you debugged them (interview gold)

**Resume material:** already drafted in the DevSecOps resume — after this phase, replace placeholders with the confirmed scanner list and a real pipeline metric.

---

## Phase 5 — Terraform + AWS + Cloud Security (IAM focus) ⬜

**Prereq:** Phase 4 complete. Runs naturally alongside SAA-C03 prep — the security add-ons here ARE exam topics, so this phase is near-zero marginal cost.

**Core scope:**
- Terraform: providers, resources, variables, outputs, state (local then S3 backend + locking)
- Plan/apply/destroy discipline; reading plan diffs carefully
- Build with Terraform: VPC with public/private subnets, EC2 instance, security group, S3 bucket
- Recreate (a simplified version of) the work assignment's 2-EC2 setup as code
- Modules: refactor the above into at least one reusable module

**Security add-on:**
- IAM least privilege — the single most asked cloud security topic: users vs roles vs policies, policy JSON structure, why EC2 instance roles beat access keys on disk
- Security Groups vs NACLs: stateful vs stateless, when each applies
- KMS basics: encrypt an S3 bucket and an EBS volume with a customer-managed key
- S3 bucket policies + Block Public Access; understand the classic public-bucket breach pattern
- No secrets in Terraform code or state pushed to Git: variables files gitignored, understand state contains secrets in plaintext

**Exit criteria — ALL must be true:**
- [ ] `terraform apply` stands up VPC + subnets + EC2 + SG + S3 from scratch; `destroy` tears it down clean
- [ ] Remote state in S3 with locking configured
- [ ] At least one custom module written and consumed
- [ ] EC2 accesses S3 via an instance role — zero access keys on the box
- [ ] One customer-managed KMS key encrypting a real resource
- [ ] Can explain: Terraform state (what/why/where), SG vs NACL, IAM role vs user, why instance profiles > access keys
- [ ] SAA-C03 exam scheduled (booking it is the exit criterion; passing it is its own track)

**Resume material:** "Provisioned AWS infrastructure (VPC, EC2, S3) as code with Terraform, using IAM instance roles and KMS encryption under least-privilege design."

---

## Phase 6 — Observability + Security Monitoring ⬜

**Prereq:** Phase 5 complete.

**Core scope:**
- Prometheus: architecture (scrape model), installing on minikube (kube-prometheus-stack via Helm — first real Helm usage), PromQL basics
- Instrument the FastAPI gateway with a metrics endpoint (prometheus-fastapi-instrumentator)
- Grafana: build one dashboard — request rate, error rate, latency (RED method) for the gateway
- Alerting: one Alertmanager rule (e.g., error rate > threshold)
- Loki or basic log aggregation — connect to the structured logging already built in the gateway

**Security add-on:**
- SIEM conceptually: what it is, how it differs from Prometheus/Grafana (events vs metrics), where Splunk/Elastic sit in the DevSecOps map
- Security-relevant log analysis: detect failed auth attempts and rate-limit trips in the gateway logs; build one Grafana panel showing failed JWT validations over time
- Connect to internship context: this is what the "monitoring" boxes in a security consulting engagement mean

**Exit criteria — ALL must be true:**
- [ ] Prometheus scraping the gateway's real metrics on minikube
- [ ] Grafana dashboard with RED metrics for the gateway, built by hand (not just imported)
- [ ] One alert rule that fires when triggered deliberately
- [ ] One security panel: failed auth attempts / rate-limit events visualized from real gateway logs
- [ ] Can explain: pull vs push metrics, RED vs USE method, metrics vs logs vs traces, what a SIEM adds over a metrics stack
- [ ] CKA prep decision made (pursue now vs post-hire) — decide with real data on time available

**Resume material:** "Built Prometheus/Grafana observability for a microservices platform including security-event dashboards for authentication failures and rate-limit violations."

---

## Explicitly Deferred (post-hire, year 1–2)

Do not touch these until employed — they are promotion skills, not hiring skills:

- Threat modeling (STRIDE, PASTA)
- Burp Suite / offensive tooling (Nmap beyond basics, Nessus, OpenVAS)
- SOAR / automated response
- PKI design, certificate lifecycle management at scale
- Compliance frameworks: SOC 2, ISO 27001, NIST mappings
- Service mesh, GitOps (ArgoCD/FluxCD), advanced cloud design patterns

## Parallel Tracks (not gated by phases)

- **DSA prep** — `dsa-prep-roadmap.md`, 13 phases, EY OA is the gate. Highest priority conflict-winner: if time is short, DSA beats roadmap phases until the EY OA is cleared.
- **SAA-C03** — 8–12 week path; overlaps heavily with Phase 5. Target: exam booked by Phase 5 exit.
- **Work assignment** — `gitlab-cicd-progress-log.md`; deadline ~July 2, 2026.

## Calendar Sketch (loose, exit-criteria still rule)

- **Now → Jul 2:** Ship the work assignment. Roadmap paused if needed.
- **Jul – Sep:** Phases 1–3. SAA-C03 study in parallel. DSA untouched and sacred.
- **Oct – Dec:** Phases 4–6 consolidation, SAA-C03 exam, EY application window.
