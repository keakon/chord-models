import datetime as dt
import tempfile
import unittest
from pathlib import Path

from catalog_coverage import discoveries, report, validate, window_start


class CoverageTest(unittest.TestCase):
    def test_calendar_window(self):
        self.assertEqual(window_start(dt.date(2026, 10, 4)), dt.date(2026, 4, 4))
        self.assertEqual(window_start(dt.date(2026, 8, 31)), dt.date(2026, 2, 28))
        self.assertEqual(window_start(dt.date(2024, 8, 31)), dt.date(2024, 2, 29))

    def test_discovery_bounds_and_unknown_release(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            modeldir = root / 'models' / 'sample'
            modeldir.mkdir(parents=True)
            for name, released in [('recent', '2026-04-04'), ('old', '2026-04-03'), ('future', '2026-10-05'), ('unknown', '')]:
                (modeldir / (name + '.toml')).write_text(f'tool_call = true\nrelease_date = "{released}"\n[modalities]\noutput = ["text"]\n')
            self.assertEqual({m['id'] for m in discoveries(root, dt.date(2026, 10, 4))}, {'sample/recent', 'sample/unknown'})

    def test_inventory_references_and_honest_completeness(self):
        day = dt.date(2026, 10, 4)
        catalog = {'models': [{'id': 'sample/model'}], 'bindings': []}
        inventory = {'schema_version': 1, 'window_months': 6, 'as_of': str(day), 'watchlist': {'sample': {'review': 'partial'}},
                     'entries': [{'id': 'sample/model', 'state': 'model', 'checked': str(day), 'reason': 'Release evidence missing', 'sources': [{'url': 'https://example.invalid/docs', 'checked': str(day)}]}]}
        with tempfile.TemporaryDirectory() as tmp:
            validate(Path(tmp), catalog, inventory, day)
            self.assertFalse(report(inventory, catalog, day)['complete'])
            inventory['entries'][0]['id'] = 'sample/missing'
            with self.assertRaises(ValueError):
                validate(Path(tmp), catalog, inventory, day)


if __name__ == '__main__':
    unittest.main()
