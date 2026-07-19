import json

from optimizer import (
    analyse_metrics,
    save_recommendations
)


def load_metrics(file_path):

    with open(file_path, "r") as file:

        return json.load(file)


def main():

    try:

        metrics = load_metrics("metrics.json")

        results = analyse_metrics(metrics)

        save_recommendations(results)

    except FileNotFoundError:

        print("Metrics file not found")

    except json.JSONDecodeError:

        print("Invalid JSON format detected")

    except Exception as error:

        print(f"Unexpected error: {error}")


if __name__ == "__main__":
    main()