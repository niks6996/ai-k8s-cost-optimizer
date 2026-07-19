import json


CPU_OVERPROVISION_THRESHOLD = 40
MEMORY_OVERPROVISION_THRESHOLD = 50

CPU_HIGH_THRESHOLD = 90
MEMORY_HIGH_THRESHOLD = 90


def calculate_percentage(usage, request):

    if request == 0:
        return 0

    return (usage / request) * 100


def validate_workload(workload):

    required_fields = [
        "pod",
        "cpu_request",
        "cpu_usage",
        "memory_request",
        "memory_usage"
    ]

    for field in required_fields:

        if field not in workload:
            return False

    return True


def generate_recommendations(workload):

    recommendations = []

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

    if cpu_percentage < CPU_OVERPROVISION_THRESHOLD:

        recommendations.append(
            "Reduce CPU requests"
        )

    if memory_percentage < MEMORY_OVERPROVISION_THRESHOLD:

        recommendations.append(
            "Reduce memory requests"
        )

    if cpu_percentage > CPU_HIGH_THRESHOLD:

        recommendations.append(
            "WARNING: High CPU usage"
        )

    if memory_percentage > MEMORY_HIGH_THRESHOLD:

        recommendations.append(
            "WARNING: High memory usage"
        )

    return {
        "pod": pod_name,
        "cpu_usage_percentage": round(cpu_percentage, 2),
        "memory_usage_percentage": round(memory_percentage, 2),
        "recommendations": recommendations
    }


def analyse_metrics(metrics):

    results = []

    for workload in metrics:

        if not validate_workload(workload):

            print("Invalid workload data detected")
            continue

        recommendation = generate_recommendations(workload)

        results.append(recommendation)

    return results


def save_recommendations(results):

    with open("recommendations.json", "w") as file:

        json.dump(results, file, indent=4)

    print("\nRecommendations saved successfully")