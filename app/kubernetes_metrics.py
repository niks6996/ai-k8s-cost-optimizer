from decimal import Decimal

CPU_SUFFIXES = {"n": Decimal("0.000001"), "u": Decimal("0.001"), "m": Decimal("1")}
MEMORY_SUFFIXES = {
    "Ki": Decimal(1) / Decimal(1024), "Mi": Decimal(1),
    "Gi": Decimal(1024), "Ti": Decimal(1024 * 1024),
}

def parse_cpu_to_millicores(value):
    value = str(value).strip()
    for suffix, multiplier in CPU_SUFFIXES.items():
        if value.endswith(suffix):
            return float(Decimal(value[:-len(suffix)]) * multiplier)
    return float(Decimal(value) * Decimal(1000))

def parse_memory_to_mib(value):
    value = str(value).strip()
    for suffix, multiplier in MEMORY_SUFFIXES.items():
        if value.endswith(suffix):
            return float(Decimal(value[:-len(suffix)]) * multiplier)
    return float(Decimal(value) / Decimal(1024 * 1024))

def _sum_container_requests(pod):
    cpu = 0.0
    memory = 0.0
    for container in pod.spec.containers:
        requests = container.resources.requests or {}
        if "cpu" in requests:
            cpu += parse_cpu_to_millicores(requests["cpu"])
        if "memory" in requests:
            memory += parse_memory_to_mib(requests["memory"])
    return cpu, memory

def _index_pod_metrics(payload):
    indexed = {}
    for pod_metric in payload.get("items", []):
        cpu = 0.0
        memory = 0.0
        for container in pod_metric.get("containers", []):
            usage = container.get("usage", {})
            if "cpu" in usage:
                cpu += parse_cpu_to_millicores(usage["cpu"])
            if "memory" in usage:
                memory += parse_memory_to_mib(usage["memory"])
        indexed[pod_metric["metadata"]["name"]] = {
            "cpu_usage": cpu, "memory_usage": memory
        }
    return indexed

def build_metrics_from_api_data(pods, metrics_payload, namespace):
    indexed = _index_pod_metrics(metrics_payload)
    workloads = []
    for pod in pods:
        name = pod.metadata.name
        if name not in indexed:
            print(f"No Metrics API data available for pod: {name}")
            continue
        cpu_request, memory_request = _sum_container_requests(pod)
        usage = indexed[name]
        workloads.append({
            "pod": name,
            "namespace": namespace,
            "cpu_request": round(cpu_request, 4),
            "cpu_usage": round(usage["cpu_usage"], 4),
            "memory_request": round(memory_request, 4),
            "memory_usage": round(usage["memory_usage"], 4),
        })
    return workloads

def load_kubernetes_metrics(namespace):
    from kubernetes import client, config
    config.load_incluster_config()
    core_api = client.CoreV1Api()
    custom_api = client.CustomObjectsApi()
    pods = core_api.list_namespaced_pod(namespace=namespace)
    metrics = custom_api.list_namespaced_custom_object(
        group="metrics.k8s.io",
        version="v1beta1",
        namespace=namespace,
        plural="pods",
    )
    return build_metrics_from_api_data(pods.items, metrics, namespace)