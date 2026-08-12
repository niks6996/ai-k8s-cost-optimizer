import json
from app.pipeline import WorkloadInput, run_optimizer

def test_end_to_end_pipeline():
    result = run_optimizer([WorkloadInput("cost-optimizer","sample",500,100,512,128)])
    w = result.workloads[0]
    assert w.analysis["cpu_utilisation_percent"] == 20.0
    assert w.recommendation["status"] == "over_provisioned"
    assert w.recommendation["recommended_cpu_request_m"] == 130.0
    assert "optimizer_workloads_analyzed_total 1.0" in result.prometheus_metrics

def test_multiple_workloads():
    result = run_optimizer([
        WorkloadInput("a","over",1000,100,1024,100),
        WorkloadInput("a","healthy",500,300,512,300),
        WorkloadInput("b","under",200,195,256,250),
    ])
    assert [w.recommendation["status"] for w in result.workloads] == [
        "over_provisioned","healthy","under_provisioned"
    ]
    assert "optimizer_workloads_analyzed_total 3.0" in result.prometheus_metrics

def test_cost_flows_through_pipeline():
    result = run_optimizer([WorkloadInput(
        "cost-optimizer","priced",1000,500,1024,512,0.04,0.005)])
    a = result.workloads[0].analysis
    assert a["requested_monthly_cost"] == 32.85
    assert a["observed_usage_monthly_cost"] == 16.425
    assert a["theoretical_monthly_savings"] == 16.425

def test_json_serialisable():
    payload = run_optimizer([WorkloadInput("n","w",500,100,512,128)]).to_dict()
    assert '"workloads"' in json.dumps(payload)

def test_empty_list():
    result = run_optimizer([])
    assert result.workloads == []
    assert "optimizer_workloads_analyzed_total 0.0" in result.prometheus_metrics