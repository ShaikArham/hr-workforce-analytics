"""Create fictional employee spells with reproducible seed 73."""
import csv, random
from datetime import date, timedelta
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def generate(path, seed=73, count=800):
    rng=random.Random(seed)
    departments=['Engineering','Customer Support','Finance','Operations','People','Sales']
    first=date(2020,1,1)
    rows=[]
    for i in range(count):
        hire=first+timedelta(days=rng.randrange((date(2026,11,1)-first).days))
        leave=hire+timedelta(days=rng.randrange(45,1800)) if rng.random()<0.38 else None
        rows.append(dict(employee_id=f'SYN-{i+1:04}',department=rng.choice(departments),location=rng.choices(['Dublin','Cork','Galway'],[6,2,2])[0],hire_date=hire.isoformat(),exit_date=leave.isoformat() if leave else '',exit_type=rng.choices(['Voluntary','Involuntary'],[8,2])[0] if leave else '',fte=rng.choice(['1.00','1.00','1.00','0.80','0.50'])))
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
    return rows

if __name__=='__main__':
    print(f'Generated {len(generate(ROOT/"data/employees.csv"))} fictional employee records')
