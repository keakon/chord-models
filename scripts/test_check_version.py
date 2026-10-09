import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).with_name('check_version.py')


class CheckVersionTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.env = dict(os.environ, GIT_CONFIG_NOSYSTEM='1', GIT_CONFIG_GLOBAL=os.devnull)
        self.git('init', '-q')
        self.git('config', 'user.name', 'Catalog test')
        self.git('config', 'user.email', 'catalog@example.invalid')
        self.write('catalog.yaml', 'version: "2026-10-08.9"\n')
        self.write('candidates/README.md', 'Candidate documentation\n')
        self.write('candidates/sample--model.yaml', 'wire_model_id: model\nscope: sample\n')
        self.write('coverage.json', '{}\n')
        self.commit()
        self.base = self.git('rev-parse', 'HEAD').strip()

    def git(self, *args):
        return subprocess.check_output(['git', *args], cwd=self.root, env=self.env, text=True)

    def write(self, path, content):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content)

    def commit(self):
        self.git('add', '.')
        self.git('-c', 'commit.gpgsign=false', 'commit', '-qm', 'test change')

    def check(self, expected):
        result = subprocess.run([sys.executable, str(SCRIPT), self.base],
                                cwd=self.root, env=self.env, text=True, capture_output=True)
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        if expected:
            self.assertIn('strictly newer version', result.stderr)

    def test_candidate_documentation_needs_no_version_bump(self):
        self.write('candidates/README.md', 'Updated documentation\n')
        self.commit()
        self.check(0)

    def test_candidate_addition_requires_version_bump(self):
        self.write('candidates/sample--new.yaml', 'wire_model_id: new\nscope: sample\n')
        self.commit()
        self.check(1)

    def test_candidate_edit_requires_version_bump(self):
        self.write('candidates/sample--model.yaml', 'wire_model_id: model\nscope: sample\ncontext: 100\n')
        self.commit()
        self.check(1)

    def test_candidate_deletion_requires_version_bump(self):
        (self.root / 'candidates/sample--model.yaml').unlink()
        self.commit()
        self.check(1)

    def test_candidate_rename_requires_version_bump(self):
        self.git('mv', 'candidates/sample--model.yaml', 'candidates/sample--renamed.yaml')
        self.commit()
        self.check(1)

    def test_coverage_change_requires_version_bump(self):
        self.write('coverage.json', '{"as_of": "2026-10-09"}\n')
        self.commit()
        self.check(1)

    def test_numeric_version_increment_allows_data_change(self):
        self.write('catalog.yaml', 'version: "2026-10-08.10"\n')
        self.write('coverage.json', '{"as_of": "2026-10-08"}\n')
        self.commit()
        self.check(0)

    def test_new_date_allows_sequence_reset(self):
        self.write('catalog.yaml', 'version: "2026-10-09.0"\n')
        self.commit()
        self.check(0)

    def test_version_regression_is_rejected(self):
        self.write('catalog.yaml', 'version: "2026-10-08.8"\n')
        self.commit()
        self.check(1)

    def test_uncommitted_version_cannot_satisfy_committed_change(self):
        self.write('coverage.json', '{"as_of": "2026-10-08"}\n')
        self.commit()
        self.write('catalog.yaml', 'version: "2026-10-08.10"\n')
        self.check(1)

    def test_uncommitted_version_cannot_invalidate_committed_bump(self):
        self.write('catalog.yaml', 'version: "2026-10-08.10"\n')
        self.commit()
        self.write('catalog.yaml', 'version: "2026-10-08.8"\n')
        self.check(0)


if __name__ == '__main__':
    unittest.main()
