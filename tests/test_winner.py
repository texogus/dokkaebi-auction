import unittest

from auction.winner import Bid, determine_winners


class WinnerTest(unittest.TestCase):
    def test_first_come_limited_sale_uses_comment_numbers_as_quantities(self):
        bids = [
            Bid("07:54 PM", "psw-ys3ru", "PSW-ys3ru", 1),
            Bid("07:55 PM", "레오-h4m", "레오-h4m", 1),
            Bid("07:56 PM", "진격의거이", "진격의거이", 1),
            Bid("07:57 PM", "허니-t9z9t", "허니-t9z9t", 2),
        ]

        winners = determine_winners(bids, "first_come", 2)

        self.assertEqual([winner.uid for winner in winners], ["psw-ys3ru", "레오-h4m"])
        self.assertEqual([winner.value for winner in winners], [1, 1])


if __name__ == "__main__":
    unittest.main()
