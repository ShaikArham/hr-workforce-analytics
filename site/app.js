'use strict';
(() => {
const D=window.HR_DATA, $=id=>document.getElementById(id);
const escape=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const num=n=>new Intl.NumberFormat('en-IE',{maximumFractionDigits:1}).format(n);
const keys=['opening','closing','hires','exits','voluntary','involuntary','employee_days','closing_fte_hundredths'];
function sum(rows){const s=Object.fromEntries(keys.map(k=>[k,0]));s.tenure={};for(const r of rows){for(const k of keys)s[k]+=r[k];for(const [k,v] of Object.entries(r.tenure))s.tenure[k]=(s.tenure[k]||0)+v;}return s;}
function rate(s,days){return s.employee_days?num(100*s.exits/(s.employee_days/days))+'%':'N/A';}
function cells(){return D.cells.filter(c=>(!$('department').value||c.department===$('department').value)&&(!$('location').value||c.location===$('location').value));}
function months(cs){return D.cells[0].monthly.map((m,i)=>({start:m.start,days:m.days,...sum(cs.map(c=>c.monthly[i]))}));}
for(const [id,list] of [['department',D.departments],['location',D.locations]])for(const name of list){const option=document.createElement('option');option.value=name;option.textContent=name;$(id).append(option);}
$('dataset').textContent=D.synthetic?'FICTIONAL WORKFORCE DATA':'WORKFORCE DATA';
$('period').textContent=`${D.start} to ${D.end} (end exclusive)`;
$('quality').textContent=`${num(D.input_records)} validated input records. Duplicate IDs, invalid dates and invalid FTE are rejected. Only aggregates enter this dashboard. The supplied sample uses seed 73 and contains no real employees.`;
function render(){
 const cs=cells(),s=sum(cs.map(c=>c.summary)),ms=months(cs),delta=s.closing-s.opening;
 $('headcount').textContent=num(s.closing);$('hires').textContent=num(s.hires);$('exits').textContent=num(s.exits);$('turnover').textContent=rate(s,D.days);
 $('change').textContent=`${delta>=0?'+':''}${num(delta)} from ${num(s.opening)} opening employees`;
 $('exit-mix').textContent=`${s.voluntary} voluntary · ${s.involuntary} involuntary`;
 $('fte').textContent=num(s.closing_fte_hundredths/100);$('average').textContent=num(s.employee_days/D.days);
 $('status').textContent=`${$('department').value||'All departments'} · ${$('location').value||'All locations'}. All charts and tables follow these filters. Rates cover ${D.days} calendar days.`;
 $('bridge').innerHTML=[['Opening',s.opening],['Hires',s.hires],['Exits',s.exits],['Closing',s.closing]].map(([label,value],i)=>(i?`<b aria-hidden="true">${['','+','−','='][i]}</b>`:'')+`<div><strong>${num(value)}</strong><span>${label}</span></div>`).join('');
 const max=Math.max(1,...ms.map(m=>m.closing));
 $('trend').innerHTML=ms.map(m=>`<div class="bar-col"><b>${m.closing}</b><div class="bar" style="height:${m.closing/max*85}%" title="${escape(m.start)}: ${m.closing}"></div><small>${escape(m.start.slice(2,7))}</small></div>`).join('');
 $('months').innerHTML=ms.map(m=>`<tr><td>${escape(m.start.slice(0,7))}</td>${['opening','hires','exits','closing'].map(k=>`<td>${m[k]}</td>`).join('')}<td>${rate(m,m.days)}</td></tr>`).join('');
 const buckets=['Under 1 year','1–3 years','3–5 years','5+ years'];
 $('tenure').innerHTML=buckets.map(k=>`<div class="tenure-row"><div><span>${k}</span><span>${s.tenure[k]||0} employees · ${s.closing?num(100*(s.tenure[k]||0)/s.closing):0}%</span></div><div class="track"><i style="width:${s.closing?100*(s.tenure[k]||0)/s.closing:0}%"></i></div></div>`).join('');
 let depts=[...new Set(cs.map(c=>c.department))].map(department=>({department,...sum(cs.filter(c=>c.department===department).map(c=>c.summary))}));
 depts.sort((a,b)=>$('sort').value==='department'?a.department.localeCompare(b.department):b[$('sort').value]-a[$('sort').value]||a.department.localeCompare(b.department));
 $('departments').innerHTML=depts.length?depts.map(d=>`<tr><td>${escape(d.department)}</td>${['opening','hires','exits','closing'].map(k=>`<td>${d[k]}</td>`).join('')}<td>${d.closing-d.opening}</td><td>${rate(d,D.days)}</td></tr>`).join(''):'<tr><td colspan="7">No records for this combination. Try Reset.</td></tr>';
}
['department','location','sort'].forEach(id=>$(id).addEventListener('change',render));
$('reset').addEventListener('click',()=>{$('department').value='';$('location').value='';$('sort').value='closing';render();});
function csv(value){let s=String(value);if(/^[=+\-@\t\r]/.test(s))s="'"+s;return '"'+s.replace(/"/g,'""')+'"';}
$('export').addEventListener('click',()=>{const rows=months(cells()).map(m=>({month:m.start,department:$('department').value||'All departments',location:$('location').value||'All locations',opening:m.opening,hires:m.hires,exits:m.exits,closing:m.closing,employee_days:m.employee_days,calendar_days:m.days,turnover_pct:m.employee_days?100*m.exits/(m.employee_days/m.days):''}));const fields=Object.keys(rows[0]);const text=[fields,...rows.map(r=>fields.map(f=>r[f]))].map(r=>r.map(csv).join(',')).join('\r\n');const url=URL.createObjectURL(new Blob([text],{type:'text/csv;charset=utf-8'}));const a=document.createElement('a');a.href=url;a.download='workforce-monthly.csv';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);});
render();
})();
