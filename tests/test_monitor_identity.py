import unittest

from auction.identity import display_id, normalize_id
from auction.winner import Bid


class MonitorIdentityTest(unittest.TestCase):
    def test_youtube_display_name_is_cleaned_before_bid_logging(self):
        display_name = display_id("@진격의거이")
        bid = Bid(time_text="10:00 AM", uid=normalize_id(display_name), display_name=display_name, value=0.6)

        self.assertEqual(bid.uid, "진격의거이")
        self.assertEqual(bid.display_name, "진격의거이")


if __name__ == "__main__":
    unittest.main()
