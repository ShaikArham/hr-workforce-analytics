"""Descriptive workforce flows. Exit date is the first inactive day."""
import csv
from collections import Counter
from datetime import date, timedelta
from decimal import Decimal, InvalidOperation

FIELDS = {'employee_id','department','location','hire_date','exit_date','exit_type','fte'}


def load_employees(path):
    rows = []
    seen = set()
    with open(path, newline='', encoding='utf-8-sig') as handle:
        reader = csv.DictReader(handle)
        if not FIELDS.issubset(reader.fieldnames or []):
            raise ValueError('Missing required columns')
        for line, raw in enumerate(reader, 2):
            try:
                r = {k: (raw[k] or '').strip() for k in FIELDS}
                if not all(r[k] for k in ('employee_id','department','location','hire_date','fte')):
                    raise ValueError('Required value is blank')
                if r['employee_id'] in seen:
                    raise ValueError('Duplicate employee_id; rehire spells are not supported')
                hire = date.fromisoformat(r['hire_date'])
                exit_day = date.fromisoformat(r['exit_date']) if r['exit_date'] else None
                if exit_day is not None and exit_day <= hire:
                    raise ValueError('exit_date must be after hire_date')
                if (exit_day is None and r['exit_type']) or (exit_day and r['exit_type'] not in ('Voluntary','Involuntary')):
                    raise ValueError('Exit type must match exit date')
                fte = Decimal(r['fte'])
                if not fte.is_finite() or not Decimal('0') < fte <= Decimal('1') or fte.as_tuple().exponent < -2:
                    raise ValueError('fte must be > 0 and <= 1, with at most 2 decimals')
                rows.append(dict(employee_id=r['employee_id'], department=r['department'],location=r['location'],hire=hire,exit=exit_day,exit_type=r['exit_type'],fte_hundredths=int(fte*100)))
                seen.add(r['employee_id'])
            except (ValueError, InvalidOperation) as exc:
                raise ValueError(f'Row {line}: {exc}') from exc
    if not rows:
        raise ValueError('Input contains no employees')
    return rows


def month_ranges(start, end):
    cursor = start
    while cursor < end:
        next_month = date(cursor.year+1,1,1) if cursor.month == 12 else date(cursor.year,cursor.month+1,1)
        stop = min(end,next_month)
        yield cursor, stop
        cursor = stop


def metrics(rows, start, end):
    """Opening/closing are immediately before events on their boundary date."""
    if end <= start:
        raise ValueError('end must be after start')
    opening = sum(r['hire'] < start and (r['exit'] is None or r['exit'] >= start) for r in rows)
    current = [r for r in rows if r['hire'] < end and (r['exit'] is None or r['exit'] >= end)]
    hires = sum(start <= r['hire'] < end for r in rows)
    exits = [r for r in rows if r['exit'] is not None and start <= r['exit'] < end]
    employee_days = sum(max(0,(min(end,r['exit'] or end)-max(start,r['hire'])).days) for r in rows)
    tenure = Counter({'Under 1 year':0,'1–3 years':0,'3–5 years':0,'5+ years':0})
    last_day = end-timedelta(days=1)
    for r in current:
        anniversary_years = last_day.year-r['hire'].year-((last_day.month,last_day.day)<(r['hire'].month,r['hire'].day))
        bucket = 'Under 1 year' if anniversary_years < 1 else '1–3 years' if anniversary_years < 3 else '3–5 years' if anniversary_years < 5 else '5+ years'
        tenure[bucket] += 1
    assert opening + hires - len(exits) == len(current)
    return dict(opening=opening,closing=len(current),hires=hires,exits=len(exits),voluntary=sum(r['exit_type']=='Voluntary' for r in exits),involuntary=sum(r['exit_type']=='Involuntary' for r in exits),employee_days=employee_days,closing_fte_hundredths=sum(r['fte_hundredths'] for r in current),tenure=dict(tenure))


def analyse(rows, start, end, synthetic=False):
    if end <= start:
        raise ValueError('end must be after start')
    cells = []
    for department, location in sorted({(r['department'],r['location']) for r in rows}):
        subset = [r for r in rows if r['department']==department and r['location']==location]
        cells.append(dict(department=department,location=location,summary=metrics(subset,start,end),monthly=[dict(start=a.isoformat(),end=b.isoformat(),days=(b-a).days,**metrics(subset,a,b)) for a,b in month_ranges(start,end)]))
    total = metrics(rows,start,end)
    avg = total['employee_days']/(end-start).days
    return dict(start=start.isoformat(),end=end.isoformat(),days=(end-start).days,synthetic=synthetic,input_records=len(rows),departments=sorted({r['department'] for r in rows}),locations=sorted({r['location'] for r in rows}),summary=total,average_headcount=avg,turnover_pct=100*total['exits']/avg if avg else None,cells=cells)
