import csv,json,sys,tempfile,unittest
from datetime import date,timedelta
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
from analysis import analyse,metrics,load_employees
from generate_data import generate
from build import build

def employee(hire='2025-01-01',exit=None,kind='Voluntary',fte=100):
    return dict(employee_id='E1',department='Engineering',location='Dublin',hire=date.fromisoformat(hire),exit=date.fromisoformat(exit) if exit else None,exit_type=kind if exit else '',fte_hundredths=fte)

class WorkforceTests(unittest.TestCase):
    start=date(2026,1,1);end=date(2026,2,1)
    def test_boundary_events(self):
        rows=[employee(exit='2026-01-01'),employee(hire='2026-01-01'),employee(hire='2026-02-01'),employee(exit='2026-02-01')]
        m=metrics(rows,self.start,self.end)
        self.assertEqual((m['opening'],m['hires'],m['exits'],m['closing']),(2,1,1,2))
        self.assertEqual(m['employee_days'],62)
    def test_daily_average_denominator(self):
        m=analyse([employee(exit='2026-01-16'),employee(hire='2026-01-16')],self.start,self.end)
        self.assertEqual(m['average_headcount'],1)
        self.assertEqual(m['turnover_pct'],100)
    def test_overlap_matches_daily_enumeration(self):
        rows=[employee(),employee(hire='2026-01-10',exit='2026-01-20'),employee(hire='2026-02-03')]
        expected=sum(sum(r['hire']<=self.start+timedelta(days=i) and (r['exit'] is None or r['exit']>self.start+timedelta(days=i)) for r in rows) for i in range(31))
        self.assertEqual(metrics(rows,self.start,self.end)['employee_days'],expected)
    def test_zero_denominator_is_null(self):
        r=analyse([employee(hire='2027-01-01')],self.start,self.end)
        self.assertIsNone(r['turnover_pct']);self.assertEqual(r['summary']['closing'],0)
    def test_fte_and_exit_types(self):
        m=metrics([employee(fte=80),employee(exit='2026-01-05'),employee(exit='2026-01-06',kind='Involuntary')],self.start,self.end)
        self.assertEqual((m['closing_fte_hundredths'],m['voluntary'],m['involuntary']),(80,1,1))
    def test_tenure_anniversary(self):
        m=metrics([employee(hire='2025-01-31'),employee(hire='2025-02-01'),employee(hire='2023-01-31'),employee(hire='2021-01-31')],self.start,self.end)
        self.assertEqual(list(m['tenure'].values()),[1,1,1,1])
    def test_partial_month_and_leap_year(self):
        r=analyse([employee(hire='2020-01-01')],date(2024,2,15),date(2024,3,2))
        months=r['cells'][0]['monthly'];self.assertEqual([m['days'] for m in months],[15,1]);self.assertEqual(sum(m['employee_days'] for m in months),16)
    def test_bad_window(self):
        with self.assertRaises(ValueError):analyse([],self.end,self.start)
    def write_rows(self,root,mutate=None):
        p=Path(root)/'input.csv';rows=generate(p,count=10)
        if mutate:mutate(rows)
        with p.open('w',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
        return p
    def test_duplicates_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=self.write_rows(d,lambda r:r.append(dict(r[0])))
            with self.assertRaisesRegex(ValueError,'Duplicate'):load_employees(p)
    def test_invalid_records_rejected(self):
        changes=[{'fte':'NaN'},{'fte':'0'},{'fte':'1.1'},{'fte':'0.123'},{'hire_date':'bad'},{'department':''},{'exit_date':'2019-01-01','exit_type':'Voluntary'},{'exit_date':'','exit_type':'Voluntary'},{'exit_date':'2035-01-01','exit_type':''}]
        with tempfile.TemporaryDirectory() as d:
            for change in changes:
                with self.subTest(change=change):
                    p=self.write_rows(d,lambda r:r[0].update(change))
                    with self.assertRaises(ValueError):load_employees(p)
    def test_empty_input(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'x.csv';p.write_text('employee_id,department,location,hire_date,exit_date,exit_type,fte\n')
            with self.assertRaises(ValueError):load_employees(p)
    def test_monthly_and_group_reconciliation(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'in.csv';generate(p)
            r=analyse(load_employees(p),date(2025,11,1),date(2026,11,1))
            for key in ['opening','closing','hires','exits','employee_days','voluntary','involuntary']:
                self.assertEqual(sum(c['summary'][key] for c in r['cells']),r['summary'][key])
            for c in r['cells']:
                self.assertEqual(sum(m['employee_days'] for m in c['monthly']),c['summary']['employee_days'])
                self.assertEqual(sum(m['exits'] for m in c['monthly']),c['summary']['exits'])
                for a,b in zip(c['monthly'],c['monthly'][1:]):self.assertEqual(a['closing'],b['opening'])
    def test_reproducible_build_and_aggregate_only_payload(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'in.csv';generate(p)
            a=build(p,Path(d)/'out',Path(d)/'site',date(2025,11,1),date(2026,11,1),True)
            original=(Path(d)/'site/data.js').read_bytes()
            generate(p);b=build(p,Path(d)/'out',Path(d)/'site',date(2025,11,1),date(2026,11,1),True)
            self.assertEqual(a,b);self.assertEqual(original,(Path(d)/'site/data.js').read_bytes())
            self.assertNotIn('employee_id',json.dumps(a));self.assertNotIn('SYN-',json.dumps(a))

if __name__=='__main__':unittest.main()
