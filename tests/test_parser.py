import unittest

from auction.parser import parse_number, parse_qty


class ParserTest(unittest.TestCase):
    def test_parse_number_accepts_decimal_bid_variants(self):
        for raw in [",5", "..5", "0,5", ",,5", "0,,5", "0..5"]:
            with self.subTest(raw=raw):
                self.assertEqual(parse_number(raw), 0.5)

    def test_parse_qty_rejects_decimal_bid_variants(self):
        for raw in [",5", "..5", "0,5", ",,5", "0,,5", "0..5"]:
            with self.subTest(raw=raw):
                self.assertIsNone(parse_qty(raw))


if __name__ == "__main__":
    unittest.main()
