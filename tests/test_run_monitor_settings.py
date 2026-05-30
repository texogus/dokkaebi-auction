import unittest

from auction.run_monitor import _settings_from_payload


class RunMonitorSettingsTest(unittest.TestCase):
    def test_polling_interval_is_never_below_15_seconds(self):
        settings = _settings_from_payload({"poll_sec": 6})

        self.assertEqual(settings.poll_sec, 15)

    def test_polling_interval_can_be_higher_than_15_seconds(self):
        settings = _settings_from_payload({"poll_sec": 30})

        self.assertEqual(settings.poll_sec, 30)


if __name__ == "__main__":
    unittest.main()
