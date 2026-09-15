"""Independent hand calculations and explicit policy edges for ALM teaching."""
import unittest
from copy import deepcopy
from fractions import Fraction

from risk_practice.alm import alm_nmd


def request():
    return dict(asset_principal=100, asset_coupon_rate=.05, asset_maturity_years=2,
                deposit_principal=100, base_deposit_rate=.02,
                base_discount_rate=.05, rate_shock=.01,
                scenarios=[dict(name="baseline", core_fraction=.8,
                                core_runoff_weights=[0, 1], noncore_runoff_weights=[1],
                                deposit_beta=.5, deposit_rate_floor=0)])


class AlmTests(unittest.TestCase):
    def test_independent_two_year_hand_calculation(self):
        result = alm_nmd(**request())["scenario_results"][0]
        # Fixed asset 5,105. Deposits repay 20,80 and pay interest on 100,80.
        base_l = Fraction(22) / Fraction(105,100) + Fraction(816,10) / Fraction(105,100)**2
        shock_l = Fraction(225,10) / Fraction(106,100) + Fraction(82) / Fraction(106,100)**2
        shock_a = Fraction(5) / Fraction(106,100) + Fraction(105) / Fraction(106,100)**2
        self.assertAlmostEqual(result["base_asset_pv"], 100)
        self.assertAlmostEqual(result["base_liability_pv"], float(base_l))
        self.assertAlmostEqual(result["shocked_liability_pv"], float(shock_l))
        self.assertAlmostEqual(result["delta_net_eve_proxy"], float(shock_a-shock_l-(100-base_l)))
        self.assertAlmostEqual(result["base_12month_nii_proxy"], 3)
        self.assertAlmostEqual(result["shocked_12month_nii_proxy"], 2.5)
        self.assertEqual(result["principal_repaid"], 100)
        self.assertEqual(result["final_deposits"], 0)

    def test_annual_principal_conservation_and_zero_asset(self):
        req=request();req["asset_principal"]=0
        req["scenarios"][0].update(core_runoff_weights=[.1,.2,.3,.4])
        result=alm_nmd(**req)["scenario_results"][0]
        for row in result["annual_results"]:
            self.assertAlmostEqual(row["opening_deposits"], row["principal_repayment"]+row["closing_deposits"])
            self.assertAlmostEqual(row["principal_repayment"], row["core_principal_repayment"]+row["noncore_principal_repayment"])
        self.assertEqual(result["base_asset_pv"],0)
        self.assertAlmostEqual(result["base_12month_nii_proxy"],-2)

    def test_zero_shock_preserves_eve_and_nii(self):
        req=request(); req["rate_shock"]=0
        row=alm_nmd(**req)["scenario_results"][0]
        self.assertEqual(row["delta_net_eve_proxy"],0)
        self.assertEqual(row["delta_12month_nii_proxy"],0)

    def test_beta_zero_and_one(self):
        req=request(); alt=deepcopy(req["scenarios"][0]);alt.update(name="full_beta",deposit_beta=1)
        req["scenarios"][0]["deposit_beta"]=0;req["scenarios"].append(alt)
        a,b=alm_nmd(**req)["scenario_results"]
        self.assertEqual(a["delta_12month_nii_proxy"],0)
        self.assertAlmostEqual(b["delta_12month_nii_proxy"],-1)
        self.assertLess(b["delta_net_eve_proxy"],a["delta_net_eve_proxy"])

    def test_maturity_changes_eve_not_first_year_income(self):
        a=request();b=deepcopy(a);b["asset_maturity_years"]=10
        ar=alm_nmd(**a)["scenario_results"][0];br=alm_nmd(**b)["scenario_results"][0]
        self.assertEqual(ar["delta_12month_nii_proxy"],br["delta_12month_nii_proxy"])
        self.assertLess(br["delta_net_eve_proxy"],ar["delta_net_eve_proxy"])

    def test_runoff_sensitivity_no_first_year_principal_replacement(self):
        req=request();alt=deepcopy(req["scenarios"][0]);alt.update(name="fast",core_runoff_weights=[1])
        req["scenarios"].append(alt)
        slow,fast=alm_nmd(**req)["scenario_results"]
        self.assertEqual(slow["base_12month_nii_proxy"],fast["base_12month_nii_proxy"])
        self.assertNotEqual(slow["base_liability_pv"],fast["base_liability_pv"])
        self.assertEqual(fast["annual_results"][1]["opening_deposits"],0)

    def test_floor_applies_to_baseline_and_shock(self):
        req=request();req.update(base_deposit_rate=-.01,rate_shock=-.02)
        result=alm_nmd(**req)["scenario_results"][0]
        self.assertEqual(result["base_deposit_rate_after_floor"],0)
        self.assertEqual(result["shocked_deposit_rate_after_floor"],0)
        self.assertEqual(result["delta_12month_nii_proxy"],0)
        req["scenarios"][0]["deposit_rate_floor"]=None
        result=alm_nmd(**req)["scenario_results"][0]
        self.assertAlmostEqual(result["delta_12month_nii_proxy"],1)

    def test_core_extremes_and_zero_deposits(self):
        for core in [0,1]:
            req=request();req["scenarios"][0]["core_fraction"]=core
            result=alm_nmd(**req)["scenario_results"][0]
            self.assertEqual(result["principal_repaid"],100)
            self.assertEqual(result["final_deposits"],0)
        req["deposit_principal"]=0
        result=alm_nmd(**req)["scenario_results"][0]
        self.assertEqual(result["base_liability_pv"],0)
        self.assertEqual(result["delta_12month_nii_proxy"],0)

    def test_invalid_policies_and_rates(self):
        for field,value in [("core_fraction",1.1),("deposit_beta",-1),("deposit_beta",True),
                            ("core_runoff_weights",[.2,.2]),("noncore_runoff_weights",[]),
                            ("core_runoff_weights",[1,-.1,.1]),("deposit_rate_floor",float('nan'))]:
            with self.subTest(field=field,value=value):
                req=request();req["scenarios"][0][field]=value
                with self.assertRaises(ValueError):alm_nmd(**req)
        for field,value in [("base_discount_rate",-1),("rate_shock",-1.05),
                            ("asset_maturity_years",0),("asset_maturity_years",1.5),
                            ("asset_maturity_years",True),("asset_maturity_years",51)]:
            req=request();req[field]=value
            with self.assertRaises(ValueError):alm_nmd(**req)

    def test_duplicate_names_and_unknown_fields_rejected(self):
        req=request();req["scenarios"].append(deepcopy(req["scenarios"][0]))
        with self.assertRaises(ValueError):alm_nmd(**req)
        req=request();req["scenarios"][0]["estimated_beta"]=.2
        with self.assertRaises(ValueError):alm_nmd(**req)

    def test_single_year_equal_principal_and_coupon_has_zero_net_eve(self):
        req=request();req.update(asset_maturity_years=1,asset_coupon_rate=.02,rate_shock=0)
        req["scenarios"][0].update(core_runoff_weights=[1])
        result=alm_nmd(**req)["scenario_results"][0]
        self.assertEqual(result["base_net_eve_proxy"],0)
        self.assertEqual(result["base_12month_nii_proxy"],0)


if __name__ == '__main__':
    unittest.main()
