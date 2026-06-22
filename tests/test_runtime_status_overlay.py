import unittest

from services.runtime_console_service import _should_overlay_verify_truth


class TestRuntimeStatusOverlay(unittest.TestCase):
    def test_overlay_when_verify_is_newer(self):
        self.assertTrue(
            _should_overlay_verify_truth(
                report_truth="TRUTH_VERIFIED",
                report_updated="2026-01-01T10:00:00+00:00",
                verify_completed_at="2026-01-01T11:00:00+00:00",
            )
        )

    def test_no_overlay_when_report_is_newer(self):
        self.assertFalse(
            _should_overlay_verify_truth(
                report_truth="TRUTH_VERIFIED",
                report_updated="2026-01-01T12:00:00+00:00",
                verify_completed_at="2026-01-01T11:00:00+00:00",
            )
        )

    def test_overlay_when_report_truth_missing(self):
        self.assertTrue(
            _should_overlay_verify_truth(
                report_truth="NOT_RUN",
                report_updated="2026-01-01T12:00:00+00:00",
                verify_completed_at="2026-01-01T11:00:00+00:00",
            )
        )


if __name__ == "__main__":
    unittest.main()
