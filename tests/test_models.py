"""Independent small-number oracles and mathematical counterexamples."""

import math
import unittest

from risk_practice.models import (
    exposure_concentration, fixed_cashflow_rate_shock, liquidity_runway,
    simplified_ecl, weighted_scenario_ecl,
)


class ECLTests(unittest.TestCase):
    def test_hand_oracle_survival_and_discount(self):
        # First default: .1; second default: .9*.2=.18. Losses 5, 7.2.
        r = simplified_ecl([.1, .2], [.5, .4], [100, 100], .1)
        self.assertAlmostEqual(r["ecl"], 5 / 1.1 + 7.2 / 1.21)
        self.assertAlmostEqual(r["cumulative_default_probability"], .28)
        self.assertAlmostEqual(r["survival_at_window_end"], .72)

    def test_one_year_window_excludes_later_defaults(self):
        r = simplified_ecl([.1, 1], [.5, 1], [100, 1000], 0, default_window_years=1)
        self.assertEqual(r["ecl"], 5)
        self.assertEqual(len(r["annual_results"]), 1)

    def test_one_year_window_uses_full_conditional_loss(self):
        # LGD=.6 represents total loss after default, including recoveries beyond
        # twelve months. The teaching approximation puts all .1*.6*100 at t=1.
        r = simplified_ecl([.1, .2], [.6, .5], [100, 100], .2, default_window_years=1)
        self.assertAlmostEqual(r["ecl"], 5)
        self.assertNotIn("stage", r)

    def test_certain_default_leaves_no_survivors(self):
        r = simplified_ecl([1, 1], [.5, 1], [100, 1000], 0)
        self.assertEqual(r["ecl"], 50)
        self.assertEqual(r["annual_results"][1]["marginal_pd"], 0)

    def test_discount_and_exposure_invariants(self):
        original = simplified_ecl([.1, .2], [.5, .5], [100, 100], 0)["ecl"]
        doubled = simplified_ecl([.1, .2], [.5, .5], [200, 200], 0)["ecl"]
        discounted = simplified_ecl([.1, .2], [.5, .5], [100, 100], .1)["ecl"]
        self.assertEqual(doubled, 2 * original)
        self.assertLess(discounted, original)

    def test_weights_hand_oracle(self):
        self.assertEqual(weighted_scenario_ecl([10, 30], [.75, .25])["weighted_ecl"], 15)

    def test_weights_reject_bad_sum_and_values(self):
        for weights in ([0, 0], [.4, .4], [-.1, 1.1], [True, 0], [math.nan, 1]):
            with self.subTest(weights=weights), self.assertRaises(ValueError):
                weighted_scenario_ecl([1, 2], weights)

    def test_bad_ecl_inputs(self):
        for pds, lgds, eads, rate, window in [
            ([], [], [], 0, None), ([.1], [.5, .4], [100], 0, None),
            ([1.1], [.5], [100], 0, None), ([.1], [-.1], [100], 0, None),
            ([.1], [.5], [-1], 0, None), ([True], [.5], [100], 0, None),
            ([.1], [.5], [100], -1, None), ([.1], [.5], [100], 0, True),
            ([.1], [.5], [100], 0, 2), ([.1], [.5], [100], 0, .5),
            ([.1], [.5], [100], 0, 0), ([.1], [.5], [100], 0, -1),
        ]:
            with self.subTest(inputs=(pds, lgds, eads, rate, window)), self.assertRaises(ValueError):
                simplified_ecl(pds, lgds, eads, rate, default_window_years=window)


class LiquidityTests(unittest.TestCase):
    def test_hand_oracle_includes_realized_proceeds(self):
        r = liquidity_runway(100, [10, 0, 10], [60, 70, 20], daily_realizable_cash=[0, 10, 0])
        self.assertEqual([d["closing_cash"] for d in r["daily_results"]], [50, -10, -20])
        self.assertEqual(r["first_negative_day"], 2)
        self.assertEqual(r["ending_cash"], -20)

    def test_zero_balance_is_not_negative_and_later_recovery_preserves_first_breach(self):
        self.assertIsNone(liquidity_runway(10, [0], [10])["first_negative_day"])
        self.assertEqual(liquidity_runway(0, [0, 20], [10, 0])["first_negative_day"], 1)

    def test_bad_lengths_and_negative_inputs(self):
        for initial, inflow, outflow in [(-1, [0], [0]), (0, [], []), (0, [1], [1, 2]), (0, [-1], [0])]:
            with self.subTest(inputs=(initial, inflow, outflow)), self.assertRaises(ValueError):
                liquidity_runway(initial, inflow, outflow)


