import tempfile
import unittest
from pathlib import Path

import openpyxl

from auction.config import Settings
from auction.members import load_members


class MembersTest(unittest.TestCase):
    def test_load_members_finds_header_row_below_title(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "members.xlsx"
            workbook = openpyxl.Workbook()
            sheet = workbook.active
            sheet.append(["", "회원 등록", "", "", ""])
            sheet.append(["", "NO", "아이디", "고객명", "연락처", "주소"])
            sheet.append(["", 1, "진격의거이", "김지산", "01012345678", "서울"])
            workbook.save(path)
            workbook.close()

            settings = Settings(
                api_key="x",
                video_id="x",
                member_file=str(path),
                blocked_file="missing.xlsx",
                col_id="아이디",
                col_name="고객명",
                col_phone="연락처",
                col_address="주소",
                host_keyword="만물도깨비",
                poll_sec=6,
                sort_by_name=True,
                output_dir=temp_dir,
            )

            members = load_members(settings)
            self.assertIn("진격의거이", members)
            self.assertEqual(members["진격의거이"].customer_name, "김지산")


if __name__ == "__main__":
    unittest.main()
