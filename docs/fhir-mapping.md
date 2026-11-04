# FHIR ExplanationOfBenefit mapping

How the fields in Synthea's FHIR R4 `ExplanationOfBenefit` (EOB) resources map to what this app explains. Based on the fixtures in `tests/fixtures/` (15 EOBs across 3 patients).

## Line-item adjudication categories

Money lives in `item[].adjudication[]`. Each entry has a `category` (what kind of amount) and an `amount`. Synthea uses the same category codes as CMS Blue Button 2.0, so a parser written against this data should also work on real Medicare data.

All codes are prefixed with `https://bluebutton.cms.gov/resources/variables/`.

| Code | Display | Plain English |
|---|---|---|
| `line_sbmtd_chrg_amt` | Line Submitted Charge Amount | What the provider billed |
| `line_alowd_chrg_amt` | Line Allowed Charge Amount | What the insurer agreed is a fair price |
| `line_prvdr_pmt_amt` | Line Provider Payment Amount | What the insurer actually paid |
| `line_bene_ptb_ddctbl_amt` | Line Beneficiary Part B Deductible Amount | Patient's share applied to their deductible |
| `line_coinsrnc_amt` | Line Beneficiary Coinsurance Amount | Patient's percentage share |
| `line_prcsg_ind_cd` | Line Processing Indicator Code | Status of the line, not a dollar amount |

Patient owes (per line) = deductible + coinsurance.

## Claim-level fields

| FHIR path | Meaning | Notes |
|---|---|---|
| `type.coding[0].code` | Claim type | Seen: `professional`, `pharmacy` |
| `billablePeriod` | When the service happened | |
| `insurer.display` | Payer name | Seen: Humana, UnitedHealthcare, Medicaid, `NO_INSURANCE` |
| `outcome` | Processing status | Always `complete` in the fixtures |
| `total[]` | Claim totals | Only `submitted` appears |
| `payment.amount` | Total paid by the insurer | Often `0.0` |
| `item[].productOrService` | The service or product on the line | Includes a `display` string |
| `item[].net` | Line amount | Matches the submitted charge |

## Quirks to handle

- **Many items have no `adjudication`.** Only 16 of the items in the fixtures have adjudication. The rest are the encounter itself or a listed condition, and some are social findings (for example "Full-time employment (finding)"), not billed services. The explainer must treat these as informational lines, not $0 charges.
- **Uninsured and zero-paid claims are common.** Claims where `insurer.display` is `NO_INSURANCE`, or `payment.amount` is `0.0`, have no line adjudication. The patient is presumably responsible for the full submitted amount, but the data doesn't say so explicitly, so the app should say "no payment recorded" instead of inventing an amount.
- **Floating-point amounts.** Values like `27.200000000000003` appear. Parse amounts as `Decimal` and round to cents. Never use `float` for money.
- **Code systems are mostly not billing codes.** `productOrService` uses SNOMED CT (39 lines), CVX vaccines (2), LOINC (2), ADA CDT dental (1), and RxNorm (1). There are no HCPCS or CPT codes. Every coding includes a `display` string, so the app can show that and use code tables only as a fallback.
- **The processing indicator has no value.** `line_prcsg_ind_cd` entries carry no reason code, so denied lines can't be detected from them in Synthea data.
- **No denied lines in the fixtures.** The closest edge cases are the uninsured and zero-paid claims above. Denied-line tests will need a hand-made fixture.
