# First integrated release verification

Date: 2026-09-15. See [machine-readable evidence](local-20260915.json).

- 24 repository tests passed with the normally installed package on Python 3.12.12, from outside the source checkout.
- All four published JSON examples executed through the installed command. ECL, cash balances/first deficit, bond PV and HHI matched separate hand/Decimal expectations.
- Repeating an output destination returned an error and preserved the complete earlier bundle. Inputs remained unchanged. Each exported payload matched its manifest hash.
- An independent reviewer checked 805 ordinary-range rational/integer numerical cases and identified an extreme intermediate-underflow defect. It was corrected using exponent-scaled multiplication; the failing example and unrepresentable-result error path were separately rechecked.
- Per-model assumptions now accompany both JSON and HTML exports. A complete manifest is written last; interrupted exports without it are incomplete.
- The catalog checks existing public-repository inventory, scenario IDs, required guide sections and local link targets. This is structural validation, not validation of every model or external link.
- A local gitleaks scan found no credential matches. This is not a certification of all rights, authorship or historical repository contents.

This release does not run every older project's tests, prove all scenario workflows implemented, establish external user usability or assess the author's mastery. Public sources and workflow designs are explicitly distinguished from executable implementations in the scenario coverage map.
