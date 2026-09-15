# Input and evidence contract

| Field | Required meaning for this case | Failure or limitation |
| --- | --- | --- |
| Population | January–December 2024, 12 expected monthly target periods, one aggregate series | The shared seven months are not the full year |
| Target | Monthly revenue, USD, untransformed, one-month forecast horizon | Supplied declarations do not establish original training or forecast vintage |
| Actual | `actual.csv`: Month → period, Observed → value | Newly invented values; not business data |
| Candidate A | `candidate-a.csv`: period → period, Forecast → value | Nine months; absent October–December |
| Candidate B | `candidate-b.csv`: snapshot → period, prediction → value | Ten months; absent April–May |
| Baseline | `baseline.csv`: Month → period, Reference → value | Supplied invented benchmark, not a fitted persistence model |
| Sample acceptance | False in intake; explicit true only in a separate request | Acceptance limits the comparison; does not cure coverage gaps |
| Unit challenge | Candidate A declares EUR against target USD | Must block; no conversion assumed |
| Sign | Residual = forecast − actual | Positive bias means overprediction |

Fixtures are exact copies of the author's already public invented Workbench case, pinned in [PROVENANCE.json](inputs/PROVENANCE.json). They are not a new independent validation dataset. Accepted and conflicting requests are transparent derivatives; the original source license is retained.

Model-owner evidence still needed before adoption: release timestamps, fitting and selection history, missing-period explanations, representative evaluation population, materiality and intended use. No CLI success can supply those facts.
