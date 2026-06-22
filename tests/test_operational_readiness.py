import unittest

from observability.health_monitor import HealthMonitor
from observability.startup_validator import StartupValidator


class TestOperationalReadiness(unittest.TestCase):
    def test_startup_validator(self):
        result = StartupValidator.validate()
        self.assertIn("ready", result)
        self.assertIn("checks", result)
        self.assertTrue(result["checks"]["persistence_available"])
        self.assertTrue(result["checks"]["configuration_valid"])

    def test_health_monitor(self):
        result = HealthMonitor.get_status()
        for key in (
            "overall",
            "runtime_health",
            "replay_health",
            "persistence_health",
            "recovery_health",
        ):
            self.assertIn(key, result)


if __name__ == "__main__":
    unittest.main()
