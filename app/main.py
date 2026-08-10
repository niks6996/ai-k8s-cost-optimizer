import json
import os
from pathlib import Path
from optimizer import analyse_metrics, save_recommendations

APP_DIR = Path(__file__).resolve().parent

def load_mock_metrics():
    with (APP_DIR / "metrics.json").open("r", encoding="utf-8") as file:
        return json.load(file)

def load_metrics():
    source = os.getenv("METRICS_SOURCE", "mock").strip().lower()
    if source == "mock":
        print("Metrics source: mock JSON")
        return load_mock_metrics()
    if source == "kubernetes":
        from kubernetes_metrics import load_kubernetes_metrics
        namespace = os.getenv("POD_NAMESPACE", "cost-optimizer")
        print(f"Metrics source: Kubernetes API (namespace={namespace})")
        return load_kubernetes_metrics(namespace)
    raise ValueError("METRICS_SOURCE must be 'mock' or 'kubernetes'")

def main():
    metrics = load_metrics()
    results = analyse_metrics(metrics)
    save_recommendations(results)

if __name__ == "__main__":
    main()