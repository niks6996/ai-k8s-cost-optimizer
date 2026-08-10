from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Optional


HOURS_PER_MONTH = 730.0


@dataclass(frozen=True)
class ResourceAnalysis:
    cpu_request_m: float
    cpu_usage_m: float
    cpu_utilisation_percent: Optional[float]
    cpu_unused_request_m: float

    memory_request_mib: float
    memory_usage_mib: float
    memory_utilisation_percent: Optional[float]
    memory_unused_request_mib: float

    requested_monthly_cost: Optional[float]
    observed_usage_monthly_cost: Optional[float]
    theoretical_monthly_savings: Optional[float]

    def to_dict(self) -> dict:
        """Return a JSON-serialisable representation."""
        return asdict(self)


def _validate_non_negative(name: str, value: float) -> float:
    try:
        numeric = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be a number.") from exc

    if numeric < 0:
        raise ValueError(f"{name} cannot be negative.")

    return numeric


def _utilisation_percent(usage: float, request: float) -> Optional[float]:
    if request == 0:
        return None
    return round((usage / request) * 100.0, 2)


def analyse_resources(
    *,
    cpu_request_m: float,
    cpu_usage_m: float,
    memory_request_mib: float,
    memory_usage_mib: float,
    cpu_core_hour_rate: Optional[float] = None,
    memory_gib_hour_rate: Optional[float] = None,
    hours_per_month: float = HOURS_PER_MONTH,
) -> ResourceAnalysis:
    
    cpu_request_m = _validate_non_negative("cpu_request_m", cpu_request_m)
    cpu_usage_m = _validate_non_negative("cpu_usage_m", cpu_usage_m)
    memory_request_mib = _validate_non_negative(
        "memory_request_mib", memory_request_mib
    )
    memory_usage_mib = _validate_non_negative(
        "memory_usage_mib", memory_usage_mib
    )
    hours_per_month = _validate_non_negative("hours_per_month", hours_per_month)

    cpu_unused_request_m = max(cpu_request_m - cpu_usage_m, 0.0)
    memory_unused_request_mib = max(memory_request_mib - memory_usage_mib, 0.0)

    requested_monthly_cost = None
    observed_usage_monthly_cost = None
    theoretical_monthly_savings = None

    rates_supplied = (
        cpu_core_hour_rate is not None or memory_gib_hour_rate is not None
    )

    if rates_supplied:
        if cpu_core_hour_rate is None or memory_gib_hour_rate is None:
            raise ValueError(
                "Both cpu_core_hour_rate and memory_gib_hour_rate "
                "must be supplied together."
            )

        cpu_core_hour_rate = _validate_non_negative(
            "cpu_core_hour_rate", cpu_core_hour_rate
        )
        memory_gib_hour_rate = _validate_non_negative(
            "memory_gib_hour_rate", memory_gib_hour_rate
        )

        requested_cpu_cores = cpu_request_m / 1000.0
        used_cpu_cores = cpu_usage_m / 1000.0

        requested_memory_gib = memory_request_mib / 1024.0
        used_memory_gib = memory_usage_mib / 1024.0

        requested_hourly_cost = (
            requested_cpu_cores * cpu_core_hour_rate
            + requested_memory_gib * memory_gib_hour_rate
        )
        usage_hourly_cost = (
            used_cpu_cores * cpu_core_hour_rate
            + used_memory_gib * memory_gib_hour_rate
        )

        requested_monthly_cost = round(
            requested_hourly_cost * hours_per_month, 4
        )
        observed_usage_monthly_cost = round(
            usage_hourly_cost * hours_per_month, 4
        )
        theoretical_monthly_savings = round(
            max(requested_monthly_cost - observed_usage_monthly_cost, 0.0),
            4,
        )

    return ResourceAnalysis(
        cpu_request_m=cpu_request_m,
        cpu_usage_m=cpu_usage_m,
        cpu_utilisation_percent=_utilisation_percent(cpu_usage_m, cpu_request_m),
        cpu_unused_request_m=round(cpu_unused_request_m, 4),
        memory_request_mib=memory_request_mib,
        memory_usage_mib=memory_usage_mib,
        memory_utilisation_percent=_utilisation_percent(
            memory_usage_mib, memory_request_mib
        ),
        memory_unused_request_mib=round(memory_unused_request_mib, 4),
        requested_monthly_cost=requested_monthly_cost,
        observed_usage_monthly_cost=observed_usage_monthly_cost,
        theoretical_monthly_savings=theoretical_monthly_savings,
    )