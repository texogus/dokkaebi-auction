import unittest

from auction.identity import display_id, normalize_id


class IdentityTest(unittest.TestCase):
    def test_normalize_id_matches_member_ids_without_at(self):
        self.assertEqual(normalize_id("@진격의거이"), "진격의거이")
        self.assertEqual(normalize_id("진격의거이"), "진격의거이")

    def test_display_id_removes_at_for_order_sheet(self):
        self.assertEqual(display_id("@진격의거이"), "진격의거이")
        self.assertEqual(display_id("진격의거이"), "진격의거이")
        self.assertEqual(display_id("  @서원상-k6e "), "서원상-k6e")


if __name__ == "__main__":
    unittest.main()
