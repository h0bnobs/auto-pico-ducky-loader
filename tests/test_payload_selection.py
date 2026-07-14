import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import main


class PayloadSelectionTests(unittest.TestCase):
    def test_select_payload_prefers_named_file_if_present(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            payload_file = os.path.join(tmpdir, 'payload.dd')
            with open(payload_file, 'w', encoding='utf-8') as handle:
                handle.write('REM test payload')

            selected = main.find_payload_file(tmpdir, 'payload.dd')
            self.assertEqual(selected, payload_file)

    def test_select_payload_falls_back_to_first_payload(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with open(os.path.join(tmpdir, 'payload2.dd'), 'w', encoding='utf-8') as handle:
                handle.write('REM test payload')

            selected = main.find_payload_file(tmpdir, None)
            self.assertEqual(selected, os.path.join(tmpdir, 'payload2.dd'))


if __name__ == '__main__':
    unittest.main()
