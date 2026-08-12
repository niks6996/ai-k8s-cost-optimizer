# AI-Powered Kubernetes Cost & Performance Optimizer

A portfolio DevOps/SRE project that analyses Kubernetes workload resource usage,
identifies inefficient CPU and memory requests, generates conservative
right-sizing recommendations, estimates potential savings when pricing inputs
are supplied, and exposes optimisation results as Prometheus-style metrics.

## Why this project exists

Kubernetes workloads are often over-provisioned to avoid performance problems.
That can leave CPU and memory reserved but unused. Reducing requests too
aggressively creates the opposite risk: throttling, instability and poor
scheduling decisions.

This project demonstrates a safer engineering workflow:

```text
Kubernetes Pods + Metrics API
            |
            v
Resource / utilisation analysis
            |
            v
Cost analysis (optional pricing)
            |
            v
Safe recommendation engine
            |
            v
Prometheus-style observability
```

## Key capabilities

- Kubernetes Pods and Metrics API integration
- namespaced least-privilege ServiceAccount/RBAC
- CPU and memory utilisation analysis
- optional cost estimation using configurable rates
- over-provisioned, under-provisioned, healthy and insufficient-data classification
- configurable recommendation headroom and minimum request floors
- Prometheus-style optimisation metrics
- Helm packaging and Kubernetes CronJob deployment
- GitHub Actions CI/CD validation
- kind-based Kubernetes integration testing
- GitOps image promotion
- non-root container runtime and restricted capabilities
- Bandit static security scanning and dependency auditing

## Architecture

See [`docs/architecture.md`](docs/architecture.md).

## Recommendation safety

The optimizer does **not** automatically patch live workloads.

Recommendations add configurable safety headroom instead of setting requests
equal to a single observed sample. Production automation would additionally
need historical data, approval controls, rollback, SLO awareness and
organisation-specific change management.

## CI/CD validation

The repository includes automated checks for:

- Python unit and end-to-end tests
- Kubernetes integration using kind
- Helm/Kubernetes deployment behaviour
- static security analysis
- dependency vulnerability auditing
- numeric non-root container execution
- obvious private-key leakage
- GitOps image promotion

## Repository areas

```text
app/                  Optimizer application and analysis logic
tests/                Unit and end-to-end tests
k8s/                  Kubernetes manifests and integration workload
helm/                 Helm packaging
gitops/               GitOps deployment configuration
.github/workflows/    CI/CD and integration workflows
docs/                 Architecture and engineering documentation
```

## Core optimisation flow

1. Collect Kubernetes workload resource configuration and usage.
2. Compare CPU/memory requests with observed usage.
3. Calculate utilisation and unused requested capacity.
4. Optionally estimate requested versus observed-usage cost.
5. Classify the workload.
6. Generate a conservative right-sizing recommendation.
7. Emit structured results and Prometheus-style metrics.

## Security approach

The project follows least-privilege and container-hardening principles:

- namespace-scoped Kubernetes RBAC
- dedicated ServiceAccount
- explicit numeric non-root container UID/GID
- `runAsNonRoot`
- privilege escalation disabled
- Linux capabilities dropped
- RuntimeDefault seccomp profile
- automated security and dependency checks

## Testing without a permanent cluster

A GitHub Actions integration workflow creates a temporary kind cluster,
installs Metrics Server, deploys a sample workload and the optimizer, validates
RBAC and Kubernetes API access, runs the optimizer, captures evidence, and then
discards the environment.

This keeps the project reproducible without requiring a permanent cloud
Kubernetes cluster.

## Project status

Core portfolio build complete through:

- real Kubernetes integration
- cost/utilisation analysis
- recommendation engine
- observability
- end-to-end orchestration
- production-oriented validation and security hardening