"""Hand-calculated independent market and financing oracles."""

import copy
import unittest

from risk_practice.market import broker_margin, counterparty_exposure, historical_var_es


class MarketTests(unittest.TestCase):
    def test_fractional_tail_not_mean_of_exceedances(self):
        r = historical_var_es([0, 10, 20, 30], .625, {"crash": 80})
        self.assertEqual(r["var"], 20)
        self.assertAlmostEqual(r["es"], 80 / 3)  # top 1.5 observations: (30 + .5*20)/1.5
        self.assertEqual(r["stress_results"], [{"scenario": "crash", "loss": 80}])

    def test_exact_boundary_and_ties(self):
        for values, confidence, var, es in [([1, 2, 3, 4], .5, 2, 3.5),
                                            ([5, 5, 5, 5], .9, 5, 5),
                                            ([0], .99, 0, 0)]:
            r = historical_var_es(values, confidence, {"named": 10})
            self.assertEqual(r["var"], var)
            self.assertAlmostEqual(r["es"], es)
            self.assertAlmostEqual(sum(x["normalized_tail_weight"] for x in r["tail_evidence"]), 1)

    def test_empirical_cdf_boundaries(self):
        for n in range(2, 101):
            for k in range(1, n):
                result = historical_var_es(list(range(1, n + 1)), k / n, {"x": n})
                self.assertEqual(result["var"], k)
                self.assertAlmostEqual(result["es"], (k + 1 + n) / 2)

    def test_order_invariance(self):
        self.assertEqual(historical_var_es([1, 9, 3], .7, {"x": 10}),
                         historical_var_es([9, 3, 1], .7, {"x": 10}))

    def test_invalid_inputs(self):
        for values, c, stress in [([], .9, {"x": 2}), ([True], .9, {"x": 2}),
                                  ([float("nan")], .9, {"x": 2}), ([-1], .9, {"x": 2}),
                                  ([1], 1, {"x": 2}), ([1], 0, {"x": 2}),
                                  ([1], True, {"x": 2}), ([1], .9, {}),
                                  ([1], .9, {"": 2}), ([1], .9, {"x": float("inf")})]:
            with self.subTest(values=values, confidence=c, stress=stress), self.assertRaises(ValueError):
                historical_var_es(values, c, stress)


class CounterpartyTests(unittest.TestCase):
    def request(self):
        return dict(mtm_paths=[[10, 20], [-5, 40]], collateral_available=[[0, 10], [0, 10]],
                    discount_factors=[1, .9], conditional_pds=[.1, .2], lgd=.5,
                    legal_netting_set="invented-set", confidence=.75)

    def test_hand_oracle(self):
        r = counterparty_exposure(**self.request())
        # EE 5,20; marginal default .1,.18. CVA .25 + 1.62 = 1.87.
        self.assertAlmostEqual(r["independent_cva"], 1.87)
        self.assertEqual([x["ee"] for x in r["period_results"]], [5, 20])
        self.assertEqual([x["pfe"] for x in r["period_results"]], [10, 30])
        self.assertEqual([x["positive_exposure"] for x in r["path_evidence"]], [10, 10, 0, 30])

    def test_explicit_delayed_collateral_increases_exposure(self):
        args = self.request()
        baseline = counterparty_exposure(**args)["independent_cva"]
        args["collateral_available"] = [[0, 0], [0, 0]]
        self.assertAlmostEqual(counterparty_exposure(**args)["independent_cva"] - baseline, .81)

    def test_full_collateral_and_zero_pd(self):
        args = self.request()
        args["collateral_available"] = [[100, 100], [100, 100]]
        self.assertEqual(counterparty_exposure(**args)["independent_cva"], 0)
        args = self.request()
        args["conditional_pds"] = [0, 0]
        self.assertEqual(counterparty_exposure(**args)["independent_cva"], 0)

    def test_survival_after_certain_default(self):
        args = self.request()
        args["conditional_pds"] = [1, 1]
        self.assertEqual(counterparty_exposure(**args)["independent_cva"], 2.5)

    def test_bad_shapes_and_values(self):
        for key, value in [("mtm_paths", [[1], [2, 3]]), ("collateral_available", [[1, 2]]),
                           ("collateral_available", [[-1, 0], [0, 0]]), ("discount_factors", [1]),
                           ("discount_factors", [0, 1]), ("conditional_pds", [1.1, .1]),
                           ("lgd", True), ("legal_netting_set", ""), ("mtm_paths", [[float("inf")]])]:
            args = self.request()
            args[key] = value
            with self.subTest(key=key, value=value), self.assertRaises(ValueError):
                counterparty_exposure(**args)


class BrokerTests(unittest.TestCase):
    def securities(self):
        return [{"security_id": "s1", "issuer": "A", "currency": "HKD", "quantity": 10,
                 "price": 10, "haircut": .2, "stress_return": -.5, "realizable_fraction": .6},
                {"security_id": "s2", "issuer": "A", "currency": "HKD", "quantity": 5,
                 "price": 10, "haircut": .4, "stress_return": -.2, "realizable_fraction": 1}]

    def test_independent_cash_and_lending_values(self):
        r = broker_margin(120, self.securities(), "HKD")
        self.assertEqual(r["baseline_collateral"], 110)
        self.assertEqual(r["stressed_collateral"], 64)
        self.assertEqual(r["stressed_margin_shortfall"], 56)
        self.assertEqual(r["stressed_realizable_proceeds"], 70)
        self.assertEqual(r["realizable_proceeds_gap"], 50)
        self.assertEqual(r["issuer_concentration"]["hhi"], 1)
        self.assertEqual(len(r["issuer_results"]), 1)

    def test_issuer_grouping_and_zero_total(self):
        records = self.securities()
        records[1]["issuer"] = "B"
        self.assertAlmostEqual(broker_margin(0, records, "HKD")["issuer_concentration"]["hhi"], 5/9)
        for record in records:
            record["quantity"] = 0
        r = broker_margin(10, records, "HKD")
        self.assertIsNone(r["issuer_concentration"]["hhi"])
        self.assertEqual(r["realizable_proceeds_gap"], 10)

    def test_duplicate_and_currency_rejected(self):
        records = self.securities()
        for bad in [[records[0], copy.deepcopy(records[0])], [dict(records[0], currency="USD")]]:
            with self.assertRaises(ValueError):
                broker_margin(100, bad, "HKD")

    def test_nonfinite_and_invalid_fields(self):
        for key, value in [("quantity", True), ("price", float("nan")), ("haircut", 1.1),
                           ("stress_return", -1.1), ("realizable_fraction", -1),
                           ("issuer", ""), ("security_id", " a ")]:
            record = dict(self.securities()[0], **{key: value})
            with self.subTest(key=key), self.assertRaises(ValueError):
                broker_margin(100, [record], "HKD")

    def test_wipeout_and_overflow(self):
        record = dict(self.securities()[0], stress_return=-1)
        self.assertEqual(broker_margin(100, [record], "HKD")["stressed_collateral"], 0)
        record.update(quantity=1e308, price=1e308)
        with self.assertRaises(ValueError):
            broker_margin(100, [record], "HKD")


if __name__ == "__main__":
    unittest.main()
