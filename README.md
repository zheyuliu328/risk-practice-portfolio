# Zheyu Liu · Model Risk Portfolio

**How do you decide whether a model result is fit for its intended use?**

My main work is a review workflow: establish the input contract, compare candidates fairly, challenge the result, and hand over findings with clear limitations. Public projects use invented examples and public methods, with AI-assisted implementation and review. They are separate from confidential professional work.

## Start with one complete task

### [Flagship: forecast review and evidence handoff](flagship/forecast-review/README.md)

A candidate looks more accurate because it omits difficult months. Inspect the missing coverage, compare on an explicitly accepted common sample, independently recalculate the errors and write a bounded recommendation.

**Use:** [Forecast Review Workbench](https://github.com/zheyuliu328/forecast-review-workbench). **Numerical foundation:** [Model Risk Lab](https://github.com/zheyuliu328/model-risk-lab). The Workbench already pins its reused numerical kernel; this portfolio does not create another forecasting engine.

[Read the worked review memo](flagship/forecast-review/REVIEW_MEMO.md) · [Run the case yourself](flagship/forecast-review/README.md#run-the-case) · [Inspect the input contract](flagship/forecast-review/INPUT_CONTRACT.md)

The flagship is an executable educational review workflow. It is not evidence of production deployment, independent human adoption or complete model validation.

## Then explore the relevant depth

| Layer | What belongs here | Reader's next action |
| --- | --- | --- |
| **[Flagship](flagship/forecast-review/README.md)** | One connected review task, with a defined user and handoff | Reproduce the finding; change an assumption; challenge the recommendation |
| **[Specialist cases](specialist/README.md)** | FX sensitivity validation, ECL movement, market/collateral risk, data control and negative research | Choose a specific problem; check that case's method, evidence and limits |
| **[Learning laboratory](lab/README.md)** | Small executable exercises in credit, ALM, liquidity, AML and AI controls | Learn and test reasoning; do not infer maturity from the number of models |
| **[References and history](reference/README.md)** | Team coursework, forks and supporting utilities | Inspect provenance and attribution; distinguish study from original contribution |

A specialist case may use a laboratory calculation. That does not promote the calculation into a production product. Repositories keep their own interfaces, assumptions and release cycles. Shared navigation and review standards are not automatic data integration.

## For an interview

Start with the flagship's decision, the evidence that changes it, and what remains unknown. Then choose **one** relevant specialist case. Use the [role-based learning route](learning/README.zh-CN.md) and [unfamiliar case questions](learning/CASE_INTERVIEWS.zh-CN.md) to test your own understanding. Personal mastery starts unassessed; independent studies must not be described as client engagements.

[All repository placements and priorities](catalog/PRIORITIES.md) · [Architecture and promotion criteria](ARCHITECTURE.md) · [Detailed scenario index](scenarios/README.md) · [Verification](validation/README.md)
