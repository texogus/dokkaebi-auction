import unittest

from auction.detector import is_auction_start, is_winning_line
from auction.parser import is_bid_message, parse_number
from auction.winner import Bid


class CloseNoticeTest(unittest.TestCase):
    def test_winning_notice_does_not_open_new_auction_for_later_numbers(self):
        in_auction = True
        bids = [Bid("11:00 AM", "winner", "winner", 1.2)]

        if is_winning_line("--------낙찰선--------"):
            in_auction = False
            bids = []

        notice = "★<경매> 4GB 램 1천원 출발 / @lazyrich_hobbyrich 1만2천 낙찰"
        if is_auction_start(notice):
            in_auction = True
            bids = []

        if in_auction and is_bid_message("100"):
            value = parse_number("100")
            if value is not None:
                bids.append(Bid("11:01 AM", "박자영-v8o", "박자영-v8o", value))

        self.assertFalse(in_auction)
        self.assertEqual(bids, [])


if __name__ == "__main__":
    unittest.main()
