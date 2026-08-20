# AI-Powered Kubernetes Cost & Performance Optimizer

A DevOps/SRE portfolio project that analyses Kubernetes CPU and memory usage,
identifies inefficient resource requests, generates conservative right-sizing
recommendations, estimates theoretical savings when pricing inputs are supplied,
and exposes live optimisation metrics through Prometheus and Grafana.

## What problem does it solve?

Kubernetes workloads are often deliberately over-provisioned to reduce the risk
of instability. That can leave CPU and memory requested but underused, reducing
cluster efficiency.

Reducing resources too aggressively creates the opposite problem: throttling,
memory pressure and poor application performance.

This project demonstrates a recommendation-first approach:

```text
Kubernetes Pods API + Metrics API
              |
              v
     Resource utilisation analysis
              |
              v
        Optional cost analysis
              |
              v
      Recommendation engine
              |
              v
        /metrics endpoint
              |
              v
           Prometheus
              |
              v
            Grafana
```

The optimizer deliberately recommends changes rather than automatically patching
live workloads.

## Live monitoring evidence

The monitoring stack is validated inside an ephemeral Kubernetes cluster created
by GitHub Actions.

![AI Kubernetes Cost Optimizer Grafana Dashboard](docs/images/grafana-dashboard.png)

The integration workflow:

1. Creates a temporary kind Kubernetes cluster.
2. Installs Metrics Server.
3. Deploys a controlled sample workload.
4. Deploys the optimizer with least-privilege Kubernetes RBAC.
5. Exposes optimizer results through an HTTP `/metrics` endpoint.
6. Deploys Prometheus and validates that it successfully scrapes the optimizer.
7. Provisions Grafana with Prometheus as the datasource.
8. Loads the version-controlled optimizer dashboard.
9. Captures the populated dashboard as CI evidence.
10. Uploads monitoring evidence before the temporary cluster is destroyed.

## Key capabilities

- Kubernetes Pods and Metrics API integration
- CPU and memory utilisation analysis
- over-provisioned, under-provisioned, healthy and insufficient-data classification
- conservative resource recommendations with configurable safety headroom
- minimum CPU and memory request floors
- configurable theoretical cost and savings estimates
- HTTP Prometheus `/metrics` endpoint
- live Prometheus scraping
- provisioned Grafana datasource and dashboard
- Docker containerisation
- Helm packaging and Kubernetes CronJob deployment
- namespace-scoped ServiceAccount, Role and RoleBinding
- kind-based Kubernetes integration testing
- GitHub Actions CI/CD
- GitHub Container Registry image publishing
- Trivy container vulnerability scanning
- Kubeconform Kubernetes manifest validation
- Bandit static application security scanning
- Python dependency vulnerability auditing
- GitOps image promotion with Argo CD configuration
- numeric non-root container runtime and restricted capabilities

## Architecture

See [`docs/architecture.md`](docs/architecture.md) for the detailed architecture.

At a high level:

```text
                    Kubernetes Cluster
                           |
              +------------+------------+
              |                         |
              v                         v
        Kubernetes Pods API        Metrics API
              |                         |
              +------------+------------+
                           |
                           v
                  Kubernetes Collector
                           |
                           v
                 Utilisation Analysis
                           |
                           v
                   Cost Analysis
                           |
                           v
                Recommendation Engine
                           |
                           v
                    /metrics :8000
                           |
                           v
                     Prometheus
                           |
                           v
                       Grafana
```

## Recommendation safety

The optimizer does **not** automatically modify workload CPU or memory requests.

Recommendations use configurable headroom instead of setting requests equal to a
single observed usage sample.

A production autonomous right-sizing system would additionally need historical
metrics, percentile-based analysis, workload criticality, SLO awareness,
approval controls, deployment safety checks and rollback mechanisms.

## Example optimisation

For a workload configured with:

```text
CPU request:     500m
Memory request:  512Mi
```

and observed around:

```text
CPU usage:       100m
Memory usage:    128Mi
```

the optimizer calculates utilisation and generates a conservative recommendation
rather than blindly reducing requests to the current usage level.

## Observability metrics

Examples exposed by the optimizer include:

```text
optimizer_workloads_analyzed_total
optimizer_run_success
optimizer_workloads_by_status
optimizer_workload_status
optimizer_recommended_cpu_request_millicores
optimizer_recommended_memory_request_mib
optimizer_theoretical_monthly_savings_total
```

These metrics are scraped by Prometheus and visualised in Grafana.

## CI/CD and validation

The repository contains automated workflows covering:

- Python syntax and unit testing
- end-to-end optimizer tests
- Docker image build and execution
- non-root runtime verification
- recommendation artifact generation
- Trivy image scanning
- GHCR image publishing
- Kubernetes manifest validation with Kubeconform
- Helm validation
- Kubernetes RBAC validation
- kind-based real Kubernetes integration
- Prometheus scrape validation
- Grafana health and dashboard validation
- Bandit static security analysis
- dependency auditing
- GitOps image promotion

## Security approach

The Kubernetes and container runtime use several defence-in-depth controls:

- dedicated Kubernetes ServiceAccount
- namespace-scoped RBAC
- explicit numeric non-root UID/GID
- `runAsNonRoot`
- privilege escalation disabled
- Linux capabilities dropped
- RuntimeDefault seccomp profile
- automated static security and dependency checks

The optimizer receives only the Kubernetes API access required for its read-only
metrics workflow.

## Repository structure

```text
app/                    Python optimizer and analysis logic
tests/                  Unit and end-to-end tests
k8s/                    Kubernetes manifests and controlled test workload
helm/                   Helm chart
monitoring/             Prometheus, Grafana and optimizer metrics deployment
argocd/                 Argo CD / GitOps configuration
.github/workflows/      CI/CD, security and integration workflows
docs/                   Architecture and portfolio evidence
```

## Testing without a permanent Kubernetes cluster

The integration environments are created on demand using kind inside GitHub
Actions. This allows the project to exercise real Kubernetes APIs, Metrics
Server, Prometheus and Grafana without maintaining a permanent cloud cluster.

The monitoring workflow preserves evidence as GitHub Actions artifacts before
the temporary environment is removed.

## Project status

**Core portfolio implementation complete.**

Implemented and validated:

- Kubernetes resource and Metrics API integration
- utilisation and theoretical cost analysis
- safe right-sizing recommendation engine
- Docker and Helm packaging
- least-privilege Kubernetes RBAC
- automated CI/CD
- container and application security checks
- GHCR publishing
- Kubeconform validation
- live Prometheus metrics
- Grafana dashboard
- end-to-end Kubernetes monitoring evidence

AWS/EKS and Terraform are intentionally outside the scope of this repository and
can be demonstrated separately as an infrastructure-focused portfolio project.