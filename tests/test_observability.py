from pathlib import Path

import pytest

from app.cost_analyzer import analyse_resources
from app.observability import (
    WorkloadObservation,
    render_prometheus_metrics,
    write_prometheus_metrics,
)
from app.recommendation_engine import generate_recommendation


def _observation(
    *,
    namespace="cost-optimizer",
    workload="sample-workload",
    cpu_request=500,
    cpu_usage=100,
    memory_request=512,
    memory_usage=128,
    savings=12.34,
):
    analysis = analyse_resources(
        cpu_request_m=cpu_request,
        cpu_usage_m=cpu_usage,
        memory_request_mib=memory_request,
        memory_usage_mib=memory_usage,
    )
    recommendation = generate_recommendation(analysis)

    return WorkloadObservation(
        namespace=namespace,
        workload=workload,
        recommendation=recommendation,
        theoretical_monthly_savings=savings,
    )


def test_renders_core_optimizer_metrics():
    payload = render_prometheus_metrics([_observation()])

    assert "optimizer_workloads_analyzed_total 1.0" in payload
    assert "optimizer_run_success 1.0" in payload
    assert (
        'optimizer_workload_status{namespace="cost-optimizer",'
        'status="over_provisioned",workload="sample-workload"} 1.0'
    ) in payload
    assert "optimizer_recommended_cpu_request_millicores" in payload
    assert "optimizer_recommended_memory_request_mib" in payload
    assert "optimizer_theoretical_monthly_savings_total 12.34" in payload


def test_counts_multiple_workload_statuses():
    over = _observation(workload="over")
    healthy = _observation(
        workload="healthy",
        cpu_request=500,
        cpu_usage=300,
        memory_request=512,
        memory_usage=300,
        savings=0,
    )

    payload = render_prometheus_metrics([over, healthy])

    assert "optimizer_workloads_analyzed_total 2.0" in payload
    assert 'optimizer_workloads_by_status{status="over_provisioned"} 1.0' in payload
    assert 'optimizer_workloads_by_status{status="healthy"} 1.0' in payload


def test_failed_run_is_visible():
    payload = render_prometheus_metrics([], run_success=False)

    assert "optimizer_run_success 0.0" in payload
    assert "optimizer_workloads_analyzed_total 0.0" in payload


def test_prometheus_labels_are_escaped():
    observation = _observation(
        namespace='team-"a"',
        workload="line\\name",
    )

    payload = render_prometheus_metrics([observation])

    assert 'namespace="team-\\"a\\""' in payload
    assert 'workload="line\\\\name"' in payload


def test_negative_savings_are_rejected():
    observation = _observation(savings=-1)

    with pytest.raises(ValueError, match="cannot be negative"):
        render_prometheus_metrics([observation])


def test_metrics_can_be_written_to_file(tmp_path: Path):
    output = tmp_path / "optimizer.prom"

    write_prometheus_metrics([_observation()], str(output))

    payload = output.read_text(encoding="utf-8")

    assert "optimizer_workloads_analyzed_total 1.0" in payload
    assert output.exists()