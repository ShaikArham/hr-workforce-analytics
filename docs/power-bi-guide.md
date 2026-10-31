# Optional Power BI rebuild

This repository does not contain a `.pbix` file. This guide explains how to reproduce the aggregate measures.

1. Import `outputs/monthly_flows.csv` as MonthlyFlows and `outputs/workforce_summary.csv` as WorkforceSummary.
2. Create distinct department and location dimension tables with one-to-many relationships to both outputs. Use those dimensions for slicers, with single-direction filtering.
3. Use WorkforceSummary for full-period opening/closing cards and FTE. Use MonthlyFlows for month-level charts. Do not sum monthly opening or closing counts into full-period headcount.
4. Convert closing_fte_hundredths to FTE by dividing by 100.
5. At month level, average daily headcount = SUM(employee_days) / MAX(days), as days repeat across department/location cells. Monthly turnover = DIVIDE(SUM(exits), average daily headcount) * 100.
6. For full-period cards, use the total window duration from `analysis.json` (365 days for the supplied sample): average headcount = SUM(WorkforceSummary[employee_days]) / 365. Replace the hardcoded duration when changing the analysis window.
7. Show voluntary/involuntary exit totals, a headcount bridge and monthly closing trend. Include the same date conventions and synthetic-data label as the browser dashboard.

Validate totals against the README and the exported CSVs before presenting a rebuilt report. These are descriptive workforce metrics, not employee performance or attrition predictions.
