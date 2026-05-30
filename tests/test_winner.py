import unittest

from auction.winner import Bid, determine_winners
from auction.monitor import _normalize_bid_value


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

    def test_first_come_limited_sale_fills_by_requested_quantities(self):
        bids = [
            Bid("07:54 PM", "한태희-f1h", "한태희-f1h", 5),
            Bid("07:55 PM", "이석문-b4g", "이석문-b4g", 5),
            Bid("07:56 PM", "whisunglee8585", "whisunglee8585", 2),
            Bid("07:57 PM", "jay-sx5nz", "Jay-sx5nz", 1),
            Bid("07:58 PM", "lmas0623", "Lmas0623", 1),
            Bid("07:59 PM", "최규영-j6l", "최규영-j6l", 1),
            Bid("08:00 PM", "이정희-r6v7x", "이정희-r6v7x", 1),
        ]

        winners = determine_winners(bids, "first_come", 15)

        self.assertEqual(
            [(winner.uid, winner.value) for winner in winners],
            [
                ("한태희-f1h", 5),
                ("이석문-b4g", 5),
                ("whisunglee8585", 2),
                ("jay-sx5nz", 1),
                ("lmas0623", 1),
                ("최규영-j6l", 1),
            ],
        )

    def test_first_come_limited_sale_trims_last_quantity_to_remaining_limit(self):
        bids = [
            Bid("07:54 PM", "a", "A", 10),
            Bid("07:55 PM", "b", "B", 5),
            Bid("07:56 PM", "c", "C", 1),
        ]

        winners = determine_winners(bids, "first_come", 12)

        self.assertEqual(
            [(winner.uid, winner.value) for winner in winners],
            [("a", 10), ("b", 2)],
        )

    def test_compact_decimal_bid_does_not_beat_higher_decimal_bid(self):
        bids = [
            Bid("", "충청도고양이들cccats", "충청도고양이들Cccats", _normalize_bid_value(7.0, 60000)),
            Bid("", "김원식-q6e9r", "김원식-q6e9r", _normalize_bid_value(7.5, 60000)),
            Bid("", "남이용호-m6q", "남이용호-m6q", _normalize_bid_value(65, 60000)),
            Bid("", "hwacho_go", "HwaCho_go", _normalize_bid_value(7.1, 60000)),
        ]

        winners = determine_winners(bids, "bidding", 1)

        self.assertEqual(winners[0].uid, "김원식-q6e9r")
        self.assertEqual(winners[0].value, 7.5)

    def test_low_start_auction_keeps_18_as_18_manwon_winner(self):
        bids = [
            Bid("", "onedol73", "onedol73", _normalize_bid_value(18, 1000)),
            Bid("", "les_paul_3", "Les_Paul_3", _normalize_bid_value(15, 1000)),
            Bid("", "밤도깨비-b9c", "밤도깨비-b9c", _normalize_bid_value(16, 1000)),
            Bid("", "남임기호-w3i", "남임기호-w3i", _normalize_bid_value(17, 1000)),
        ]

        winners = determine_winners(bids, "bidding", 1)

        self.assertEqual(winners[0].uid, "onedol73")
        self.assertEqual(winners[0].value, 18)

    def test_bidding_tie_uses_first_bid_that_reached_the_highest_price(self):
        bids = [
            Bid("", "문돈사랑-e5g", "문돈사랑-e5g", _normalize_bid_value(5.5, 50000)),
            Bid("", "눈이큰아이-h6f", "눈이큰아이-h6f", _normalize_bid_value(7, 50000)),
            Bid("", "김문현-l2e", "김문현-l2e", _normalize_bid_value(6, 50000)),
            Bid("", "문돈사랑-e5g", "문돈사랑-e5g", _normalize_bid_value(7, 50000)),
        ]

        winners = determine_winners(bids, "bidding", 1)

        self.assertEqual(winners[0].uid, "눈이큰아이-h6f")
        self.assertEqual(winners[0].value, 7)

    def test_bidding_tie_uses_youtube_published_time_not_api_arrival_order(self):
        bids = [
            Bid(
                "",
                "김현정-g4e2c",
                "김현정-g4e2c",
                11,
                published_at="2026-05-27T04:59:13.900Z",
                sequence=1,
            ),
            Bid(
                "",
                "영미이-k6l",
                "영미이-k6l",
                11,
                published_at="2026-05-27T04:59:13.800Z",
                sequence=2,
            ),
        ]

        winners = determine_winners(bids, "bidding", 1)

        self.assertEqual(winners[0].uid, "영미이-k6l")

    def test_first_come_uses_youtube_published_time_not_api_arrival_order(self):
        bids = [
            Bid("", "second", "second", 1, published_at="2026-05-27T04:59:14Z", sequence=1),
            Bid("", "first", "first", 1, published_at="2026-05-27T04:59:13Z", sequence=2),
        ]

        winners = determine_winners(bids, "first_come", 1)

        self.assertEqual(winners[0].uid, "first")

    def test_bidding_ignores_single_extreme_high_outlier(self):
        bids = [
            Bid("", "점점점-t9b", "점점점-t9b", 8),
            Bid("", "onedol73", "onedol73", 735),
            Bid("", "런처와친구들", "런처와친구들", 8),
            Bid("", "이슬독사", "이슬독사", 9),
            Bid("", "엄마는외계인-x4b", "엄마는외계인-x4b", 8),
        ]

        winners = determine_winners(bids, "bidding", 1)

        self.assertEqual(winners[0].uid, "이슬독사")
        self.assertEqual(winners[0].value, 9)

    def test_bidding_ignores_single_decimal_extreme_high_outlier(self):
        bids = [
            Bid("", "점점점-t9b", "점점점-t9b", 8),
            Bid("", "onedol73", "onedol73", 73.5),
            Bid("", "런처와친구들", "런처와친구들", 8),
            Bid("", "이슬독사", "이슬독사", 9),
        ]

        winners = determine_winners(bids, "bidding", 1)

        self.assertEqual(winners[0].uid, "이슬독사")
        self.assertEqual(winners[0].value, 9)

    def test_bidding_allows_high_price_when_other_bids_are_nearby(self):
        bids = [
            Bid("", "a", "a", 900),
            Bid("", "b", "b", 1000),
            Bid("", "c", "c", 1100),
        ]

        winners = determine_winners(bids, "bidding", 1)

        self.assertEqual(winners[0].uid, "c")
        self.assertEqual(winners[0].value, 1100)


if __name__ == "__main__":
    unittest.main()
