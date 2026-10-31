"""Build aggregate-only workforce dashboard data and CSV reports."""
import argparse,csv,json,sys
from datetime import date
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from analysis import analyse,load_employees

def build(path,out,site,start,end,synthetic=False):
    result=analyse(load_employees(path),start,end,synthetic)
    out=Path(out);site=Path(site);out.mkdir(parents=True,exist_ok=True);site.mkdir(parents=True,exist_ok=True)
    payload=json.dumps(result,indent=2,sort_keys=True,ensure_ascii=True)
    (out/'analysis.json').write_text(payload+'\n',encoding='utf-8')
    (site/'data.js').write_text('window.HR_DATA = '+payload+';\n',encoding='utf-8')
    for filename,records in [('workforce_summary.csv',[dict(department=c['department'],location=c['location'],**{k:v for k,v in c['summary'].items() if k!='tenure'}) for c in result['cells']]),('monthly_flows.csv',[dict(department=c['department'],location=c['location'],**{k:v for k,v in m.items() if k!='tenure'}) for c in result['cells'] for m in c['monthly']])]:
        with (out/filename).open('w',newline='',encoding='utf-8') as f:
            w=csv.DictWriter(f,fieldnames=list(records[0]),lineterminator='\n');w.writeheader();w.writerows(records)
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input',type=Path,default=ROOT/'data/employees.csv')
    p.add_argument('--start',type=date.fromisoformat,default=date(2025,11,1))
    p.add_argument('--end',type=date.fromisoformat,default=date(2026,11,1))
    p.add_argument('--out',type=Path,default=ROOT/'outputs')
    p.add_argument('--site',type=Path,default=ROOT/'site')
    p.add_argument('--synthetic',action='store_true')
    a=p.parse_args()
    try:r=build(a.input,a.out,a.site,a.start,a.end,a.synthetic)
    except ValueError as e:p.exit(2,str(e)+'\n')
    print(json.dumps({k:r[k] for k in ['summary','average_headcount','turnover_pct']},indent=2))
