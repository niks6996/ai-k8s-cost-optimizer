import pytest

from app.cost_analyzer import analyse_resources
from app.recommendation_engine import generate_recommendation


def test_over_provisioned_workload_gets_smaller_requests_with_headroom():
    analysis = analyse_resources(
        cpu_request_m=500,
        cpu_usage_m=100,
        memory_request_mib=512,
        memory_usage_mib=128,
    )

    recommendation = generate_recommendation(analysis)

    assert recommendation.status == "over_provisioned"
    assert recommendation.recommended_cpu_request_m == 130.0
    assert recommendation.recommended_memory_request_mib == 176.0
    assert recommendation.cpu_change_percent == -74.0
    assert recommendation.memory_change_percent == pytest.approx(-65.62, abs=0.01)
    assert recommendation.confidence == "medium"


def test_under_provisioned_workload_never_recommends_reduction():
    analysis = analyse_resources(
        cpu_request_m=200,
        cpu_usage_m=190,
        memory_request_mib=256,
        memory_usage_mib=250,
    )

    recommendation = generate_recommendation(analysis)

    assert recommendation.status == "under_provisioned"
    assert recommendation.recommended_cpu_request_m >= 200
    assert recommendation.recommended_memory_request_mib >= 256
    assert recommendation.confidence == "high"


def test_healthy_workload_keeps_current_requests():
    analysis = analyse_resources(
        cpu_request_m=500,
        cpu_usage_m=300,
        memory_request_mib=512,
        memory_usage_mib=300,
    )

    recommendation = generate_recommendation(analysis)

    assert recommendation.status == "healthy"
    assert recommendation.recommended_cpu_request_m == 500
    assert recommendation.recommended_memory_request_mib == 512
    assert recommendation.cpu_change_percent == 0.0
    assert recommendation.memory_change_percent == 0.0


def test_zero_request_returns_insufficient_data():
    analysis = analyse_resources(
        cpu_request_m=0,
        cpu_usage_m=50,
        memory_request_mib=256,
        memory_usage_mib=100,
    )

    recommendation = generate_recommendation(analysis)

    assert recommendation.status == "insufficient_data"
    assert recommendation.recommended_cpu_request_m is None
    assert recommendation.recommended_memory_request_mib is None
    assert recommendation.confidence == "low"


def test_minimum_resource_floors_are_respected():
    analysis = analyse_resources(
        cpu_request_m=100,
        cpu_usage_m=1,
        memory_request_mib=128,
        memory_usage_mib=1,
    )

    recommendation = generate_recommendation(analysis)

    assert recommendation.status == "over_provisioned"
    assert recommendation.recommended_cpu_request_m == 25.0
    assert recommendation.recommended_memory_request_mib == 32.0


def test_custom_headroom_is_applied():
    analysis = analyse_resources(
        cpu_request_m=1000,
        cpu_usage_m=200,
        memory_request_mib=1024,
        memory_usage_mib=200,
    )

    recommendation = generate_recommendation(
        analysis,
        cpu_headroom_percent=50,
        memory_headroom_percent=50,
    )

    assert recommendation.recommended_cpu_request_m == 300.0
    assert recommendation.recommended_memory_request_mib == 304.0


def test_invalid_thresholds_are_rejected():
    analysis = analyse_resources(
        cpu_request_m=500,
        cpu_usage_m=100,
        memory_request_mib=512,
        memory_usage_mib=128,
    )

    with pytest.raises(ValueError):
        generate_recommendation(
            analysis,
            over_provisioned_threshold_percent=95,
            under_provisioned_threshold_percent=90,
        )


def test_negative_headroom_is_rejected():
    analysis = analyse_resources(
        cpu_request_m=500,
        cpu_usage_m=100,
        memory_request_mib=512,
        memory_usage_mib=128,
    )

    with pytest.raises(ValueError):
        generate_recommendation(
            analysis,
            cpu_headroom_percent=-10,
        )


def test_recommendation_to_dict_is_json_friendly():
    analysis = analyse_resources(
        cpu_request_m=500,
        cpu_usage_m=100,
        memory_request_mib=512,
        memory_usage_mib=128,
    )

    payload = generate_recommendation(analysis).to_dict()

    assert payload["status"] == "over_provisioned"
    assert "recommended_cpu_request_m" in payload
    assert "recommended_memory_request_mib" in payload