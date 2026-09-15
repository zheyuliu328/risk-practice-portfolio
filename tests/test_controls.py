import math
import unittest

from risk_practice.controls import ai_release_review, alert_capacity_review, model_monitoring


class MonitoringTests(unittest.TestCase):
    def test_identical_bins_and_unknown_performance(self):
        r = model_monitoring([0, 1, 2], [0, 1, 2], [1], .2)
        self.assertEqual(r["psi"], 0)
        self.assertEqual(r["review_signals"], ["performance_unassessed_no_observed_losses"])

    def test_both_tails_preserved_and_independent_psi(self):
        r = model_monitoring([-100, -2, 1, 100], [1, 2, 3, 1000], [0], .1)
        self.assertEqual([x["current_count"] for x in r["bins"]], [0, 4])
        # Half counts give p=(.5,.5), q=(.1,.9), independently evaluated.
        self.assertAlmostEqual(r["psi"], (-.4)*math.log(.1/.5)+.4*math.log(.9/.5))
        self.assertEqual(sum(x["reference_count"] for x in r["bins"]), 4)

    def test_loss_review_and_missing_contract(self):
        r = model_monitoring([1, 2], [1, 2], [1.5], .2,
                             reference_losses=[1, 3], current_losses=[5, 7], mean_loss_increase_threshold=3)
        self.assertEqual(r["performance"]["absolute_mean_increase"], 4)
        self.assertIn("observed_loss_increase_exceeds_declared_review_threshold", r["review_signals"])
        with self.assertRaises(ValueError):
            model_monitoring([1], [2], [1], .2, current_losses=[1])


class CapacityTests(unittest.TestCase):
    def test_known_subset_does_not_count_unknown_as_negative(self):
        rows = [{"id": "a", "score": 3, "label": None}, {"id": "b", "score": 2, "label": False},
                {"id": "c", "score": 1, "label": True}]
        r = alert_capacity_review(rows, 2, 0, 2, 10)
        self.assertEqual(r["observed_counts"], dict(tp=0, fp=1, tn=0, fn=1, unknown_selected=1, unknown_not_selected=0))
        self.assertEqual(r["illustrative_cost_on_known_labels"], 12)
        self.assertEqual(r["recall_on_known_labels"], 0)

    def test_no_known_labels_means_undefined(self):
        r = alert_capacity_review([{"id": "x", "score": 1, "label": None}], 0, 0, 1, 10)
        self.assertIsNone(r["precision_on_known_labels"])
        self.assertIsNone(r["recall_on_known_labels"])

    def test_tie_and_reordering_and_duplicate_failure(self):
        rows = [{"id": "b", "score": 1, "label": True}, {"id": "a", "score": 1, "label": False}]
        for data in (rows, list(reversed(rows))):
            chosen = [r["id"] for r in alert_capacity_review(data, 1, 0, 1, 1)["records"] if r["selected_for_review"]]
            self.assertEqual(chosen, ["a"])
        with self.assertRaises(ValueError):
            alert_capacity_review(rows+rows, 1, 0, 1, 1)


class AIReviewTests(unittest.TestCase):
    def row(self):
        return {"id": "a", "expected_value": 10, "reported_value": 10,
                "required_sources": ["s"], "cited_sources": ["s"], "semantic_supported": True,
                "allowed_actions": ["draft"], "requested_actions": ["draft"]}

    def test_reference_presence_is_not_semantic_support(self):
        row = self.row(); row["semantic_supported"] = None
        result = ai_release_review([row], .01)
        self.assertEqual(result["requires_resolution"], 1)
        self.assertIn("semantic_support_unassessed", result["records"][0]["issues"])

    def test_numeric_and_actions_independently_block(self):
        row = self.row(); row["reported_value"] = 9; row["requested_actions"] = ["trade"]
        issues = ai_release_review([row], .01)["records"][0]["issues"]
        self.assertEqual(issues, ["numerical_difference", "unauthorized_action_requested"])
        self.assertEqual(ai_release_review([self.row()], .01)["records"][0]["status"], "eligible_for_human_review")

    def test_boolean_number_and_unknown_fields_fail(self):
        row = self.row(); row["expected_value"] = True
        with self.assertRaises(ValueError): ai_release_review([row], .01)
        row = self.row(); row["silent_extra"] = 1
        with self.assertRaises(ValueError): ai_release_review([row], .01)


if __name__ == "__main__":
    unittest.main()
