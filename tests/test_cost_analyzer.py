import pytest

from app.cost_analyzer import analyse_resources


def test_calculates_cpu_and_memory_utilisation():
    result = analyse_resources(
        cpu_request_m=500,
        cpu_usage_m=125,
        memory_request_mib=512,
        memory_usage_mib=256,
    )

    assert result.cpu_utilisation_percent == 25.0
    assert result.cpu_unused_request_m == 375.0

    assert result.memory_utilisation_percent == 50.0
    assert result.memory_unused_request_mib == 256.0

    assert result.requested_monthly_cost is None
    assert result.observed_usage_monthly_cost is None
    assert result.theoretical_monthly_savings is None


def test_usage_above_request_does_not_create_negative_unused_capacity():
    result = analyse_resources(
        cpu_request_m=250,
        cpu_usage_m=400,
        memory_request_mib=256,
        memory_usage_mib=300,
    )

    assert result.cpu_utilisation_percent == 160.0
    assert result.cpu_unused_request_m == 0.0
    assert result.memory_utilisation_percent == pytest.approx(117.19, abs=0.01)
    assert result.memory_unused_request_mib == 0.0


def test_zero_request_returns_unknown_utilisation():
    result = analyse_resources(
        cpu_request_m=0,
        cpu_usage_m=50,
        memory_request_mib=0,
        memory_usage_mib=100,
    )

    assert result.cpu_utilisation_percent is None
    assert result.memory_utilisation_percent is None


def test_calculates_optional_monthly_cost_estimate():
    result = analyse_resources(
        cpu_request_m=1000,
        cpu_usage_m=500,
        memory_request_mib=1024,
        memory_usage_mib=512,
        cpu_core_hour_rate=0.04,
        memory_gib_hour_rate=0.005,
        hours_per_month=100,
    )

    assert result.requested_monthly_cost == 4.5
    assert result.observed_usage_monthly_cost == 2.25
    assert result.theoretical_monthly_savings == 2.25


def test_cost_rates_must_be_supplied_together():
    with pytest.raises(ValueError, match="supplied together"):
        analyse_resources(
            cpu_request_m=500,
            cpu_usage_m=100,
            memory_request_mib=512,
            memory_usage_mib=128,
            cpu_core_hour_rate=0.04,
        )


@pytest.mark.parametrize(
    "field,value",
    [
        ("cpu_request_m", -1),
        ("cpu_usage_m", -1),
        ("memory_request_mib", -1),
        ("memory_usage_mib", -1),
        ("hours_per_month", -1),
    ],
)
def test_rejects_negative_resource_values(field, value):
    values = {
        "cpu_request_m": 500,
        "cpu_usage_m": 100,
        "memory_request_mib": 512,
        "memory_usage_mib": 128,
        "hours_per_month": 730,
    }
    values[field] = value

    with pytest.raises(ValueError):
        analyse_resources(**values)


def test_to_dict_is_json_friendly():
    result = analyse_resources(
        cpu_request_m=500,
        cpu_usage_m=100,
        memory_request_mib=256,
        memory_usage_mib=128,
    )

    payload = result.to_dict()

    assert payload["cpu_utilisation_percent"] == 20.0
    assert payload["memory_utilisation_percent"] == 50.0