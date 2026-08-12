from dataclasses import asdict, dataclass
from typing import Iterable, Optional
from app.cost_analyzer import analyse_resources
from app.observability import WorkloadObservation, render_prometheus_metrics
from app.recommendation_engine import generate_recommendation

@dataclass(frozen=True)
class WorkloadInput:
    namespace: str
    workload: str
    cpu_request_m: float
    cpu_usage_m: float
    memory_request_mib: float
    memory_usage_mib: float
    cpu_core_hour_rate: Optional[float] = None
    memory_gib_hour_rate: Optional[float] = None

@dataclass(frozen=True)
class WorkloadResult:
    namespace: str
    workload: str
    analysis: dict
    recommendation: dict
    def to_dict(self): return asdict(self)

@dataclass(frozen=True)
class OptimizerRunResult:
    workloads: list[WorkloadResult]
    prometheus_metrics: str
    def to_dict(self):
        return {"workloads":[w.to_dict() for w in self.workloads],
                "prometheus_metrics":self.prometheus_metrics}

def run_optimizer(workloads: Iterable[WorkloadInput], *, cpu_headroom_percent=30.0,
                  memory_headroom_percent=30.0) -> OptimizerRunResult:
    results, observations = [], []
    for w in workloads:
        pricing = {}
        if w.cpu_core_hour_rate is not None or w.memory_gib_hour_rate is not None:
            pricing = {"cpu_core_hour_rate": w.cpu_core_hour_rate,
                       "memory_gib_hour_rate": w.memory_gib_hour_rate}
        analysis = analyse_resources(cpu_request_m=w.cpu_request_m,
                                     cpu_usage_m=w.cpu_usage_m,
                                     memory_request_mib=w.memory_request_mib,
                                     memory_usage_mib=w.memory_usage_mib,
                                     **pricing)
        rec = generate_recommendation(analysis,
                                      cpu_headroom_percent=cpu_headroom_percent,
                                      memory_headroom_percent=memory_headroom_percent)
        results.append(WorkloadResult(w.namespace, w.workload,
                                      analysis.to_dict(), rec.to_dict()))
        observations.append(WorkloadObservation(
            namespace=w.namespace, workload=w.workload, recommendation=rec,
            theoretical_monthly_savings=analysis.theoretical_monthly_savings))
    return OptimizerRunResult(results, render_prometheus_metrics(observations, run_success=True))