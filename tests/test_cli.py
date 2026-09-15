import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from risk_practice.cli import main, run_request


class ExportTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.source = self.root / "input.json"
        self.source.write_text(json.dumps({"model": "concentration", "inputs": {"exposures": [70, 10, 10, 10]}}))

    def test_complete_inspectable_export_and_input_preservation(self):
        original = self.source.read_bytes()
        output = self.root / "result"
        result = run_request(self.source, output)
        self.assertAlmostEqual(result["result"]["hhi"], .52)
        self.assertEqual(self.source.read_bytes(), original)
        manifest = json.loads((output / "manifest.json").read_text())
        self.assertTrue(manifest["complete"])
        self.assertEqual(set(manifest["sha256"]), {"request.json", "result.json", "report.html"})
        for name, digest in manifest["sha256"].items():
            self.assertEqual(hashlib.sha256((output / name).read_bytes()).hexdigest(), digest)
        self.assertIn("regulatory capital", (output / "report.html").read_text())
        self.assertNotIn("<script", (output / "report.html").read_text())

    def test_existing_directory_and_files_preserved(self):
        output = self.root / "result"
        run_request(self.source, output)
        before = {p.name: p.read_bytes() for p in output.iterdir()}
        with self.assertRaises(FileExistsError):
            run_request(self.source, output)
        self.assertEqual(before, {p.name: p.read_bytes() for p in output.iterdir()})
        empty = self.root / "empty"
        empty.mkdir()
        with self.assertRaises(FileExistsError):
            run_request(self.source, empty)

    def test_invalid_request_publishes_no_output(self):
        for text in ['[]', '{"model":"ecl","inputs":{},"extra":1}',
                     '{"model":"ecl","model":"rates","inputs":{}}',
                     '{"model":"concentration","inputs":{"exposures":[NaN]}}',
                     '{"model":"concentration","inputs":{"exposures":[1e309]}}']:
            with self.subTest(text=text):
                self.source.write_text(text)
                output = self.root / "invalid"
                self.assertEqual(main(["--input", str(self.source), "--output", str(output)]), 2)
                self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
