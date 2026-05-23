import unittest

from auction.workbook import HEADERS, init_workbook


class WorkbookTest(unittest.TestCase):
    def test_order_sheet_uses_full_header_names(self):
        workbook, sheet = init_workbook()
        try:
            headers = [sheet.cell(row=1, column=index).value for index in range(1, len(HEADERS) + 1)]
            self.assertEqual(headers[1], "번호")
            self.assertEqual(headers[4], "수량")
        finally:
            workbook.close()


if __name__ == "__main__":
    unittest.main()
