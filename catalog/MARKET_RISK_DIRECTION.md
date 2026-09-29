# Market-risk project direction

Updated 2026-09-29. This is a presentation and development map, not a claim that an integrated options-risk application is already delivered.

## Existing work worth examining

- **QQQ implied-volatility research**: [MSc team project](https://github.com/zheyuliu328/RMSC6007-GroupProject). The local project documentation attributes the daily pipeline and comparative analysis to Zheyu, and the contract-level pipeline to Ernest. Team modules are not sole-authored work. Historical AUC, Sharpe and strategy returns are excluded from current showcase claims pending consistent-version reproduction and backtest repair. The academic archive is not a deployed trading system.
- **Forecast Review Workbench + Model Risk Lab**: one application and its numerical foundation, not two unrelated flagship projects. Shows common-sample forecast comparison, time-based candidate evaluation, traceable outputs and independent numerical checks. Monthly regression review is not portfolio market-risk measurement.
- **VaR backtesting**: a supporting market-risk module. Current scope includes historical/normal VaR and unconditional coverage testing. It does not establish ES validation, exception independence, derivatives full revaluation or regulatory capital compliance.
- **Table Check**: a useful supporting data-control utility. It remains available, but is not the main finance research project.

## Proposed integration: volatility and options-risk analysis

The target workflow is to load a documented sample position, inspect volatility and exposures, apply spot/volatility/time shocks, explain position and portfolio P&L, and export assumptions and results. It is planned work, not current functionality.

1. Establish a single academic source version, module attribution and permitted data provenance. Keep third-party option data out of the public distribution unless redistribution rights are established.
2. Repair evaluation boundaries: forward-label availability, horizon-aware train/test separation, training-only transformations and development-only threshold selection. Preserve a final unseen evaluation period.
3. Revalue the same option contract at exit: fixed strike, expiry and quantity; explicit time units, transaction costs, overlap policy and portfolio cash accounting. Separate model-priced scenarios from historically executable trading results.
4. Add independently checked Greeks and full-revaluation spot/volatility/time scenarios. Explain approximation residuals and concentration; add portfolio VaR/ES only with an explicit loss definition and separate verification.
5. Publish a small browser workflow using independently invented examples. Verify sample import, invalid-input handling, shock results and exported evidence before describing it as available.

The purpose is to connect academic volatility research with practical risk explanation. No investment-performance, bank-desk experience, production-use or regulatory-compliance claim follows from the roadmap.
