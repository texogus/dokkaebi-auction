import unittest

from auction.detector import is_auction_start


class ProductConsistencyTest(unittest.TestCase):
    def test_high_bid_status_line_does_not_replace_started_product(self):
        product_name = "경매>세잔선글라스/1만출발"
        in_auction = is_auction_start(product_name)
        status_line = "경매>세잔선글라스/런처와친구들4만"

        if in_auction and is_auction_start(status_line):
            product_name = status_line

        self.assertEqual(product_name, "경매>세잔선글라스/1만출발")


if __name__ == "__main__":
    unittest.main()
