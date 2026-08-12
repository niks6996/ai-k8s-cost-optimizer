# Architecture

## High-level design

```text
                    +-----------------------+
                    |   Kubernetes Cluster  |
                    +-----------+-----------+
                                |
                 +--------------+--------------+
                 |                             |
                 v                             v
        Kubernetes Pods API             Metrics API
        requests / limits              CPU / memory use
                 |                             |
                 +--------------+--------------+
                                |
                                v
                    +-----------------------+
                    | Kubernetes Collector  |
                    +-----------+-----------+
                                |
                                v
                    +-----------------------+
                    | Analysis Layer        |
                    | utilisation + cost    |
                    +-----------+-----------+
                                |
                                v
                    +-----------------------+
                    | Recommendation Engine |
                    | safety headroom       |
                    +-----------+-----------+
                                |
                                v
                    +-----------------------+
                    | Observability Layer   |
                    | Prometheus metrics    |
                    +-----------+-----------+
                                |
                    +-----------+-----------+
                    |                       |
                    v                       v
             Structured result       Prometheus/Grafana
```

## Kubernetes execution

The optimizer is packaged as a container and deployed through Helm. A dedicated
ServiceAccount is bound to namespace-scoped read permissions. The workload runs
with a numeric non-root identity and restricted container privileges.

## CI/CD and integration validation

```text
Git push
   |
   v
GitHub Actions
   |
   +--> unit / end-to-end tests
   +--> security checks
   +--> container build
   +--> temporary kind cluster
              |
              +--> Metrics Server
              +--> sample workload
              +--> Helm deployment
              +--> RBAC validation
              +--> optimizer execution
              +--> evidence/log collection
```

The temporary cluster provides real Kubernetes API integration testing without
requiring a permanently running development cluster.

## Design boundary

The project generates recommendations rather than automatically mutating
production workloads. That boundary is deliberate because safe autonomous
rightsizing needs historical utilisation, workload criticality, SLO context,
approval policy and rollback controls.