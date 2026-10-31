# Data contract and output guide

Input is UTF-8 CSV, one employment spell per unique employee ID. The sample is entirely fictional. Additional columns are ignored.

| Column | Rule |
|---|---|
| employee_id | Required, unique, nonblank string |
| department | Required, nonblank string; fixed throughout spell |
| location | Required, nonblank string; fixed throughout spell |
| hire_date | Required ISO date YYYY-MM-DD; first active day |
| exit_date | Blank or ISO date strictly after hire_date; first inactive day |
| exit_type | Blank if no exit date; otherwise Voluntary or Involuntary |
| fte | Decimal greater than 0 and no greater than 1; at most 2 decimal places |

Duplicate IDs, same-day hire/exit, incomplete records, nonfinite FTE and invalid exit types are rejected with a row number. Empty input is rejected. An employee must have at least one active calendar day. Rehire spells need a different effective-dated schema and are not supported here.

## Outputs

`workforce_summary.csv`: one department/location combination per row. `monthly_flows.csv`: one combination/month per row, including partial months. `analysis.json` and `site/data.js`: aggregate cells, summary, time window and dataset label, without employee IDs.

| Output field | Meaning |
|---|---|
| opening / closing | Headcount immediately before events on respective boundary dates |
| hires / exits | Events within the half-open reporting window |
| voluntary / involuntary | Mutually exclusive exit counts |
| employee_days | Sum of active days intersecting reporting window |
| closing_fte_hundredths | FTE × 100, stored as an integer |
| tenure | Closing employees by completed-year buckets |
| days | Calendar days in the corresponding window |

Turnover is derived from exits and employee-days, not stored as a rounded percentage per cell. Never average subgroup turnover percentages. The browser CSV includes unrounded rates, selected filters and denominators for reconciliation.

Small groups are displayed for this fictional demonstration. No disclosure suppression suitable for real employee data has been implemented.
