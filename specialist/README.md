# Specialist cases

Choose a problem that follows naturally from the flagship. These are distinct cases, not modules of a universal risk engine. “Specialist” indicates subject depth, not production readiness.

| Case / intended reviewer | Question and method | Runnable evidence | Acceptance and limits |
| --- | --- | --- | --- |
| FX sensitivities / valuation control | Prices agree; do derivative units and bump convergence agree? | [Model Risk Lab](https://github.com/zheyuliu328/model-risk-lab), [M02 contract](../scenarios/README.md#m02-valuation-and-greeks) | Explain Vega units and independent finite differences; European examples only, no proprietary SIMM implementation |
| ECL movement / credit and finance review | Why did the loss estimate change? Separate exposure, window, parameters and weights | [Worked ECL case](../scenarios/WORKED_CASES.zh-CN.md), [request](../examples/ecl-movement.json) | Reconcile opening/closing and disclose order dependence; teaching bridge, no automatic SICR or full IFRS 9 engine |
| Market and collateral / market or broker risk | Why do VaR, stress, margin calls and available cash lead to different actions? | [VaR project](https://github.com/zheyuliu328/risk-var-dashboard), [market](../examples/market-stress.json), [collateral](../examples/broker-margin.json) | Challenge sample/holding-period and cash availability; separate tools, no portfolio capital or liquidation engine |
| Data control / reporting operations | Can offsetting differences and shared omissions hide behind equal totals? | [FCT browser](https://table-check-zheyuliu.mystic-pear-2111.chatgpt.site), [source and limits](https://github.com/zheyuliu328/financial-control-tower), [O01](../scenarios/README.md#o01-data-and-operational-controls) | Retain row exceptions; independent expected population needed for common omissions; no implicit transfer into the flagship |
| Negative research / quantitative research | Does a sentiment factor survive sample, costs and alternative explanations? | [HSTECH study](https://github.com/zheyuliu328/hstech-nlp-quant-factor) | Historical evidence, not freshly reproduced here; short sample and missing neutralisation remain material |

For a first visit, show the flagship and **one** case relevant to the role. The ECL/margin numerical requests live in the [laboratory](../lab/README.md); their small size is deliberate and their case interpretation supplies the context. A domain case is not a claim of corresponding professional experience.
