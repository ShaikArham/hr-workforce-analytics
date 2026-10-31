# Workforce Atlas · HR Analytics

An auditable Python workforce analysis pipeline and interactive HR dashboard built by Shaik Arham Saquib.

**The 800 supplied employee records are fictional.** This is a new portfolio demonstration built in October 2026, not a report for a real employer or evidence of historical commercial results.

## Run locally

Requires Python 3.12 or later. No external Python packages are needed.

```bash
python scripts/generate_data.py
python scripts/build.py --synthetic
python -m unittest discover -s tests -v
python -m http.server 8000 --directory site
```

Open http://localhost:8000 or open `site/index.html` directly. Prebuilt outputs are included.

## What the project demonstrates

- Input validation, unique employee IDs and consistent event dates.
- Headcount reconciliation: opening + hires − exits = closing.
- Turnover using average daily headcount, rather than an unexplained denominator.
- Voluntary/involuntary exits, closing FTE and completed-years tenure.
- Department/location filters that update every chart and table.
- Monthly CSV export, accessible chart tables and responsive presentation.
- Reproducible generation and automated calculation/reconciliation tests.
- Aggregate-only dashboard payload: no employee IDs or individual scores.

## Reproduced fictional results

Period: **1 November 2025 inclusive to 1 November 2026 exclusive**. Generator seed: 73.

| Measure | Sample result |
|---|---:|
| Input employee records | 800 |
| Opening headcount | 536 |
| Hires | 125 |
| Exits | 46 |
| Closing headcount | 615 |
| Closing FTE | 524.5 |
| Average daily headcount | 576.08 |
| Period turnover | 7.99% |
| Voluntary / involuntary exits | 38 / 8 |

These statistics describe the synthetic dataset. They are not measured improvements or market benchmarks.

## Metric definitions

Hire date is the first active day. Exit date is the first inactive day. The reporting window is `[start, end)`.

Opening headcount is the workforce immediately before events on the start date: hire date < start and exit date is blank or ≥ start. Closing headcount uses the same rule at the end date. An exit on the start date is counted in opening and period exits. An exit on the end date is counted in closing and in the next period's exits. This convention preserves flow reconciliation.

Active employee-days sum each employee's overlap with the reporting window. Average daily headcount = employee-days / calendar days. Period turnover = exits / average daily headcount × 100. This rate is not annualised. A zero denominator returns null in JSON and N/A on screen. Short periods can produce rates above 100%, especially with rapid replacement.

FTE sums the fixed contract fraction of closing employees. It does not estimate hours actually worked. Tenure uses completed calendar years on the last included date. A leap-day hire reaches the next completed year on 1 March in non-leap years.

All dashboard measures follow department/location filters. Aggregate turnover is recalculated from aggregate employee-days, never averaged from departmental percentages.

## Own data

Follow [the data dictionary](docs/data-dictionary.md), then run:

```bash
python scripts/build.py --input /path/to/employees.csv --start 2025-11-01 --end 2026-11-01
```

Omit `--synthetic` for non-fictional data. The sample repository is public and contains fictional data only. Do not commit real employee data. Aggregate output can also reveal information in small groups, so it requires a disclosure review before any real-world publication. The dashboard itself sends no data to a server.

## Repository map

- `src/analysis.py`: validation, dates, metrics and grouped results.
- `scripts/generate_data.py`: reproducible fictional employee data.
- `scripts/build.py`: JSON, CSV and static dashboard payload.
- `data/employees.csv`: synthetic employee spells.
- `outputs/`: aggregate JSON, workforce summary CSV and monthly flows CSV.
- `site/`: HTML/CSS/JavaScript dashboard.
- `tests/`: boundary, denominator, FTE, tenure and reconciliation tests.
- `docs/`: definitions, validation notes and an optional Power BI guide.

## Scope and limitations

Each employee has one employment spell and fixed department, location and FTE. Rehires, internal transfers, leave, historic contract changes, payroll, hiring funnels and reasons for leaving are not modelled. Future hire/exit dates are permitted; only events within the window affect flows. Future scheduled exits do not count as current departures.

This is descriptive reporting. It does not predict attrition, identify causes, score employees, recommend employment decisions or include a Power BI `.pbix` file. The generator creates illustrative patterns, not realistic labour-market estimates.

## Interview walkthrough

1. Explain the business question: how did workforce size and composition change?
2. Show the data contract and invalid-record handling.
3. Reconcile 536 + 125 − 46 = 615.
4. Explain why turnover uses 576.08 average daily employees, not 615 closing employees.
5. Filter a department and location, then export and reconcile monthly figures.
6. Discuss limitations and how an effective-dated employment history would support transfers and rehires.
