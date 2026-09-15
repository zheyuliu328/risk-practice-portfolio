# Independently invented examples

Every amount, probability, cash flow and exposure in this directory was chosen for this educational repository. Values are not transformed, anonymized or resampled employer/client observations. Currency is an abstract single currency unit; rates and probabilities are decimal ratios.

| Request | Decision question | Independent expectation | Boundary |
| --- | --- | --- | --- |
| [ecl.json](ecl.json) | How does the expected loss of an amortising exposure depend on survival, default probabilities and discounting? | First-year contribution is `0.02 × 0.40 × 1,000,000 / 1.05 = 7,619.047619…`; second-year marginal default probability is `0.98 × 0.03 = 0.0294` | Conditional annual PDs; LGD represents all loss conditional on default, simplified as paid at that year's end. Stage policy, recovery timing, scenarios, collateral and overlays require additional modelling. |
| [liquidity.json](liquidity.json) | On which day do the declared cash flows exhaust the available buffer? | End-of-day balances: `70, 30, 15, -10`; the first negative balance is day 4 | Specified inflows and realizable assets are assumptions. No asset can be monetised twice. This is a cash-flow survival illustration, not regulatory LCR. |
| [rates.json](rates.json) | What happens to a fixed bond's PV after a parallel yield increase? | At 5%, `5/1.05 + 5/1.05² + 105/1.05³ = 100`; a 7% yield lowers PV | Fixed cash flows and one discrete annual curve; no options, NMD behaviour, liabilities, basis or nonparallel shock model. This is not a complete bank EVE/NII measure. |
| [concentration.json](concentration.json) | How unevenly are exposures distributed across the declared names? | Shares `0.7, 0.1, 0.1, 0.1`; HHI `0.52`; effective number `1/0.52` | Exposure concentration is not default correlation, loss distribution or a regulatory large-exposure test. Economic group mapping remains essential. |

Twelve-month expected credit loss concerns lifetime losses associated with default events possible within the next twelve months. It does not mean cash shortfalls occurring only during those twelve months. In the simplified function, restricting the default window to one year is meaningful only under the stated conditional-LGD/loss-timing assumptions.

For each exercise, write an expectation before changing inputs. Keep the original run, the changed request, the new run and an explanation of any surprising result. Select a response only after checking whether the changed assumption is operationally plausible.


## Extended workflows

All 16 JSON files are executable through the same entry point. See the [worked-case guide](../scenarios/WORKED_CASES.zh-CN.md) for expected results, adverse changes, owners and limits. Requests and reported results preserve explicit assumptions; no private data is bundled.
