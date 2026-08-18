"""HTTP /metrics endpoint backed by live Kubernetes Metrics API data."""
from __future__ import annotations
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from app.kubernetes_metrics import load_kubernetes_metrics
from app.pipeline import WorkloadInput, run_optimizer

def collect_optimizer_metrics(namespace: str) -> str:
    raw = load_kubernetes_metrics(namespace)
    workloads = [
        WorkloadInput(
            namespace=item.get("namespace", namespace),
            workload=item["pod"],
            cpu_request_m=item["cpu_request"],
            cpu_usage_m=item["cpu_usage"],
            memory_request_mib=item["memory_request"],
            memory_usage_mib=item["memory_usage"],
        )
        for item in raw
    ]
    return run_optimizer(workloads).prometheus_metrics

class MetricsHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        if self.path == "/healthz":
            payload = b"ok\n"
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers(); self.wfile.write(payload); return
        if self.path != "/metrics":
            self.send_response(404); self.end_headers(); return
        namespace = os.getenv("POD_NAMESPACE", "cost-optimizer")
        try:
            payload = collect_optimizer_metrics(namespace).encode("utf-8"); status = 200
        except Exception as exc:
            payload = (
                "# HELP optimizer_metrics_collection_error Whether the latest metrics collection failed.\n"
                "# TYPE optimizer_metrics_collection_error gauge\n"
                "optimizer_metrics_collection_error 1\n"
                f"# collection_error {type(exc).__name__}\n"
            ).encode("utf-8"); status = 500
        self.send_response(status)
        self.send_header("Content-Type", "text/plain; version=0.0.4; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers(); self.wfile.write(payload)
    def log_message(self, format: str, *args) -> None:
        print("%s - - [%s] %s" % (self.address_string(), self.log_date_time_string(), format % args))

def main() -> None:
    host = os.getenv("METRICS_HOST", "0.0.0.0")
    port = int(os.getenv("METRICS_PORT", "8000"))
    server = ThreadingHTTPServer((host, port), MetricsHandler)
    print(f"Optimizer metrics server listening on {host}:{port}")
    server.serve_forever()

if __name__ == "__main__":
    main()