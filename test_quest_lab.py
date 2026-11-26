import itertools
import json
import subprocess
import sys
import unittest
from pathlib import Path
from quest_lab import MATERIALS, QUESTS, markdown, plan

class PlanningTests(unittest.TestCase):
    def test_constraints_across_catalog(self):
        for count in range(len(MATERIALS)+1):
            for materials in itertools.combinations(MATERIALS, count):
                for space in ('table', 'floor', 'both'):
                    for adult in (False, True):
                        for budget in (1, 10, 15, 25, 40, 60):
                            result = plan(materials, budget, space, adult)
                            self.assertLessEqual(result['minutes'], budget)
                            self.assertEqual(result['minutes']+result['remaining'], budget)
                            for q in result['quests']:
                                self.assertTrue(set(q['materials']) <= set(materials))
                                self.assertTrue(space == 'both' or q['space'] == space)
                                self.assertTrue(adult or not q['adult'])
                            ids = [q['id'] for q in result['quests']] + [q['id'] for q in result['excluded']]
                            self.assertCountEqual(ids, [q['id'] for q in QUESTS])
    def test_shared_budget_and_best_fit(self):
        result = plan(MATERIALS, 25, 'both', True)
        self.assertEqual(result['minutes'], 25)
        self.assertEqual(len(result['quests']), 2)
        self.assertEqual(result, plan(MATERIALS, 25, 'both', True))
    def test_explanations(self):
        result = plan(['paper'], 10, 'table')
        self.assertEqual(result['quests'], [])
        reasons = next(x['reasons'] for x in result['excluded'] if x['id']=='robot-route')
        self.assertIn('needs adult participation', reasons)
        self.assertIn('needs floor space', reasons)
        self.assertIn('No missions match', markdown(result))
    def test_invalid_input(self):
        for minutes in (0, -1, True, 1.5):
            with self.assertRaises(ValueError): plan([], minutes, 'both')
        with self.assertRaises(ValueError): plan(['unknown'], 20, 'both')
    def test_cli_json_and_errors(self):
        script = str(Path(__file__).with_name('quest_lab.py'))
        args = [sys.executable, script, '--materials', 'paper', '--minutes', '10', '--space', 'floor', '--adult', '--json']
        result = subprocess.run(args, capture_output=True, text=True, check=True)
        self.assertEqual(json.loads(result.stdout)['quests'][0]['id'], 'robot-route')
        args[args.index('10')] = '0'
        result = subprocess.run(args, capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertNotIn('Traceback', result.stderr)

if __name__ == '__main__': unittest.main()
