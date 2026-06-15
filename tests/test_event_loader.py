import unittest

from services.event_loader import load_events


class TestEventLoaderFilters(unittest.TestCase):
    def test_live_category_counts(self):
        self.assertEqual(load_events(log="live", limit=500)["filtered_total"], 100)
        self.assertEqual(
            load_events(log="live", limit=500, category="normal")["filtered_total"], 80
        )
        self.assertEqual(
            load_events(log="live", limit=500, category="corrupted")["filtered_total"], 10
        )
        self.assertEqual(
            load_events(log="live", limit=500, category="interrupted")["filtered_total"], 10
        )

    def test_replay_category_counts(self):
        self.assertEqual(load_events(log="replay", limit=500)["filtered_total"], 101)
        self.assertEqual(
            load_events(log="replay", limit=500, category="normal")["filtered_total"], 80
        )

    def test_recovery_interrupted_candidates(self):
        self.assertEqual(load_events(log="recovery", limit=500)["filtered_total"], 11)
        self.assertEqual(
            load_events(log="recovery", limit=500, category="interrupted")[
                "filtered_total"
            ],
            10,
        )

    def test_event_type_alias(self):
        live_normal = load_events(log="live", limit=500, event_type="normal")
        cat_normal = load_events(log="live", limit=500, category="normal")
        self.assertEqual(
            live_normal["filtered_total"], cat_normal["filtered_total"]
        )

    def test_mode_alias(self):
        live = load_events(mode="live", limit=500)
        self.assertEqual(live["log"], "live")
        self.assertGreater(live["filtered_total"], 0)

    def test_validation_filter(self):
        valid = load_events(log="live", limit=500, status="VALID")
        invalid = load_events(log="live", limit=500, status="INVALID")
        self.assertEqual(valid["filtered_total"], 90)
        self.assertEqual(invalid["filtered_total"], 10)


if __name__ == "__main__":
    unittest.main()
