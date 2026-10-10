import sqlite3
import unittest
from compare import add_corpus
from policy_reports import id_feasibility, gender_option

class PolicyReportsTest(unittest.TestCase):
    def test_unique_ids_and_gender_hypothesis_are_separate(self):
        db=sqlite3.connect(':memory:')
        self.addCleanup(db.close)
        # Ambiguous identical paradigms must not silently obtain stable IDs.
        add_corpus(db,'old',[[('дом',(19,))],[('луг',(19,))],[('луг',(19,))],
                             [('сирота',(19,27)),('сироты',(19,27))]])
        add_corpus(db,'new',[[('луг',(19,))],[('дом',(19,))],
                             [('сирота',(19,1,48)),('сироты',(19,1,48))]])
        result=id_feasibility(db)
        self.assertEqual(result['unique_exact_ordered_paradigms'],1)
        self.assertEqual(result['preservable_ids_in_exact_ordered_paradigms'],1)
        self.assertEqual(result['unresolved_old_slots'],3)
        self.assertEqual(result['retired_old_ids'],4)
        self.assertEqual(result['total_slots_if_preserving_all_old_slots'],6)
        self.assertEqual(result['old_paradigms_no_semantic_match'],1)
        self.assertEqual(gender_option(db),dict(new_paradigms_with_joint_male_female_tags=1,
                         new_paradigms_matching_old_after_collapse=1,distinct_old_paradigms_matched=1))
        self.assertEqual(id_feasibility(db),result)  # Hypothesis never mutates the input.

if __name__=='__main__':unittest.main()
