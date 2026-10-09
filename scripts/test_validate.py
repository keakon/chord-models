import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).with_name('validate.sh')
PIN = 'a' * 40

# Stub only external commands; execute the real shell control flow and EXIT trap.
COMMAND = '''
import json
import os
from pathlib import Path
import sys
import tempfile

name = Path(sys.argv[0]).name
args = sys.argv[1:]
with open(os.environ['TRACE'], 'a') as trace:
    trace.write(json.dumps([name, args]) + '\\n')
if name == 'mktemp':
    path = tempfile.mkdtemp(dir=os.environ['SCRATCH'])
    Path(os.environ['TEMP_RECORD']).write_text(path)
    print(path)
elif name == 'go':
    if args[:2] == ['mod', 'download']:
        sys.exit(0 if os.environ['MODE'] == 'proxy' else 1)
    if args[0] == 'run':
        if os.environ.get('GENERATOR_FAIL'):
            print('generator failed', file=sys.stderr)
            sys.exit(2)
        Path(args[args.index('-out') + 1]).write_text('{}')
elif name == 'git':
    step = args[2] if args[0] == '-C' else args[0]
    if step == os.environ.get('FAIL_GIT_STEP'):
        print('git ' + step + ' failed', file=sys.stderr)
        sys.exit(128)
    if step == 'init':
        Path(args[-1]).mkdir()
elif name == 'python3' and args[0] == '-c':
    print('2026-10-08')
'''


class ValidateTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        scripts = self.root / 'scripts'
        scripts.mkdir()
        shutil.copyfile(SCRIPT, scripts / 'validate.sh')
        (self.root / 'coverage.json').write_text('{"as_of": "2026-10-08"}')
        (self.root / 'validator-revision').write_text(PIN + '\n')
        self.bin = self.root / 'bin'
        self.bin.mkdir()
        for name in ('go', 'git', 'python3', 'mktemp'):
            executable = self.bin / name
            executable.write_text(f'#!{sys.executable}\n' + COMMAND)
            executable.chmod(0o755)
        self.trace = self.root / 'trace.jsonl'
        self.temp_record = self.root / 'temporary-path'
        self.report = self.root / 'report.json'

    def run_validator(self, mode='proxy', fail_step='', generator_fail='', local=None):
        self.trace.write_text('')
        env = dict(os.environ, PATH=str(self.bin) + os.pathsep + os.environ['PATH'],
                   TRACE=str(self.trace), SCRATCH=str(self.root),
                   TEMP_RECORD=str(self.temp_record), MODE=mode,
                   FAIL_GIT_STEP=fail_step, GENERATOR_FAIL=generator_fail,
                   CATALOG_REVISION='v2026-10-08.5', CATALOG_REPORT_PATH=str(self.report))
        args = ['bash', str(self.root / 'scripts/validate.sh')]
        if local is not None:
            args.append(str(local))
        result = subprocess.run(args, cwd=self.root, env=env, text=True, capture_output=True)
        self.calls = [json.loads(line) for line in self.trace.read_text().splitlines()]
        if self.temp_record.exists():
            self.assertFalse(Path(self.temp_record.read_text()).exists(), 'temporary directory leaked')
        return result

    def assert_failure(self, result):
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(f'Validator check failed (pin {PIN})', result.stderr)
        self.assertIn('GOPROXY/GOSUMDB', result.stderr)
        self.assertIn('published', result.stderr)
        self.assertIn('./scripts/validate.sh /path/to/chord', result.stderr)
        self.assertFalse(self.report.exists())

    def test_proxy_success(self):
        result = self.run_validator()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(any(name == 'git' for name, _ in self.calls))
        run = next(args for name, args in self.calls if name == 'go' and args[0] == 'run')
        self.assertEqual(run[1], f'github.com/keakon/chord/cmd/modelcatalog-gen@{PIN}')
        self.assertEqual(run[-2:], ['-revision', 'v2026-10-08.5'])
        self.assertEqual(self.report.read_text(), '{}')
        self.assertTrue(any(name == 'python3' and args[:2] == ['-m', 'unittest']
                            for name, args in self.calls))
        self.assertTrue(any(name == 'python3' and args[0].endswith('/catalog_coverage.py')
                            for name, args in self.calls))

    def test_proxy_failure_falls_back_to_same_git_pin(self):
        result = self.run_validator(mode='fallback')
        self.assertEqual(result.returncode, 0, result.stderr)
        fetch = next(args for name, args in self.calls if name == 'git' and args[2] == 'fetch')
        self.assertEqual(fetch[-1], PIN)
        self.assertTrue(any(name == 'go' and args[:2] == ['run', './cmd/modelcatalog-gen']
                            for name, args in self.calls))
        self.assertEqual(self.report.read_text(), '{}')

    def test_git_failures_stop_before_generation(self):
        steps = ['init', 'remote', 'fetch', 'checkout']
        for step in steps:
            with self.subTest(step=step):
                result = self.run_validator(mode='fallback', fail_step=step)
                self.assert_failure(result)
                self.assertIn(f'git {step} failed', result.stderr)
                actual = [args[2] if args[0] == '-C' else args[0]
                          for name, args in self.calls if name == 'git']
                self.assertEqual(actual, steps[:steps.index(step) + 1])
                self.assertFalse(any(name == 'go' and args[0] == 'run' for name, args in self.calls))

    def test_local_checkout_skips_downloads(self):
        local = self.root / 'local checkout'
        local.mkdir()
        result = self.run_validator(local=local)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(any(name == 'git' or name == 'go' and args[0] == 'mod'
                             for name, args in self.calls))
        self.assertEqual(self.report.read_text(), '{}')

    def test_missing_local_checkout_reports_failure(self):
        self.assert_failure(self.run_validator(local=self.root / 'missing'))
        self.assertFalse(any(name in ('git', 'go') for name, _ in self.calls))

    def test_generator_failure_reports_cause_and_cleans_up(self):
        local = self.root / 'local checkout'
        local.mkdir()
        for mode, checkout in [('proxy', None), ('fallback', None), ('local', local)]:
            with self.subTest(mode=mode):
                result = self.run_validator(mode=mode, generator_fail='1', local=checkout)
                self.assert_failure(result)
                self.assertIn('generator failed', result.stderr)
                self.assertFalse(any(name == 'python3' for name, _ in self.calls))

    def test_invalid_pin_fails_before_downloading(self):
        (self.root / 'validator-revision').write_text('short-sha\n')
        result = self.run_validator()
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn('validator-revision must contain one full Chord commit SHA', result.stderr)
        self.assertEqual(self.calls, [])


if __name__ == '__main__':
    unittest.main()
