const fmtInt=new Intl.NumberFormat('en-US');
const fmtPct=new Intl.NumberFormat('en-US',{minimumFractionDigits:1,maximumFractionDigits:1});

function signedInt(value){return `${value>=0?'+':''}${fmtInt.format(value)}`;}
function signedPct(value){return value===null?'n/a':`${value>=0?'+':''}${fmtPct.format(value)}%`;}

function renderTrend(target, profile){
  const series=profile.series;
  const width=760,height=240,pad={l:46,r:20,t:18,b:34};
  const values=series.map(row=>row.nonresident_enrollment);
  const max=Math.max(...values), min=Math.min(...values,0);
  const x=i=>pad.l+i/(series.length-1)*(width-pad.l-pad.r);
  const y=value=>height-pad.b-(value-min)/(Math.max(max-min,1))*(height-pad.t-pad.b);
  const points=series.map((row,i)=>`${x(i)},${y(row.nonresident_enrollment)}`).join(' ');
  const ticks=[0,.5,1].map(frac=>{
    const value=min+(max-min)*frac;
    const yy=y(value);
    return `<line x1="${pad.l}" y1="${yy}" x2="${width-pad.r}" y2="${yy}" stroke="#d9e1e8"/><text x="${pad.l-8}" y="${yy+4}" text-anchor="end" font-size="11" fill="#526274">${value>=1000?`${Math.round(value/1000)}k`:Math.round(value)}</text>`;
  }).join('');
  const dots=series.map((row,i)=>`<circle cx="${x(i)}" cy="${y(row.nonresident_enrollment)}" r="4" fill="#0b776e"><title>${row.year}: ${fmtInt.format(row.nonresident_enrollment)}</title></circle>`).join('');
  target.innerHTML=`<svg viewBox="0 0 ${width} ${height}" role="img" aria-label="${profile.state_name} U.S. nonresident enrollment from ${series[0].year} through ${series[series.length-1].year}">${ticks}<polyline points="${points}" fill="none" stroke="#0b776e" stroke-width="3" stroke-linejoin="round" stroke-linecap="round"/>${dots}<text x="${pad.l}" y="${height-8}" font-size="11" fill="#526274">${series[0].year}</text><text x="${width-pad.r}" y="${height-8}" text-anchor="end" font-size="11" fill="#526274">${series[series.length-1].year}</text></svg>`;
}

function fillTable(target, rows, columns){
  target.replaceChildren();
  rows.forEach(row=>{
    const tr=document.createElement('tr');
    columns.forEach(formatter=>{const td=document.createElement('td');td.textContent=formatter(row);tr.appendChild(td);});
    target.appendChild(tr);
  });
}

async function init(){
  const response=await fetch('data/state_profiles.json');
  if(!response.ok) throw new Error(`State profile data load failed: ${response.status}`);
  const data=await response.json();
  const requested=(new URLSearchParams(location.search).get('state')||'AZ').toUpperCase();
  const code=data.profiles[requested]?requested:'AZ';
  const p=data.profiles[code], latest=p.latest, changes=p.changes;
  document.querySelector('#state-profile-eyebrow').textContent=`NCES / IPEDS · State profile · ${data.coverage.start_year}–${data.coverage.end_year}`;
  document.title=`${p.state_name} U.S. Nonresident Enrollment | Higher Education Data Brief`;
  document.querySelector('#state-profile-title').textContent=`${p.state_name}: U.S. nonresident enrollment`;
  document.querySelector('#state-profile-lede').textContent=`A state-level view of the same NCES/IPEDS series used in the national research brief, including composition, recovery, institution concentration, and annual trend.`;
  document.querySelector('#state-profile-status').textContent=`Fall ${latest.year} ${data.coverage.latest_data_status}`;
  document.querySelector('#profile-total-label').textContent=`Fall ${latest.year} U.S. nonresident`;
  document.querySelector('#profile-composition-label').textContent=`${latest.year} composition`;
  document.querySelector('#profile-start-change-label').textContent=`Change since ${data.coverage.start_year}`;
  const md=document.querySelector('#state-markdown-link'); md.href=`downloads/state_profiles/${code}.md`; md.textContent=`Download ${p.state_name} profile notes`;
  document.querySelector('#profile-total').textContent=fmtInt.format(latest.nonresident_enrollment);
  document.querySelector('#profile-institutions').textContent=`${fmtInt.format(latest.institution_count)} institutions`;
  document.querySelector('#profile-share').textContent=`${latest.nonresident_share_pct.toFixed(2)}%`;
  document.querySelector('#profile-recovery-change').textContent=signedPct(changes.since_2019.pct);
  document.querySelector('#profile-recovery-status').textContent=changes.since_2019.recovery_status;
  document.querySelector('#profile-latest-change').textContent=signedInt(changes.latest_year.absolute);
  document.querySelector('#profile-latest-years').textContent=`${changes.latest_year.prior_year} → ${latest.year} (${signedPct(changes.latest_year.pct)})`;
  document.querySelector('#profile-recovery-pill').textContent=changes.since_2019.recovery_status;
  document.querySelector('#profile-grad-share').textContent=`${fmtPct.format(latest.graduate_share_pct)}%`;
  document.querySelector('#profile-undergrad').textContent=fmtInt.format(latest.undergraduate_nonresident);
  document.querySelector('#profile-grad').textContent=fmtInt.format(latest.graduate_nonresident);
  document.querySelector('#profile-decade-change').textContent=`${signedInt(changes.since_start.absolute)} (${signedPct(changes.since_start.pct)})`;
  document.querySelector('#state-footer-label').textContent=`${p.state_name} U.S. nonresident enrollment profile`;
  renderTrend(document.querySelector('#profile-trend-chart'),p);
  fillTable(document.querySelector('#profile-institution-table'),p.top_institutions,[
    row=>row.institution,row=>row.control,row=>fmtInt.format(row.nonresident_enrollment),row=>`${row.nonresident_share_pct.toFixed(2)}%`
  ]);
  fillTable(document.querySelector('#profile-series-table'),p.series,[
    row=>String(row.year),row=>fmtInt.format(row.nonresident_enrollment),row=>`${row.nonresident_share_pct.toFixed(2)}%`,row=>fmtInt.format(row.undergraduate_nonresident),row=>fmtInt.format(row.graduate_nonresident)
  ]);
}

init().catch(error=>{
  console.error(error);
  document.querySelector('#state-profile-lede').textContent='Unable to load state profile data.';
});
