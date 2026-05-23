import unittest

from auction.detector import detect_auction, is_auction_start, is_no_sale_line


class DetectorTest(unittest.TestCase):
    def test_parenthesized_limited_sale_is_first_come(self):
        details = detect_auction("(2개한정)메라블 앰플 클렌저/8천")

        self.assertEqual(details.auction_type, "first_come")
        self.assertEqual(details.limit, 2)
        self.assertEqual(details.base_price, 8000)

    def test_bracketed_limited_sale_is_first_come(self):
        details = detect_auction("[3개한정]양말/5천")

        self.assertEqual(details.auction_type, "first_come")
        self.assertEqual(details.limit, 3)
        self.assertEqual(details.base_price, 5000)

    def test_limited_sale_with_arrow_and_man_price_is_first_come(self):
        details = detect_auction("(5개한정)>병속의 배/1만")

        self.assertEqual(details.auction_type, "first_come")
        self.assertEqual(details.limit, 5)
        self.assertEqual(details.base_price, 10000)

    def test_only_auction_prefix_uses_bidding_money_mode(self):
        details = detect_auction("경매>보잉안경/1천출발")

        self.assertEqual(details.auction_type, "bidding")
        self.assertEqual(details.limit, 1)
        self.assertEqual(details.base_price, 1000)

    def test_start_detection_is_explicit(self):
        self.assertTrue(is_auction_start("(2개한정)메라블 앰플 클렌저/8천"))
        self.assertTrue(is_auction_start("(5개한정)>병속의 배/1만"))
        self.assertTrue(is_auction_start("경매>보잉안경/1천출발"))
        self.assertFalse(is_auction_start("그냥 경매 이야기"))
        self.assertFalse(is_auction_start("경매>세잔선글라스/런처와친구들4만"))
        self.assertFalse(is_auction_start("(5개한정)>병속의 배/@똔꼬-k2r1@한성호-l8q회원(1개월)1"))
        self.assertFalse(is_auction_start("(5개한정)>병속의 배"))

    def test_no_sale_line_detection(self):
        self.assertTrue(is_no_sale_line("--------유찰--------"))
        self.assertFalse(is_no_sale_line("--------낙찰선--------"))


if __name__ == "__main__":
    unittest.main()
