import json


def load_metrics(file_path):
    with open(file_path, "r") as file:
        return json.load(file)


def calculate_percentage(usage, request):
    return (usage / request) * 100


def analyse_workloads(metrics):

    for workload in metrics:

        pod_name = workload["pod"]

        cpu_request = workload["cpu_request"]
        cpu_usage = workload["cpu_usage"]

        memory_request = workload["memory_request"]
        memory_usage = workload["memory_usage"]

        cpu_percentage = calculate_percentage(cpu_usage, cpu_request)
        memory_percentage = calculate_percentage(memory_usage, memory_request)

        print(f"\nAnalysing pod: {pod_name}")

        print(f"CPU Usage: {cpu_percentage:.2f}%")
        print(f"Memory Usage: {memory_percentage:.2f}%")

        if cpu_percentage < 40:
            print("CPU appears over-provisioned")

        if memory_percentage < 50:
            print("Memory appears over-provisioned")

        if cpu_percentage > 90:
            print("WARNING: CPU usage is very high")

        if memory_percentage > 90:
            print("WARNING: Memory usage is very high")


def main():

    metrics = load_metrics("metrics.json")

    analyse_workloads(metrics)


if __name__ == "__main__":
    main()