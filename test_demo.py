import unittest
import tempfile
import json
from pathlib import Path
from demo import run

class ExperimentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory()
        cls.output=Path(cls.temp.name)/'results.json'
        cls.r=run(cls.output)
    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()
    def test_output_matches_returned_result(self):
        self.assertEqual(json.loads(self.output.read_text()),self.r)
    def test_no_leakage(self):
        from demo import split_positives,interactions
        tr,te=split_positives(interactions())
        self.assertTrue(all(not(set(a)&set(b)) for a,b in zip(tr,te)))
    def test_hand_metric(self):
        from demo import evaluate
        self.assertAlmostEqual(evaluate([1,2,3],[1,2],2)[0],1.)
        self.assertAlmostEqual(evaluate([1,2,3],[1,2],2)[1],1.)
    def test_ranges(self):
        self.assertTrue(all(0<=v<=1 for m in self.r['models'].values() for v in m.values()))

if __name__ == "__main__":
    unittest.main()
