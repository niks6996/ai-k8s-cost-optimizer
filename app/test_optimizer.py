import unittest

from optimizer import (
    analyse_metrics,
    calculate_percentage,
    generate_recommendations,
    validate_workload,
)


class TestOptimizer(unittest.TestCase):

    def test_calculate_percentage(self):
        self.assertEqual(calculate_percentage(100, 500), 20)

    def test_calculate_percentage_with_zero_request(self):
        self.assertEqual(calculate_percentage(100, 0), 0)

    def test_validate_complete_workload(self):
        workload = {
            "pod": "frontend-app",
            "cpu_request": 500,
            "cpu_usage": 100,
            "memory_request": 512,
            "memory_usage": 200,
        }

        self.assertTrue(validate_workload(workload))

    def test_validate_incomplete_workload(self):
        workload = {
            "pod": "frontend-app",
            "cpu_request": 500,
        }

        self.assertFalse(validate_workload(workload))

    def test_generate_overprovisioning_recommendations(self):
        workload = {
            "pod": "frontend-app",
            "cpu_request": 500,
            "cpu_usage": 100,
            "memory_request": 512,
            "memory_usage": 200,
        }

        result = generate_recommendations(workload)

        self.assertEqual(result["pod"], "frontend-app")
        self.assertIn("Reduce CPU requests", result["recommendations"])
        self.assertIn("Reduce memory requests", result["recommendations"])

    def test_analyse_metrics_skips_invalid_workload(self):
        metrics = [
            {
                "pod": "valid-app",
                "cpu_request": 500,
                "cpu_usage": 100,
                "memory_request": 512,
                "memory_usage": 200,
            },
            {
                "pod": "invalid-app",
                "cpu_request": 500,
            },
        ]

        results = analyse_metrics(metrics)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["pod"], "valid-app")


if __name__ == "__main__":
    unittest.main()
