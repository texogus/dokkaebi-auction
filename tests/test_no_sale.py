import unittest

from auction.detector import is_no_sale_line
from auction.parser import is_bid_message
from auction.winner import Bid


class NoSaleTest(unittest.TestCase):
    def test_no_sale_closes_current_sale_before_later_numbers(self):
        in_auction = True
        bids = [Bid(time_text="08:00 PM", uid="jin", display_name="진격의거이", value=0.5)]

        if is_no_sale_line("--------유찰--------"):
            in_auction = False
            bids = []

        if in_auction and is_bid_message("1"):
            bids.append(Bid(time_text="08:01 PM", uid="late", display_name="늦은댓글", value=1))

        self.assertFalse(in_auction)
        self.assertEqual(bids, [])


if __name__ == "__main__":
    unittest.main()
