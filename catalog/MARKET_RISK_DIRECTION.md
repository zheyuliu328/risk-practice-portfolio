# Market-risk project direction

Updated 2026-09-29. Current delivery and evidence boundaries, not a promise of investment performance.

## Two CV projects

1. [Options Risk Workbench](https://github.com/zheyuliu328/options-risk-workbench): [public browser tool](https://options-risk-zheyuliu.mystic-pear-2111.chatgpt.site) for fixed-contract European BSM/American CRR valuation, signed exposures, spot/volatility/time scenarios and JSON/HTML reports. Twenty-three numerical and workflow tests passed. Browser results matched native Python within 1e-8 relative numeric tolerance. Inputs and examples are independently invented; user inputs are calculated in the browser.
2. [Forecast Review Workbench](https://github.com/zheyuliu328/forecast-review-workbench), with Model Risk Lab as its numerical foundation: common-sample comparison, temporal candidate evaluation and traceable reviewer outputs. Present these as one application/foundation story, not two independent flagship projects.

## MSc research connection

[QQQ coursework](https://github.com/zheyuliu328/RMSC6007-GroupProject) supplies the financial research question. The original documentation attributes the daily pipeline and comparative analysis to Zheyu and the contract-level pipeline to Ernest; team work is not sole-authored.

A separate local corrected retrospective evaluation was completed on 2026-09-29. It uses horizon-aware label-availability boundaries, training-only preprocessing, a constant baseline and validation-only model selection. Unknown forward labels remain excluded. Structural counterexamples and independent metric/label checks passed. This is not an exact reproduction of the old tuned models or an unseen blind test: the historical evaluation period was already viewed during earlier research. Old AUC, Sharpe and trading-return claims remain excluded.

The public tool is independently implemented. No team source, raw market data or daily research predictions are distributed here. Data-vintage certification and redistribution rights remain unverified. Forecasts are not automatically connected to scenario valuation.

## Supporting projects

- Table Check: supporting data-control utility; no primary CV slot.
- VaR backtesting: single-return-series historical/normal VaR and unconditional coverage, not portfolio VaR/ES or capital compliance.
- Credit/NLP experiments and reference forks: learning or research material with explicit attribution and limits, not additional mature products.

## Scope beyond this delivery

A historically executable trading ledger, discrete dividends, market-data adapters, automatic research-to-scenario mapping and independently verified portfolio VaR/ES are future extensions. They are not required to use the current scenario tool and are not completed capabilities. No claim of bank-desk work, production adoption or realised profit follows from this portfolio.
