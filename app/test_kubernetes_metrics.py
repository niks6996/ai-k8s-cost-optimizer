import unittest
from types import SimpleNamespace
from kubernetes_metrics import build_metrics_from_api_data, parse_cpu_to_millicores, parse_memory_to_mib

def make_pod(name, requests):
    containers = [
        SimpleNamespace(resources=SimpleNamespace(requests=item))
        for item in requests
    ]
    return SimpleNamespace(
        metadata=SimpleNamespace(name=name),
        spec=SimpleNamespace(containers=containers),
    )

class TestKubernetesMetrics(unittest.TestCase):
    def test_cpu_conversion(self):
        self.assertEqual(parse_cpu_to_millicores("250m"), 250)
        self.assertEqual(parse_cpu_to_millicores("1"), 1000)
        self.assertEqual(parse_cpu_to_millicores("50000000n"), 50)

    def test_memory_conversion(self):
        self.assertEqual(parse_memory_to_mib("128Mi"), 128)
        self.assertEqual(parse_memory_to_mib("1Gi"), 1024)
        self.assertEqual(parse_memory_to_mib("65536Ki"), 64)

    def test_combines_container_metrics(self):
        pods = [make_pod("frontend", [
            {"cpu": "100m", "memory": "128Mi"},
            {"cpu": "50m", "memory": "64Mi"},
        ])]
        payload = {"items": [{
            "metadata": {"name": "frontend"},
            "containers": [
                {"usage": {"cpu": "40000000n", "memory": "80Mi"}},
                {"usage": {"cpu": "10000000n", "memory": "32Mi"}},
            ],
        }]}
        result = build_metrics_from_api_data(pods, payload, "cost-optimizer")
        self.assertEqual(result[0]["cpu_request"], 150)
        self.assertEqual(result[0]["cpu_usage"], 50)
        self.assertEqual(result[0]["memory_request"], 192)
        self.assertEqual(result[0]["memory_usage"], 112)

if __name__ == "__main__":
    unittest.main()