from app.metrics_server import collect_optimizer_metrics

def test_collect_optimizer_metrics_connects_collector_to_pipeline(monkeypatch):
    monkeypatch.setattr(
        "app.metrics_server.load_kubernetes_metrics",
        lambda namespace: [{
            "pod": "sample-workload", "namespace": namespace,
            "cpu_request": 500, "cpu_usage": 100,
            "memory_request": 512, "memory_usage": 128,
        }],
    )
    payload = collect_optimizer_metrics("cost-optimizer")
    assert "optimizer_workloads_analyzed_total 1.0" in payload
    assert 'status="over_provisioned"' in payload
    assert "optimizer_recommended_cpu_request_millicores" in payload
    assert "optimizer_recommended_memory_request_mib" in payload