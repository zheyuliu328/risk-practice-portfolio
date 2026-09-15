# Worked review memo · Candidate accuracy under incomplete coverage

**Status: teaching example; needs further evidence.** This is an illustrative reviewer response, not an approval, client deliverable or claim of actual work experience.

## Decision and finding

Candidate B has lower error than A and the supplied baseline on the seven comparable months. That supports a narrowly scoped comparative statement. It does not justify full-year adoption: five of twelve expected months are excluded, including the final quarter absent from A. Request the missing-period explanations and timestamped forecast history before recommending adoption.

## Independent evidence

| Metric | Candidate A | Candidate B | Baseline |
| --- | --- | --- | --- |
| Available months | 9 | 10 | 12 |
| Available-sample MAE | 14/9 ≈ 1.5556 | 43/10 = 4.3 | 3 |
| Common months | 7 | 7 | 7 |
| Common MAE | 2 | 1 | 3 |
| Common RMSE | 2 | 1 | 3 |
| Common signed bias | +2 | +1 | +3 |

Own-sample ranking is misleading because samples differ. On the common months each candidate's error is constant, making the MAE/RMSE/bias check directly inspectable. Excluded months remain April, May, October, November and December. Lower common-sample error is not proof that omitted difficult months would behave similarly.

## Findings and action register

| Finding | Consequence | Action / owner | Closure evidence |
| --- | --- | --- | --- |
| Different missing periods | Own-sample ranking cannot select a model fairly | Analyst preserves exclusions; model owner explains omissions | Complete coverage or justified restricted intended use, followed by a new review |
| Forecasts are supplied, not fitted here | Leakage and holdout independence remain unknown | Model owner supplies timestamped production/training records; independent reviewer challenges | Source vintage and selection history tied to the evaluated forecasts |
| B beats baseline on a partial sample | Useful evidence but not an adoption decision | Reviewer states scope; authorized owner decides next investigation | Representative out-of-sample evidence and approved use limits |
| Conflicting-unit request fails | Even accepted sample cannot fix incompatible definitions | Data owner corrects the declaration or supplies genuinely comparable values | New source/declaration and fresh review; not relabeling to conceal a real conversion need |

No institution-specific finding severity or risk appetite is invented. Priorities here follow whether the issue blocks the stated conclusion.

## Handoff and challenge

Attach the intake, accepted comparison and unit-conflict evidence directories, plus your own signed/date-stamped reasoning when doing a real exercise. The shipped CLI notes remain empty. File hashes preserve identity but are not proof of truthful declarations.

An unfamiliar reviewer should independently reproduce 14/9, 4.3 and 2/1/3 from the raw CSVs. Then ask: would filling the omitted periods reverse the ranking? What evidence makes those additional forecasts genuinely out-of-sample? Never fabricate missing forecasts solely to make the case pass.

The next experiment is broader representative evaluation with known forecast vintage. Independent human usability and repeat-use evidence remain open.
