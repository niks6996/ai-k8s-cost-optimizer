"""Prometheus-style observability output for optimizer results.

This module intentionally uses only the Python standard library so the
optimizer can emit metrics without adding another runtime dependency.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional

from app.recommendation_engine import Recommendation


@dataclass(frozen=True)
class WorkloadObservation:
    namespace: str
    workload: str
    recommendation: Recommendation
    theoretical_monthly_savings: Optional[float] = None


_STATUS_VALUES = (
    "over_provisioned",
    "under_provisioned",
    "healthy",
    "insufficient_data",
)


def _escape_label(value: str) -> str:
    return (
        str(value)
        .replace("\\", "\\\\")
        .replace("\n", "\\n")
        .replace('"', '\\"')
    )


def _metric_line(name: str, value: float, **labels: str) -> str:
    if labels:
        rendered = ",".join(
            f'{key}="{_escape_label(label_value)}"'
            for key, label_value in sorted(labels.items())
        )
        return f"{name}{{{rendered}}} {value}"
    return f"{name} {value}"


def render_prometheus_metrics(
    observations: Iterable[WorkloadObservation],
    *,
    run_success: bool = True,
) -> str:
    """Render optimizer observations in Prometheus text exposition format."""

    observations = list(observations)

    status_counts = {status: 0 for status in _STATUS_VALUES}
    total_savings = 0.0

    lines = [
        "# HELP optimizer_workloads_analyzed_total Number of workloads analysed in the latest optimizer run.",
        "# TYPE optimizer_workloads_analyzed_total gauge",
        _metric_line("optimizer_workloads_analyzed_total", float(len(observations))),
        "# HELP optimizer_run_success Whether the latest optimizer run completed successfully.",
        "# TYPE optimizer_run_success gauge",
        _metric_line("optimizer_run_success", 1.0 if run_success else 0.0),
    ]

    for observation in observations:
        recommendation = observation.recommendation
        if recommendation.status not in status_counts:
            raise ValueError(
                f"Unsupported recommendation status: {recommendation.status}"
            )

        status_counts[recommendation.status] += 1

        savings = observation.theoretical_monthly_savings
        if savings is not None:
            if savings < 0:
                raise ValueError("theoretical_monthly_savings cannot be negative")
            total_savings += savings

        common_labels = {
            "namespace": observation.namespace,
            "workload": observation.workload,
        }

        for status in _STATUS_VALUES:
            lines.append(
                _metric_line(
                    "optimizer_workload_status",
                    1.0 if recommendation.status == status else 0.0,
                    **common_labels,
                    status=status,
                )
            )

        if recommendation.recommended_cpu_request_m is not None:
            lines.append(
                _metric_line(
                    "optimizer_recommended_cpu_request_millicores",
                    recommendation.recommended_cpu_request_m,
                    **common_labels,
                )
            )

        if recommendation.recommended_memory_request_mib is not None:
            lines.append(
                _metric_line(
                    "optimizer_recommended_memory_request_mib",
                    recommendation.recommended_memory_request_mib,
                    **common_labels,
                )
            )

        if savings is not None:
            lines.append(
                _metric_line(
                    "optimizer_theoretical_monthly_savings",
                    savings,
                    **common_labels,
                )
            )

    lines.extend(
        [
            "# HELP optimizer_workloads_by_status Number of workloads in each optimisation status.",
            "# TYPE optimizer_workloads_by_status gauge",
        ]
    )

    for status in _STATUS_VALUES:
        lines.append(
            _metric_line(
                "optimizer_workloads_by_status",
                float(status_counts[status]),
                status=status,
            )
        )

    lines.extend(
        [
            "# HELP optimizer_theoretical_monthly_savings_total Sum of theoretical monthly savings for analysed workloads.",
            "# TYPE optimizer_theoretical_monthly_savings_total gauge",
            _metric_line(
                "optimizer_theoretical_monthly_savings_total",
                round(total_savings, 4),
            ),
        ]
    )

    return "\n".join(lines) + "\n"


def write_prometheus_metrics(
    observations: Iterable[WorkloadObservation],
    output_path: str,
    *,
    run_success: bool = True,
) -> None:
    """Write rendered metrics to a .prom text file."""
    payload = render_prometheus_metrics(
        observations,
        run_success=run_success,
    )

    with open(output_path, "w", encoding="utf-8") as handle:
        handle.write(payload)