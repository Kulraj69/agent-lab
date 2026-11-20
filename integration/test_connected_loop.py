import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from connected_loop import demo, run_traces, POLICY
from teval.harness import evaluate

class ConnectedLoopTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.output=Path(self.tmp.name)/'run'; self.proof=demo(self.output)
    def test_three_real_traces(self):
        self.assertEqual(self.proof['trace_count'],3)
        for line in (self.output/'traces.jsonl').read_text().splitlines():
            kinds=[s['kind'] for s in json.loads(line)['steps']]
            self.assertIn('tool_call',kinds); self.assertIn('tool_result',kinds)
    def test_negative_control_has_specific_canary_failure(self):
        self.assertTrue(self.proof['negative_control_rejected'])
        self.assertTrue(any('evil-fetch/injection_canary' in r for r in self.proof['negative_control_reasons']))
    def test_restoration_passes(self): self.assertTrue(self.proof['restored_passed'])
    def test_missing_baseline_case_fails(self): self.assertTrue(self.proof['missing_case_rejected'])
    def test_exact_two_promotions_one_rejection(self):
        first=self.proof['first_promotion']; self.assertEqual(first['promoted'],['calc-task','clean-fetch']); self.assertEqual(list(first['rejected']),['bad-citation'])
    def test_rerun_is_byte_identical(self):
        self.assertTrue(self.proof['golden_byte_identical_on_rerun']); self.assertEqual(self.proof['second_promotion']['promoted'],[])
    def test_reused_output_directory_rejected(self):
        with self.assertRaises(FileExistsError): demo(self.output)
    def test_repeated_fresh_runs_match(self):
        other=demo(Path(self.tmp.name)/'other'); self.assertEqual(self.proof,other)
