# Risk Practice Portfolio

**Work scenarios → explicit methods → executable tools → review evidence.**

A portfolio and learning companion by Zheyu Liu, focused on model risk, credit and market risk, and financial data controls. The existing projects remain independent repositories. This entry connects them to work that a risk analyst or reviewer needs to perform.

**2026-09-15 · v0.2.0.** Twenty pre-existing public repositories are inventoried, with 12 core scenario guides and 16 executable requests spanning credit, market, counterparty, ALM and risk controls. [Worked cases and response plans](scenarios/WORKED_CASES.zh-CN.md) connect results to decisions and escalation. [Verification scope](validation/README.md). These independent studies do not establish personal mastery, regulatory compliance or production readiness.

## Explore the work

| Start with a task | Project | What to inspect |
| --- | --- | --- |
| Compare candidate forecasts fairly and document a review | [Forecast Review Workbench](https://github.com/zheyuliu328/forecast-review-workbench) | External CSV/Excel, common-sample decisions, retained gaps and manual opinions |
| Challenge model selection and numerical sensitivities | [Model Risk Lab](https://github.com/zheyuliu328/model-risk-lab) | Causal monthly OLS experiments, independent checks, European FX Greeks and failed hypotheses |
| Locate differences between two tables | [Financial Control Tower](https://github.com/zheyuliu328/financial-control-tower) · [Try the browser tool](https://table-check-zheyuliu.mystic-pear-2111.chatgpt.site) | File mapping, exact-decimal checks, duplicate/missing identities and inspectable exports |
| Inspect VaR forecasts and exception frequency | [VaR Backtesting](https://github.com/zheyuliu328/risk-var-dashboard) | Historical/normal forecasts, timing controls and unconditional-coverage limits |

[Full project inventory and priorities](catalog/PRIORITIES.md) · [Work-scenario casebook](scenarios/README.md) · [中文学习与面试路线](learning/README.zh-CN.md)

## Three kinds of evidence

- **Usable workflow:** a documented path accepts user-selected inputs and produces inspectable outputs. Actual independent human adoption still needs separate evidence.
- **Worked learning case:** a simplified model, invented inputs, independently checked outputs, assumptions and response options. It teaches a decision process; it is not a production model.
- **Coverage gap:** a named topic with prerequisites and an exercise to build next. A heading or a reference link does not count as an implemented capability.

The catalog's public-default-branch inspection is dated separately from historical runtime tests. A repository description, README claim or passing software check does not certify financial suitability.

## Run the new worked examples

Python 3.10+. The numerical runtime uses only the standard library. Installation of build tools may require internet access; calculations do not.

```sh
python -m pip install .
risk-practice --input examples/ecl.json --output outputs/ecl-first-run
risk-practice --input examples/liquidity.json --output outputs/liquidity-first-run
risk-practice --input examples/rates.json --output outputs/rates-first-run
risk-practice --input examples/concentration.json --output outputs/concentration-first-run
```

Each command requires a new output directory and retains the request, exact JSON results, a readable offline HTML report and a checksum manifest. The manifest is written last; an export without it is incomplete. Choose a different directory to rerun. Outputs contain supplied input values, so review them before sharing.

[Example assumptions](examples/README.md) explain annual conditional PD, simplified loss timing, cash-flow survival, fixed cash-flow discounting and exposure concentration. These models do not automatically infer stages, calculate regulatory LCR/IRRBB or prescribe risk limits.

## Authorship and learning integrity

New code and scenarios use public methods and independently invented examples, with AI-assisted implementation and review. No employer/client code, templates, data, screenshots or private history are included. Team projects and forks are attributed separately. A public source explains a method; it does not grant permission to redistribute proprietary implementations or parameter sets.

The learning route uses explain, reproduce, challenge and defend exercises. Its progress starts unassessed. Case studies must be described as independent studies in interviews unless a separate, accurate work-experience claim can be supported.

[Delivery requirements and current status](DELIVERY.md)