class RateTests(unittest.TestCase):
    def test_hand_oracle(self):
        r = fixed_cashflow_rate_shock([110, 121], [1, 2], .1, .1)
        self.assertAlmostEqual(r["base_pv"], 200)
        self.assertAlmostEqual(r["shocked_pv"], 110 / 1.2 + 121 / 1.44)
        self.assertAlmostEqual(r["delta_pv"], r["shocked_pv"] - 200)

    def test_positive_cashflow_monotonic_and_zero_shock(self):
        self.assertLess(fixed_cashflow_rate_shock([100], [2], .02, .01)["delta_pv"], 0)
        self.assertEqual(fixed_cashflow_rate_shock([100], [2], .02, 0)["delta_pv"], 0)
        self.assertGreater(fixed_cashflow_rate_shock([100], [2], .02, -.01)["delta_pv"], 0)

    def test_signed_cashflows_are_not_assumed_monotonic(self):
        self.assertGreater(fixed_cashflow_rate_shock([-100], [1], 0, .1)["delta_pv"], 0)

    def test_invalid_time_and_rates(self):
        for years in ([0, 1], [1, 1], [2, 1], [1, 1.5], [True, 2]):
            with self.subTest(years=years), self.assertRaises(ValueError):
                fixed_cashflow_rate_shock([1, 2], years, .1, 0)
        for rate, shock in [(-1, .1), (0, -1), (.1, math.inf)]:
            with self.subTest(rate=rate, shock=shock), self.assertRaises(ValueError):
                fixed_cashflow_rate_shock([1], [1], rate, shock)


class ConcentrationTests(unittest.TestCase):
    def test_hand_oracle(self):
        r = exposure_concentration([50, 30, 20])
        self.assertEqual(r["hhi"], .38)
        self.assertEqual(r["top_share"], .5)
        self.assertAlmostEqual(r["effective_count"], 50 / 19)

    def test_equal_and_single_entity(self):
        self.assertEqual(exposure_concentration([5] * 4)["effective_count"], 4)
        self.assertEqual(exposure_concentration([0, 100])["hhi"], 1)

    def test_scale_invariance_and_zero_undefined(self):
        self.assertEqual(exposure_concentration([5, 3, 2])["shares"], exposure_concentration([50, 30, 20])["shares"])
        r = exposure_concentration([0, 0])
        self.assertIsNone(r["hhi"])
        self.assertIsNone(r["effective_count"])


class NumericalValidationTests(unittest.TestCase):
    def test_small_probabilities_do_not_erase_representable_loss(self):
        result = simplified_ecl([1e-200], [1e-200], [1e300], 0)
        self.assertTrue(math.isclose(result["ecl"], 1e-100, rel_tol=1e-14))
        with self.assertRaises(ValueError):
            simplified_ecl([1e-200], [1e-200], [1], 0)

    def test_nonfinite_and_bool_rejected_every_model(self):
        for value in (math.inf, -math.inf, math.nan, True, "1"):
            for call in (
                lambda: simplified_ecl([value], [.5], [100], 0),
                lambda: weighted_scenario_ecl([value], [1]),
                lambda: liquidity_runway(value, [0], [0]),
                lambda: fixed_cashflow_rate_shock([value], [1], 0, 0),
                lambda: exposure_concentration([value]),
            ):
                with self.subTest(value=value, call=call), self.assertRaises(ValueError):
                    call()

    def test_overflow_and_discount_underflow_are_explicit(self):
        for call in (
            lambda: exposure_concentration([1e308, 1e308]),
            lambda: fixed_cashflow_rate_shock([1], [10000], .1, 0),
            lambda: fixed_cashflow_rate_shock([1e308], [1], -.9, 0),
            lambda: liquidity_runway(1e308, [1e308], [0]),
            lambda: simplified_ecl([.5, 1], [1, 1], [1e308, 1e308], -.5),
        ):
            with self.subTest(call=call), self.assertRaises(ValueError):
                call()


if __name__ == "__main__":
    unittest.main()
