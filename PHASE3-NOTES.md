# Phase 3 — Kubernetes Intermediate: Notes & Cheat-Sheet

> API Gateway project · Ingress, probes, and autoscaling.
> Use this for review and CKA prep.

## What we built

Phase 3 closed three production gaps in the Kubernetes setup:

| Gap | Problem | What we added |
|-----|---------|---------------|
| **Health** | K8s only knew if the *process* was alive, not if the app was actually working | `/health` endpoints + **liveness & readiness probes** |
| **Access** | Reaching the gateway needed `kubectl port-forward` (manual, single-user, no URL) | **Ingress** + NGINX Ingress Controller (real URL: `apigw.local`) |
| **Load** | `replicas: 1` was fixed — couldn't handle traffic spikes | **HorizontalPodAutoscaler (HPA)** scaling on CPU |

New files: `k8s/ingress.yaml`, `k8s/hpa.yaml`. Edited: every Deployment (probes), the gateway (CPU `resources` + a public `/health` route placed BEFORE the catch-all), all services (`/health`).

## Core concepts

- **Liveness probe** — "is it healthy?" Fails → Kubernetes **restarts** the pod.
- **Readiness probe** — "is it ready for traffic?" Fails → Kubernetes **stops routing traffic** to it (does NOT restart).
- **Rolling update** — pods are immutable; changing the template makes a new ReplicaSet and cuts over gradually. Readiness **gates the cutover**, so a broken new version can't take down the working old one → zero-downtime deploys.
- **Ingress vs. your gateway** — the Ingress Controller is the *cluster's edge router* (routes by host/path to a Service, handles TLS). Your gateway is *app-level* (JWT auth, rate limiting, routing among your services). Different layers.
- **HPA math** — `desiredReplicas = ceil(currentReplicas × currentCPU ÷ targetCPU)`. Needs **metrics-server** (data) + a **CPU request** on the pods (the baseline). Scales **up fast**, **down slow** (anti-flapping).
- **minikube has its own image store** — pods don't see your host's Docker images automatically.

## Command reference

| Command | Use case |
|---------|----------|
| `minikube addons enable ingress` | Install the NGINX Ingress Controller |
| `minikube addons enable metrics-server` | Install the metrics source the HPA reads |
| `kubectl apply -f k8s/` | Push desired state (all manifests); idempotent |
| `kubectl get pods / ingress / hpa / svc` | Inspect current state |
| `kubectl get hpa gateway-hpa --watch` | Live-stream changes (watch replicas climb) |
| `kubectl describe pod <name>` | Detail + **events** — the #1 tool for diagnosing pod failures |
| `kubectl logs <name>` | A pod's app-level stdout/stderr |
| `kubectl rollout restart deployment <names>` | Recreate a deployment's pods (e.g. to pick up a new image) |
| `docker build -t apigw:latest .` | Rebuild the image after a code change |
| `minikube image load apigw:latest` | Copy a host image into minikube's store |
| `minikube docker-env \| Invoke-Expression` | Point `docker` at minikube's daemon so builds land where pods run |
| `minikube tunnel` | Bridge the Ingress to 127.0.0.1 (must stay running) |
| `kubectl run ... load-generator ...` | Throwaway pod to generate load |
| `kubectl top pods` | Live CPU/memory per pod (confirms metrics-server) |
| `Add-Content ...\etc\hosts` | Map `apigw.local` → 127.0.0.1 (needs Admin) |
| `curl.exe http://apigw.local/...` | Test through the real URL |

## Challenges faced & lessons

1. **`/health` 404 / gateway still demanded a token** — pods ran a **stale image**. minikube's `:latest` was cached; `minikube image load` didn't replace it.
   - **Fix:** `minikube docker-env | Invoke-Expression` → `docker build` → `kubectl rollout restart`.
   - **Lesson:** minikube has its own Docker daemon; build *into* it. Debug pod failures with `kubectl describe pod` (events) first.
2. **`kubectl rollout restart deployment --all` → "unknown flag"** — name the deployments explicitly instead.
3. **`Add-Content` on hosts → "Access denied"** — the hosts file requires an **Administrator** shell.
4. **`apigw.local` → "could not resolve host"** — needs *both* the hosts entry *and* `minikube tunnel` running.
5. **A bad deploy caused no outage** — the **readiness probe** kept the old, working pods serving while the broken new ones were withheld. (Feature, not bug.)

## Debugging order (rule of thumb)

`kubectl get pods` (spot the symptom) → `kubectl describe pod <name>` (read the events = root cause) → `kubectl logs <name>` (app-level errors).

## Daily driver commands

```powershell
minikube start                 # bring the cluster back
minikube tunnel                # (separate window) enable the Ingress URL
kubectl get pods               # check health
minikube stop                  # free memory when done
```
