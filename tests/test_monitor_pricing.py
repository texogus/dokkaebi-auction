import unittest

from auction.monitor import _is_valid_bid_increment, _normalize_bid_value, _price_and_quantity


class MonitorPricingTest(unittest.TestCase):
    def test_bidding_numbers_are_always_manwon_units(self):
        cases = [
            (0.5, 5000),
            (9.5, 95000),
            (18, 180000),
            (100, 1000000),
        ]

        for bid_value, expected_price in cases:
            with self.subTest(bid_value=bid_value):
                price, quantity = _price_and_quantity("bidding", bid_value, 0)
                self.assertEqual(price, expected_price)
                self.assertEqual(quantity, 1)

    def test_first_come_uses_base_price_and_bid_value_as_quantity(self):
        price, quantity = _price_and_quantity("first_come", 3, 8000)

        self.assertEqual(price, 8000)
        self.assertEqual(quantity, 3)

    def test_sub_100000_start_accepts_compact_decimal_bids(self):
        self.assertEqual(_normalize_bid_value(65, 60000), 6.5)
        self.assertEqual(_normalize_bid_value(75, 60000), 7.5)
        self.assertEqual(_normalize_bid_value(10, 60000), 10)

    def test_very_low_start_keeps_full_manwon_bids(self):
        self.assertEqual(_normalize_bid_value(15, 1000), 15)
        self.assertEqual(_normalize_bid_value(18, 1000), 18)
        self.assertEqual(_normalize_bid_value(20, 1000), 20)

    def test_100000_or_higher_start_keeps_full_manwon_bids(self):
        self.assertEqual(_normalize_bid_value(18, 150000), 18)
        self.assertEqual(_normalize_bid_value(100, 150000), 100)

    def test_bid_increment_validation(self):
        self.assertTrue(_is_valid_bid_increment(26, 1))
        self.assertFalse(_is_valid_bid_increment(26.5, 1))
        self.assertTrue(_is_valid_bid_increment(26.5, 0.5))
        self.assertTrue(_is_valid_bid_increment(26.1, 0.1))
        self.assertFalse(_is_valid_bid_increment(26.15, 0.1))


if __name__ == "__main__":
    unittest.main()
