"""Safe Kubernetes rightsizing recommendation engine.

Day 17 converts Day 16 utilisation analysis into practical recommendations.
It deliberately adds safety headroom and minimum request floors so it does
not recommend setting Kubernetes requests equal to one observed usage sample.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Literal, Optional

from app.cost_analyzer import ResourceAnalysis


Status = Literal[
    "over_provisioned",
    "under_provisioned",
    "healthy",
    "insufficient_data",
]


@dataclass(frozen=True)
class Recommendation:
    status: Status
    reason: str

    recommended_cpu_request_m: Optional[float]
    recommended_memory_request_mib: Optional[float]

    cpu_change_percent: Optional[float]
    memory_change_percent: Optional[float]

    confidence: Literal["low", "medium", "high"]

    def to_dict(self) -> dict:
        return asdict(self)


def _percent_change(current: float, recommended: float) -> Optional[float]:
    if current <= 0:
        return None
    return round(((recommended - current) / current) * 100.0, 2)


def _round_up(value: float, step: float) -> float:
    if step <= 0:
        raise ValueError("rounding step must be greater than zero")

    quotient = value / step
    rounded = int(quotient)
    if quotient > rounded:
        rounded += 1
    return round(rounded * step, 4)


def generate_recommendation(
    analysis: ResourceAnalysis,
    *,
    cpu_headroom_percent: float = 30.0,
    memory_headroom_percent: float = 30.0,
    min_cpu_request_m: float = 25.0,
    min_memory_request_mib: float = 32.0,
    cpu_rounding_step_m: float = 10.0,
    memory_rounding_step_mib: float = 16.0,
    over_provisioned_threshold_percent: float = 40.0,
    under_provisioned_threshold_percent: float = 90.0,
) -> Recommendation:
    """Generate a conservative rightsizing recommendation.

    Classification rules:
    - insufficient_data: a request is zero, so utilisation cannot be calculated.
    - under_provisioned: CPU or memory utilisation is >= the upper threshold.
    - over_provisioned: both CPU and memory utilisation are <= the lower threshold.
    - healthy: everything else.

    Recommended requests are based on observed usage plus configurable headroom,
    then rounded upward and protected by configurable minimum request floors.
    """

    if cpu_headroom_percent < 0 or memory_headroom_percent < 0:
        raise ValueError("headroom percentages cannot be negative")

    if not 0 <= over_provisioned_threshold_percent < under_provisioned_threshold_percent:
        raise ValueError(
            "thresholds must satisfy 0 <= over_provisioned < under_provisioned"
        )

    cpu_util = analysis.cpu_utilisation_percent
    memory_util = analysis.memory_utilisation_percent

    if cpu_util is None or memory_util is None:
        return Recommendation(
            status="insufficient_data",
            reason=(
                "CPU or memory request is zero, so utilisation-based "
                "rightsizing cannot be calculated safely."
            ),
            recommended_cpu_request_m=None,
            recommended_memory_request_mib=None,
            cpu_change_percent=None,
            memory_change_percent=None,
            confidence="low",
        )

    raw_cpu_target = analysis.cpu_usage_m * (1 + cpu_headroom_percent / 100.0)
    raw_memory_target = analysis.memory_usage_mib * (
        1 + memory_headroom_percent / 100.0
    )

    recommended_cpu = max(
        min_cpu_request_m,
        _round_up(raw_cpu_target, cpu_rounding_step_m),
    )
    recommended_memory = max(
        min_memory_request_mib,
        _round_up(raw_memory_target, memory_rounding_step_mib),
    )

    if (
        cpu_util >= under_provisioned_threshold_percent
        or memory_util >= under_provisioned_threshold_percent
    ):
        status: Status = "under_provisioned"
        reason = (
            "Observed CPU or memory usage is close to or above the configured "
            "request. Increase requests to preserve operating headroom."
        )
        confidence = "high"

        # Never suggest reducing a request for an under-provisioned workload.
        recommended_cpu = max(recommended_cpu, analysis.cpu_request_m)
        recommended_memory = max(recommended_memory, analysis.memory_request_mib)

    elif (
        cpu_util <= over_provisioned_threshold_percent
        and memory_util <= over_provisioned_threshold_percent
    ):
        status = "over_provisioned"
        reason = (
            "Both CPU and memory utilisation are below the configured "
            "over-provisioning threshold. A smaller request may reduce "
            "reserved capacity while retaining safety headroom."
        )
        confidence = "medium"

        # Do not accidentally recommend a larger request for an
        # over-provisioned workload.
        recommended_cpu = min(recommended_cpu, analysis.cpu_request_m)
        recommended_memory = min(recommended_memory, analysis.memory_request_mib)

    else:
        status = "healthy"
        reason = (
            "Current resource requests are within the configured utilisation "
            "band. No immediate rightsizing change is recommended."
        )
        confidence = "medium"

        recommended_cpu = analysis.cpu_request_m
        recommended_memory = analysis.memory_request_mib

    return Recommendation(
        status=status,
        reason=reason,
        recommended_cpu_request_m=round(recommended_cpu, 4),
        recommended_memory_request_mib=round(recommended_memory, 4),
        cpu_change_percent=_percent_change(
            analysis.cpu_request_m, recommended_cpu
        ),
        memory_change_percent=_percent_change(
            analysis.memory_request_mib, recommended_memory
        ),
        confidence=confidence,
    )