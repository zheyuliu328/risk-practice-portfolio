# Flagship · Forecast review and evidence handoff

**User:** an analyst reviewing supplied forecasts for a model owner. **Decision:** whether comparative accuracy supports further consideration, or missing evidence prevents a recommendation. **Handoff:** retained inputs, coverage exceptions, independently checked metrics and a reasoned review memo.

The worked task uses invented monthly revenue, not credit default data. Candidate A appears better on its own available months; candidate B is better on their shared months. The task is to discover why and limit the recommendation accordingly. It reviews supplied predictions, not the original training process.

[Read the answer and action memo](REVIEW_MEMO.md) · [Input contract](INPUT_CONTRACT.md) · [Source provenance](inputs/PROVENANCE.json)

## Run the case

Use Python 3.10+ in a separate environment. From this portfolio checkout:

```sh
python3 -m venv .venv-flagship
source .venv-flagship/bin/activate
python -m pip install 'forecast-review-workbench @ git+https://github.com/zheyuliu328/forecast-review-workbench.git@41dacd968cd9941be0c0c5b4170211f6757ba52c'
forecast-review --review flagship/forecast-review/inputs/request.json --output outputs/flagship-intake
```

This first command deliberately returns **exit 1** and exports a pending review. Open `outputs/flagship-intake/report.html`. It must show 12 expected months, seven common months and five excluded months. Read the missing-period reasons and declarations; nothing is filled with zero.

Only if you accept comparison **on those seven months**, run the separate accepted request:

```sh
forecast-review --review flagship/forecast-review/inputs/request-accepted.json --output outputs/flagship-comparison
```

The only change is `accept_common_sample=true`. Exit 0 means a comparison was computed. It does not approve the model or remove the five exclusions. A blank `review-notes.json` is correct: the CLI does not invent a human opinion. Write your own memo using [the worked memo's structure](REVIEW_MEMO.md), or use the GUI to retain input-bound manual opinions.

Now challenge the control:

```sh
forecast-review --review flagship/forecast-review/inputs/request-conflicting-unit.json --output outputs/flagship-unit-conflict
```

This declares one candidate as EUR while the target remains USD. It must return **exit 1**, retain the conflict and block comparison even though sample acceptance is true. This is a declared-unit inconsistency, not currency conversion. Rerunning any existing output directory must return exit 2 without replacing it.

Each output contains offline HTML, results, mapped input rows, evaluation rows, metrics, issues, declarations, notes and fingerprints. Preserve the whole directory. All paths above must be new; use different names for another run.

## Independently check the evidence

```sh
python scripts/verify_flagship.py --output outputs/flagship-regression
```

This automated check replays all three states and uses raw CSVs with separate Decimal arithmetic to recalculate metrics. It checks excluded periods, exported checksums, empty manual notes and refusal to overwrite. It is a developer regression check; its automatic use of the accepted fixture does not demonstrate that a person understood or accepted the sample.

## Use the actual interface and your own inputs

Run `forecast-review` to open the local application. Select these CSVs through its file pickers and map their different headers. Follow the [Workbench guide](https://github.com/zheyuliu328/forecast-review-workbench/blob/main/docs/QUICKSTART.zh-CN.md) to declare scope, inspect exclusions, accept the common sample, add reasons and export. Real first-time human acceptance remains unverified by this portfolio.

When moving to another task, supply your own dates, target, unit, horizon and sources. Do not reuse the accepted fixture as a default policy. No employer/client data is needed to practise.

## Progress to model production and holdout review

The Workbench already provides **Training experiments → explicit holdout reveal → transfer to Forecast review**. It keeps attempted candidates, failures, baseline evidence and development selection. It requires declared lags/release delays, and transferred forecasts still require sample acceptance. Use its [training contract](https://github.com/zheyuliu328/forecast-review-workbench/blob/main/docs/EXTENSION_CONTRACT.md).

The numerical kernel is pinned from [Model Risk Lab](https://github.com/zheyuliu328/model-risk-lab); these are shared calculations, not two independent validators. The raw-CSV metric check above is separate. This first case does not run or certify all training/holdout workflows.

[Choose one specialist case](../../specialist/README.md) · [Portfolio](../../README.md)
