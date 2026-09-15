"""Installed entry point: every shipped request, retained evidence and no overwrite."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from risk_practice.cli import run_request

ROOT = Path(__file__).resolve().parents[1]


class ExampleDeliveryTests(unittest.TestCase):
    def test_all_shipped_examples_preserve_complete_evidence(self):
        requests = sorted((ROOT / 'examples').glob('*.json'))
        self.assertEqual(len(requests), 16)
        with tempfile.TemporaryDirectory() as folder:
            for source in requests:
                with self.subTest(example=source.name):
                    destination = Path(folder) / source.stem
                    evidence = run_request(source, destination)
                    self.assertEqual(evidence['package_version'], '0.2.0')
                    self.assertEqual((destination / 'request.json').read_bytes(), source.read_bytes())
                    manifest = json.loads((destination / 'manifest.json').read_text())
                    self.assertTrue(manifest['complete'])
                    for name, digest in manifest['sha256'].items():
                        self.assertEqual(hashlib.sha256((destination / name).read_bytes()).hexdigest(), digest)
                    before = {p.name: p.read_bytes() for p in destination.iterdir()}
                    with self.assertRaises(FileExistsError):
                        run_request(source, destination)
                    self.assertEqual(before, {p.name: p.read_bytes() for p in destination.iterdir()})
                    self.assertIn('Assumptions and limits', (destination / 'report.html').read_text())
