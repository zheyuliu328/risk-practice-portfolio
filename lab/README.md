# Learning laboratory

The 16 numerical requests support learning and independent challenges. They are not 16 standalone products and are not the portfolio's headline. Each can be run with `risk-practice --input <request> --output <new-directory>` after `python -m pip install .` from this repository.

| Study family | Requests under examples/ | Completion exercise |
| --- | --- | --- |
| Credit parameters | credit-parameters.json, recovery-lgd.json, ead-utilization.json | Separate ranking/calibration, provisional recovery and utilization assumptions |
| ECL arithmetic | ecl.json, weighted-ecl.json, ecl-movement.json | Reconcile a fixed-order bridge and explain what SICR evidence is missing |
| Market/counterparty | market-stress.json, counterparty.json, broker-margin.json, concentration.json | Distinguish tail loss, exposure, required call and realized cash |
| Liquidity and ALM | liquidity.json, rates.json, alm-nmd.json | Change cash timing/beta/runoff; explain what should and should not change |
| Governance controls | monitoring.json, alert-capacity.json, ai-review.json | Separate numerical alerts, unknown labels, semantics and human authorization |

[Input explanations](../examples/README.md) · [Worked calculations and response options](../scenarios/WORKED_CASES.zh-CN.md) · [Interview exercises](../learning/CASE_INTERVIEWS.zh-CN.md) · [Report download, v0.2.0](https://github.com/zheyuliu328/risk-practice-portfolio/releases/tag/v0.2.0)

The [CreditOne prototype](https://github.com/zheyuliu328/algorithmic-credit-risk-engine) belongs on this learning shelf because its supplied-model validation and other legacy components have documented limitations. It is not a second flagship.

ALM, AML, AI and other unfamiliar areas are independent studies. Run a baseline, create an adverse case, then explain the result without assistance. Record evidence in the [personal progress template](../learning/progress.template.json); do not pre-fill mastery. The eight specialist gap routes in the interview guide remain learning plans, not implemented capabilities.
