import copy
import math
import unittest

from risk_practice.credit import credit_parameter_review, recovery_lgd, ead_from_utilization, ecl_movement


def record(identity, pd, label, mature=True, group="A"):
    return {"id": identity, "predicted_pd": pd, "defaulted": label,
            "label_mature": mature, "exposure": 100, "group": group}


def snapshot(date="2026-01-01", ead=100, pds=(.1, .2), weights=(.5, .5)):
    return {"report_date": date, "entity_id": "fictional-01", "currency": "HKD",
            "effective_annual_rate": 0, "default_window_years": 1, "sicr_flag": False,
            "scenarios": [{"name": name, "weight": weight, "conditional_pds": [pd, 0, 0],
                           "lgds": [1, 1, 1], "eads": [ead, ead, ead]}
                          for name, pd, weight in zip(("base", "stress"), pds, weights)]}


class ParameterTests(unittest.TestCase):
    def test_pd_oracle(self):
        result = credit_parameter_review([record("a", .8, True), record("b", .2, False)])
        self.assertAlmostEqual(result["metrics"]["brier_score"], .04)
        self.assertEqual(result["metrics"]["auc"], 1)
        self.assertEqual(result["metrics"]["calibration_gap_observed_minus_predicted"], 0)

    def test_ties_and_reversed_ranking(self):
        tie = credit_parameter_review([record("a", .5, True), record("b", .5, False)])
        self.assertEqual(tie["metrics"]["auc"], .5)
        reversed_scores = credit_parameter_review([record("a", .2, True), record("b", .8, False)])
        self.assertEqual(reversed_scores["metrics"]["auc"], 0)

    def test_immature_and_missing_never_become_nondefault(self):
        result = credit_parameter_review([record("a", .2, False), record("b", .9, True, False),
                                          record("c", .7, None)])
        self.assertEqual(result["metrics"]["count"], 1)
        self.assertIsNone(result["metrics"]["auc"])
        self.assertEqual(result["label_integrity"]["missing_label"], 1)
        self.assertEqual(result["label_integrity"]["immature"], 1)
        self.assertEqual(result["grouped_results"][0]["excluded_records"], 2)

    def test_empty_eligible_group_is_undefined(self):
        result = credit_parameter_review([record("a", .2, None)])
        self.assertIsNone(result["metrics"]["brier_score"])
        self.assertIsNone(result["metrics"]["observed_default_rate"])

    def test_invalid_pd_inputs(self):
        for field, value in (("predicted_pd", math.nan), ("predicted_pd", True),
                             ("defaulted", 1), ("label_mature", "yes"), ("exposure", -1)):
            r = record("a", .5, True)
            r[field] = value
            with self.subTest(field=field, value=value), self.assertRaises(ValueError):
                credit_parameter_review([r])
        with self.assertRaises(ValueError):
            credit_parameter_review([record("a", .2, True)] * 2)
        with self.assertRaises(ValueError):
            credit_parameter_review([record("a", .2, True)], observation_horizon_months=True)

    def test_lgd_hand_discount_oracle(self):
        result = recovery_lgd(100, [{"year": 1, "recovery": 66, "cost": 11}], .1, workout_complete=True)
        self.assertAlmostEqual(result["discounted_net_recovery"], 50)
        self.assertAlmostEqual(result["final_lgd"], .5)

    def test_incomplete_workout_and_no_silent_clipping(self):
        result = recovery_lgd(100, [{"year": 0, "recovery": 0, "cost": 20}], 0, workout_complete=False)
        self.assertEqual(result["observed_lgd"], 1.2)
        self.assertIsNone(result["final_lgd"])
        result = recovery_lgd(100, [{"year": 0, "recovery": 120, "cost": 0}], 0, workout_complete=True)
        self.assertAlmostEqual(result["observed_lgd"], -.2)

    def test_invalid_lgd_inputs(self):
        for ead, flows, rate in [(0, [{"year": 0, "recovery": 0, "cost": 0}], 0),
                                 (100, [{"year": 1, "recovery": -1, "cost": 0}], 0),
                                 (100, [{"year": 1, "recovery": 1, "cost": 0}] * 2, 0),
                                 (100, [{"year": 1, "recovery": 1, "cost": 0}], -1)]:
            with self.subTest(ead=ead, flows=flows, rate=rate), self.assertRaises(ValueError):
                recovery_lgd(ead, flows, rate, workout_complete=True)

    def test_ead_oracle_and_boundary(self):
        self.assertEqual(ead_from_utilization(60, 40, .5)["ead"], 80)
        self.assertEqual(ead_from_utilization(60, 40, 0)["ead"], 60)
        self.assertEqual(ead_from_utilization(60, 40, 1)["ead"], 100)
        for ccf in (-.1, 1.1, math.inf, True):
            with self.subTest(ccf=ccf), self.assertRaises(ValueError):
                ead_from_utilization(60, 40, ccf)


class MovementTests(unittest.TestCase):
    def test_ordered_bridge_hand_oracle(self):
        opening = snapshot()
        closing = snapshot("2026-04-01", 200, (.2, .4), (.25, .75))
        result = ecl_movement(opening, closing)
        self.assertAlmostEqual(result["opening_ecl"], 15)
        self.assertAlmostEqual(result["closing_ecl"], 70)
        self.assertEqual([r["movement"] for r in result["records"]], [15, 0, 30, 10])
        self.assertAlmostEqual(result["reconciliation_residual"], 0)

    def test_window_change_survival_oracle(self):
        opening = snapshot(pds=(.1, .1))
        for scenario in opening["scenarios"]:
            scenario["conditional_pds"] = [.1, .1, 0]
        closing = copy.deepcopy(opening)
        closing.update(report_date="2026-04-01", default_window_years=3, sicr_flag=True)
        result = ecl_movement(opening, closing)
        self.assertAlmostEqual(result["closing_ecl"], 19)
        self.assertAlmostEqual(result["records"][1]["movement"], 9)
        self.assertNotIn("stage", result)

    def test_input_not_mutated_and_unchanged_values_bridge_zero(self):
        opening = snapshot()
        closing = copy.deepcopy(opening)
        closing["report_date"] = "2026-02-01"
        original = copy.deepcopy((opening, closing))
        result = ecl_movement(opening, closing)
        self.assertEqual((opening, closing), original)
        self.assertEqual(result["net_movement"], 0)
        self.assertEqual(sum(r["movement"] for r in result["records"]), 0)

    def test_invalid_snapshot_keys_dates_and_vectors(self):
        for field, value in (("report_date", "2026-01-01"), ("report_date", "2026-W02-1"),
                             ("currency", "USD"), ("entity_id", "other"),
                             ("sicr_flag", 1), ("default_window_years", True), ("default_window_years", None)):
            closing = snapshot("2026-02-01")
            closing[field] = value
            with self.subTest(field=field, value=value), self.assertRaises(ValueError):
                ecl_movement(snapshot(), closing)
        for field, value in (("eads", [1, 2]), ("conditional_pds", [1, 2, 3]),
                             ("weight", -.5), ("lgds", [1, True, 1])):
            closing = snapshot("2026-02-01")
            closing["scenarios"][0][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                ecl_movement(snapshot(), closing)

    def test_duplicate_or_changed_scenarios_rejected(self):
        closing = snapshot("2026-02-01")
        closing["scenarios"][1]["name"] = "base"
        with self.assertRaises(ValueError):
            ecl_movement(snapshot(), closing)
        closing["scenarios"][1]["name"] = "adverse"
        with self.assertRaises(ValueError):
            ecl_movement(snapshot(), closing)


if __name__ == "__main__":
    unittest.main()
