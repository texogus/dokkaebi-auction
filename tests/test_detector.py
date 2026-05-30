import unittest

from auction.detector import (
    UNLIMITED_SALE_LIMIT,
    detect_auction,
    detect_bid_increment,
    is_auction_start,
    is_no_sale_line,
)


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

    def test_angle_limited_sale_is_first_come_quantity_sale(self):
        details = detect_auction("☆<15개한정> 달콩 블루레몬에이드 10개입 1박스 5천원 /")

        self.assertEqual(details.auction_type, "first_come")
        self.assertEqual(details.limit, 15)
        self.assertEqual(details.base_price, 5000)

    def test_angle_limited_sale_accepts_non_gae_units(self):
        details = detect_auction("☆<20세트한정> 스노우 아이스팜 젤리 4봉지 1천원 /")

        self.assertEqual(details.auction_type, "first_come")
        self.assertEqual(details.limit, 20)
        self.assertEqual(details.base_price, 1000)

    def test_angle_limited_sale_accepts_large_limits(self):
        details = detect_auction("☆<1,000박스한정> 테스트 상품 1천원 /")

        self.assertEqual(details.auction_type, "first_come")
        self.assertEqual(details.limit, 1000)
        self.assertEqual(details.base_price, 1000)

    def test_only_auction_prefix_uses_bidding_money_mode(self):
        details = detect_auction("경매>보잉안경/1천출발")

        self.assertEqual(details.auction_type, "bidding")
        self.assertEqual(details.limit, 1)
        self.assertEqual(details.base_price, 1000)

    def test_general_sale_without_limit_is_first_come_with_large_limit(self):
        details = detect_auction("☆ 메가스톰 손선풍기 5천원 (색상 랜덤발송) /")

        self.assertEqual(details.auction_type, "first_come")
        self.assertEqual(details.limit, UNLIMITED_SALE_LIMIT)
        self.assertEqual(details.base_price, 5000)

    def test_decorated_angle_auction_prefix_uses_bidding_money_mode(self):
        details = detect_auction("★<경매> 아이폰6S 6만원 출발 /")

        self.assertEqual(details.auction_type, "bidding")
        self.assertEqual(details.limit, 1)
        self.assertEqual(details.base_price, 60000)

    def test_start_detection_is_explicit(self):
        self.assertTrue(is_auction_start("(2개한정)메라블 앰플 클렌저/8천"))
        self.assertTrue(is_auction_start("(5개한정)>병속의 배/1만"))
        self.assertTrue(is_auction_start("☆<15개한정> 달콩 블루레몬에이드 10개입 1박스 5천원 /"))
        self.assertTrue(is_auction_start("☆<20세트한정> 스노우 아이스팜 젤리 4봉지 1천원 /"))
        self.assertTrue(is_auction_start("☆<1,000박스한정> 테스트 상품 1천원 /"))
        self.assertTrue(is_auction_start("☆ 메가스톰 손선풍기 5천원 (색상 랜덤발송) /"))
        self.assertTrue(is_auction_start("경매>보잉안경/1천출발"))
        self.assertTrue(is_auction_start("★<경매> 아이폰6S 6만원 출발 /"))
        self.assertFalse(is_auction_start("그냥 경매 이야기"))
        self.assertFalse(is_auction_start("경매>세잔선글라스/런처와친구들4만"))
        self.assertFalse(is_auction_start("★<경매> 아이폰6S 64GB입니다"))
        self.assertFalse(is_auction_start("128기가짜리입니다."))
        self.assertFalse(is_auction_start("★<경매> 4GB 램 1천원 출발 / @lazyrich_hobbyrich 1만2천 낙찰"))
        self.assertFalse(is_auction_start("★<경매> 4GB 램 1천원 출발 / 낙찰 완료"))
        self.assertFalse(is_auction_start("(5개한정)>병속의 배/@똔꼬-k2r1@한성호-l8q회원(1개월)1"))
        self.assertFalse(is_auction_start("(5개한정)>병속의 배"))

    def test_no_sale_line_detection(self):
        self.assertTrue(is_no_sale_line("--------유찰--------"))
        self.assertFalse(is_no_sale_line("--------낙찰선--------"))

    def test_bid_increment_detection(self):
        self.assertEqual(detect_bid_increment("1만원단위입찰"), 1)
        self.assertEqual(detect_bid_increment("10만원 단위 입찰"), 10)
        self.assertEqual(detect_bid_increment("5천원단위입찰"), 0.5)
        self.assertEqual(detect_bid_increment("1천원 단위 입찰"), 0.1)
        self.assertIsNone(detect_bid_increment("64GB입니다"))


if __name__ == "__main__":
    unittest.main()
