import locate
import unittest

with locate.prepend_sys_path(".."):
    from proactuary._util import excel_to_datetime_template


class TestExcelToPythonDateTemplate(unittest.TestCase):
    def test_yyyy_mm_dd(self):
        self.assertEqual(excel_to_datetime_template("yyyy/mm/dd"), "%Y/%m/%d")

    def test_dd_mm_yyyy_hh_mm_ss(self):
        self.assertEqual(
            excel_to_datetime_template("dd-mm-yyyy hh:mm:ss"), "%d-%m-%Y %H:%M:%S"
        )

    def test_dd_mm_yy_h_m_s_AM_PM(self):
        self.assertEqual(
            excel_to_datetime_template("dd/mm/yy h:m:s AM/PM"),
            "%d/%m/%y %-I:%-M:%-S %p",
        )

    def test_h_m_s_dd_mm_yyyy(self):
        self.assertEqual(
            excel_to_datetime_template("h:m:s dd/mm/yyyy"), "%-H:%-M:%-S %d/%m/%Y"
        )

    def test_s_m_h_dd_mm_yyyy(self):
        self.assertEqual(
            excel_to_datetime_template("s:m:h dd/mm/yyyy"), "%-S:%-M:%-H %d/%m/%Y"
        )


unittest.main()


if __name__ == "__main__":
    unittest.main()
