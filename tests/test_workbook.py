import unittest

from auction.members import Member
from auction.workbook import HEADERS, OrderRow, init_workbook, write_order_row


class WorkbookTest(unittest.TestCase):
    def test_order_sheet_uses_full_header_names(self):
        workbook, sheet = init_workbook()
        try:
            headers = [sheet.cell(row=1, column=index).value for index in range(1, len(HEADERS) + 1)]
            self.assertEqual(headers[1], "번호")
            self.assertEqual(headers[4], "수량")
        finally:
            workbook.close()

    def test_order_sheet_writes_id_value_without_extra_formatting(self):
        workbook, sheet = init_workbook()
        try:
            order = OrderRow(
                time_text="10:00 AM",
                sequence=1,
                product="테스트 상품",
                price=5000,
                quantity=1,
                uid="진격의거이",
                member=Member(customer_name="김지산", phone="", address=""),
                is_member=True,
                is_blocked=False,
                is_duplicate=False,
                notes="",
                auction_type="bidding",
            )
            write_order_row(sheet, 2, order)
            self.assertEqual(sheet.cell(row=2, column=7).value, "진격의거이")
        finally:
            workbook.close()


if __name__ == "__main__":
    unittest.main()
